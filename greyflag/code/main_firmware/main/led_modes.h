#pragma once
#include "driver/ledc.h"
#include "esp_timer.h"

/* 5 discrete LEDs: GPIO -> LED -> GND.
 * All modes are driven through LEDC PWM (configured once at init and never torn
 * down). "On"/"off" are just duty = LED_ON_DUTY / 0, and breathing ramps the
 * duty. Using a single driver for every mode avoids the GPIO-vs-LEDC routing
 * conflict that caused "GPIO not usable" warnings when switching modes. */
#define LED_COUNT     5
#define LED_ON_DUTY   64   /* cap brightness (~25% of 255) to limit current */
static const int LED_PINS[LED_COUNT] = {22, 23, 15, 2, 3};

static uint8_t  ledMode        = 0;
static int      ledStep        = 0;
static int64_t  lastLedUpdate  = 0;

/* breathing state */
static int  breatheVal = 0;
static int  breatheDir = 1;

/* binary counter state */
static int  counterVal = 0;
static bool counterUp  = true;

/* pile state */
static int  pileCount = 0;
static bool pilePause = false;

/* ── LEDC helpers ───────────────────────────────────────────── */

/* Set one LED to an 8-bit brightness (0 = off). */
static void led_set(int idx, int duty)
{
    if (duty < 0)   duty = 0;
    if (duty > 255) duty = 255;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)idx, (uint32_t)duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)idx);
}

static void led_on(int idx)  { led_set(idx, LED_ON_DUTY); }
static void led_off(int idx) { led_set(idx, 0); }

static void all_leds_off(void)
{
    for (int i = 0; i < LED_COUNT; i++) led_off(i);
}

/* ── Public API ─────────────────────────────────────────────── */

void setupLEDModes(void)
{
    ledc_timer_config_t tmr = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT,
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = 5000,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ledc_timer_config(&tmr);
    for (int i = 0; i < LED_COUNT; i++) {
        ledc_channel_config_t ch = {
            .gpio_num   = LED_PINS[i],
            .speed_mode = LEDC_LOW_SPEED_MODE,
            .channel    = (ledc_channel_t)i,
            .timer_sel  = LEDC_TIMER_0,
            .duty       = 0,
            .hpoint     = 0,
        };
        ledc_channel_config(&ch);
    }
    all_leds_off();
}

void nextLEDMode(void)
{
    all_leds_off();
    ledMode    = (ledMode + 1) % 4;
    ledStep    = 0;
    pileCount  = 0;
    pilePause  = false;
    breatheVal = 0;
    breatheDir = 1;
    counterVal = 0;
    counterUp  = true;
    lastLedUpdate = 0;
}

void runLEDModes(void)
{
    int64_t now = esp_timer_get_time() / 1000; /* ms */

    /* Mode 0 — chase: one LED sweeps left→right */
    if (ledMode == 0) {
        if (now - lastLedUpdate < 80) return;
        lastLedUpdate = now;
        all_leds_off();
        led_on(ledStep % LED_COUNT);
        ledStep++;
        return;
    }

    /* Mode 1 — pile-up: light 1→2→3→4→5, pause, clear */
    if (ledMode == 1) {
        if (now - lastLedUpdate < (pilePause ? 600 : 200)) return;
        lastLedUpdate = now;
        if (pilePause) {
            pilePause = false;
            pileCount = 0;
            all_leds_off();
        } else {
            pileCount++;
            if (pileCount > LED_COUNT) {
                pilePause = true;
            } else {
                led_on(pileCount - 1);
            }
        }
        return;
    }

    /* Mode 2 — synchronized breathing */
    if (ledMode == 2) {
        if (now - lastLedUpdate < 15) return;
        lastLedUpdate = now;
        breatheVal += breatheDir * 3;
        if (breatheVal >= LED_ON_DUTY) { breatheVal = LED_ON_DUTY; breatheDir = -1; }
        if (breatheVal <= 0)           { breatheVal = 0;           breatheDir =  1; }
        for (int i = 0; i < LED_COUNT; i++) led_set(i, breatheVal);
        return;
    }

    /* Mode 3 — 5-bit binary counter 0→31→0 */
    if (now - lastLedUpdate < 333) return;
    lastLedUpdate = now;
    for (int bit = 0; bit < LED_COUNT; bit++)
        led_set(bit, (counterVal >> bit) & 1 ? LED_ON_DUTY : 0);
    if (counterUp) { counterVal++; if (counterVal >= 31) counterUp = false; }
    else           { counterVal--; if (counterVal <= 0)  counterUp = true;  }
}
