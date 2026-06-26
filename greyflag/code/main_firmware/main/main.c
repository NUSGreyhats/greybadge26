#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <unistd.h>
#include <fcntl.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_vfs_eventfd.h"
#include "esp_vfs_dev.h"

/* OpenThread */
#include "esp_openthread.h"
#include "esp_openthread_lock.h"
#include "esp_openthread_netif_glue.h"
#include "esp_openthread_types.h"
#include "esp_ot_config.h"
#include "openthread/dataset.h"
#include "openthread/instance.h"
#include "openthread/thread.h"
#include "openthread/cli.h"

/* Badge modules */
#include "led_modes.h"
#include "challenges.h"
#include "speaker.h"

/* ── Hardware ───────────────────────────────────────────────── */
#define BUTTON_PIN      9
#define DEBOUNCE_MS     20
#define LONG_PRESS_MS   800

/* ── State machine ──────────────────────────────────────────── */
typedef enum {
    STATE_MENU,
    STATE_CHALLENGES,
    STATE_SPEAKER,
    STATE_CH1,
    STATE_CH2,
    STATE_CH3,
    STATE_CH4,
} AppState;

static volatile AppState currentState = STATE_MENU;

/* ── Button ISR ─────────────────────────────────────────────── */
static volatile int64_t btn_press_time   = 0;
static volatile bool    btn_pending      = false;
static volatile int64_t btn_duration_ms  = 0;

static void IRAM_ATTR btn_isr(void *arg)
{
    int level = gpio_get_level(BUTTON_PIN);
    int64_t now = esp_timer_get_time() / 1000;
    if (level == 0) {
        /* falling edge: button pressed */
        btn_press_time = now;
    } else {
        /* rising edge: button released */
        int64_t dur = now - btn_press_time;
        if (dur > DEBOUNCE_MS) {
            btn_duration_ms = dur;
            btn_pending     = true;
        }
    }
}

/* ── OpenThread ─────────────────────────────────────────────── */
/*
 * The CLI is driven manually: input typed while in the Thread challenge
 * is forwarded to otCliInputLine(). There is NO auto-join — discovering
 * the commands (ot ifconfig up / ot joiner start GREYFLAG99 / ot thread
 * start / ot dataset active) is part of the challenge.
 *
 * The flag itself is NOT delivered here. Participants obtain the encrypted
 * flag by sniffing the organiser's broadcaster and decrypting it with the
 * provided decrypt.py. The only reward shown here is a "welcome" message
 * once the badge successfully attaches to the GreyFlag network.
 */
static bool ot_welcomed = false;

/* CLI output callback — writes OT CLI output to the USB console. */
static int ot_cli_output_cb(void *ctx, const char *fmt, va_list ap)
{
    (void)ctx;
    int n = vprintf(fmt, ap);
    fflush(stdout);
    return n;
}

static void ot_state_changed(otChangedFlags flags, void *ctx)
{
    otInstance *inst = (otInstance *)ctx;
    if (flags & OT_CHANGED_THREAD_ROLE) {
        otDeviceRole role = otThreadGetDeviceRole(inst);
        if (!ot_welcomed &&
            (role == OT_DEVICE_ROLE_CHILD || role == OT_DEVICE_ROLE_ROUTER)) {
            ot_welcomed = true;
            printf("\r\nWelcome to the GreyFlag network\r\n\r\n");
            fflush(stdout);
        }
    }
}

/* ── Menu printers ──────────────────────────────────────────── */

static void print_main_menu(void)
{
    printf("\n==========================\n");
    printf("      GREYFLAG BADGE      \n");
    printf("==========================\n");
    printf("[1] Challenges\n");
    printf("[2] Speaker Samples\n");
    printf("[3] LED Modes (button cycles)\n");
    printf("Enter choice: ");
    fflush(stdout);
}

static void print_challenge_menu(void)
{
    printf("\n==========================\n");
    printf("       CHALLENGES         \n");
    printf("==========================\n");
    printf("[1] Welcome to GreyFlag\n");
    printf("[2] Music to My Ear\n");
    printf("[3] Hidden in Plain Sight\n");
    printf("[4] What's this Thread Connecting Us?\n");
    printf("[0] Back to Main Menu\n");
    printf("Enter choice: ");
    fflush(stdout);
}

/* ── Input handling ─────────────────────────────────────────── */

static void goto_menu(void)
{
    currentState = STATE_MENU;
    print_main_menu();
}

/* ── Thread challenge CLI line buffer (CH4) ─────────────────── */
#define CLI_LINE_MAX 128
static char cli_line[CLI_LINE_MAX];
static int  cli_len = 0;

static void ch4_reset_line(void)
{
    cli_len = 0;
}

/* Feed one typed character to the OpenThread CLI while in CH4.
 * Returns true if the user requested to leave the challenge. */
static bool ch4_feed_char(char c)
{
    if (c == '\r' || c == '\n') {
        printf("\r\n");
        cli_line[cli_len] = '\0';

        /* skip leading whitespace */
        char *cmd = cli_line;
        while (*cmd == ' ' || *cmd == '\t') cmd++;

        /* local commands to leave the CLI */
        if (strcmp(cmd, "exit") == 0 || strcmp(cmd, "menu") == 0) {
            ch4_reset_line();
            return true;
        }

        /* Be forgiving: the OpenThread CLI expects bare commands (e.g.
         * "ifconfig up"), but participants often type an "ot" prefix out of
         * habit — strip it so both forms work. */
        if (strncmp(cmd, "ot ", 3) == 0)      cmd += 3;
        else if (strcmp(cmd, "ot") == 0)      cmd += 2;
        while (*cmd == ' ' || *cmd == '\t') cmd++;

        if (*cmd) {
            /* The CLI prints its own "> " prompt after running the command. */
            esp_openthread_lock_acquire(portMAX_DELAY);
            otCliInputLine(cmd);
            esp_openthread_lock_release();
        } else {
            /* Empty line: the CLI won't run, so print a fresh prompt ourselves. */
            printf("> ");
            fflush(stdout);
        }
        ch4_reset_line();
        return false;
    }

    /* backspace / delete */
    if (c == 0x7f || c == 0x08) {
        if (cli_len > 0) {
            cli_len--;
            printf("\b \b");
            fflush(stdout);
        }
        return false;
    }

    if (cli_len < CLI_LINE_MAX - 1) {
        cli_line[cli_len++] = c;
        putchar(c);          /* echo */
        fflush(stdout);
    }
    return false;
}

static void handle_main_menu(char c)
{
    switch (c) {
        case '1':
            currentState = STATE_CHALLENGES;
            print_challenge_menu();
            break;
        case '2':
            currentState = STATE_SPEAKER;
            setupSpeaker();
            break;
        case '3':
            printf("Short press the boot button (U7) to cycle LED modes.\n");
            print_main_menu();
            break;
        default:
            printf("Invalid. Try again: ");
            fflush(stdout);
            break;
    }
}

static void handle_challenge_menu(char c)
{
    switch (c) {
        case '1':
            currentState = STATE_CH1;
            setupCH1();
            break;
        case '2':
            currentState = STATE_CH2;
            setupCH2();
            break;
        case '3':
            currentState = STATE_CH3;
            setupCH3();
            /* CH3 is display-only; stay here until '0' */
            break;
        case '4':
            currentState = STATE_CH4;
            setupCH4();
            break;
        case '0':
            currentState = STATE_MENU;
            print_main_menu();
            break;
        default:
            printf("Invalid. Try again: ");
            fflush(stdout);
            break;
    }
}

/* ── app_main ───────────────────────────────────────────────── */

void app_main(void)
{
    /* Core init */
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_netif_init());

    esp_vfs_eventfd_config_t efd_cfg = { .max_fds = 3 };
    ESP_ERROR_CHECK(esp_vfs_eventfd_register(&efd_cfg));

    /* Button */
    gpio_config_t btn_cfg = {
        .pin_bit_mask = 1ULL << BUTTON_PIN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_ANYEDGE,
    };
    gpio_config(&btn_cfg);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(BUTTON_PIN, btn_isr, NULL);

    /* LEDs */
    setupLEDModes();

    /* USB Serial/JTAG console.
     * Install the USB-Serial-JTAG driver and route stdio through it so the USB
     * OUT endpoint is actually serviced (otherwise host writes time out and no
     * input ever reaches the app). Then unbuffer stdio and make stdin
     * non-blocking so fgetc() returns EOF when no key is waiting — this keeps
     * the main loop spinning so LED animations, CH2 sampling, and (critically)
     * the long-press button check stay live. */
    usb_serial_jtag_driver_config_t usj_cfg = USB_SERIAL_JTAG_DRIVER_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usj_cfg));
    usb_serial_jtag_vfs_use_driver();

    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    fcntl(fileno(stdin), F_SETFL, O_NONBLOCK);

    /* OpenThread */
    static esp_openthread_config_t ot_cfg = {
        .netif_config    = ESP_NETIF_DEFAULT_OPENTHREAD(),
        .platform_config = {
            .radio_config = ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG(),
            .host_config  = ESP_OPENTHREAD_DEFAULT_HOST_CONFIG(),
            .port_config  = ESP_OPENTHREAD_DEFAULT_PORT_CONFIG(),
        },
    };
    ESP_ERROR_CHECK(esp_openthread_start(&ot_cfg));

    /* Initialise the OT CLI (driven manually from CH4 via otCliInputLine)
     * and register the role-change callback for the welcome message.
     * No auto-join: the participant types the commands themselves. */
    esp_openthread_lock_acquire(portMAX_DELAY);
    otInstance *ot_inst = esp_openthread_get_instance();
    otCliInit(ot_inst, ot_cli_output_cb, NULL);
    otSetStateChangedCallback(ot_inst, ot_state_changed, ot_inst);
    esp_openthread_lock_release();

    /* Welcome */
    vTaskDelay(pdMS_TO_TICKS(200)); /* let UART settle */
    print_main_menu();

    /* ── Main loop ─────────────────────────────────────────── */
    while (1) {
        /* Run LED animation */
        runLEDModes();

        /* Process button */
        if (btn_pending) {
            btn_pending = false;
            int64_t dur = btn_duration_ms;
            if (dur >= LONG_PRESS_MS) {
                /* Long press → return to main menu */
                goto_menu();
            } else {
                /* Short press → next LED mode */
                nextLEDMode();
            }
        }

        /* Non-blocking serial read */
        int ch = fgetc(stdin);
        if (ch == EOF) {
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }
        char c = (char)ch;

        switch (currentState) {
            case STATE_MENU:
                if (c != '\n' && c != '\r')
                    handle_main_menu(c);
                break;

            case STATE_CHALLENGES:
                if (c != '\n' && c != '\r')
                    handle_challenge_menu(c);
                break;

            case STATE_SPEAKER:
                if (runSpeaker(c))
                    goto_menu();
                break;

            case STATE_CH1:
                if (c == '0') {
                    goto_menu();
                } else {
                    runCH1(c);
                }
                break;

            case STATE_CH2:
                /* display-only; '0' goes back */
                if (c == '0') goto_menu();
                break;

            case STATE_CH3:
                /* display-only; '0' goes back */
                if (c == '0') goto_menu();
                break;

            case STATE_CH4:
                /* Forward typed input to the OpenThread CLI. Type "exit"
                 * or "menu" (or long-press the button) to leave. */
                if (ch4_feed_char(c))
                    goto_menu();
                break;
        }

        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
