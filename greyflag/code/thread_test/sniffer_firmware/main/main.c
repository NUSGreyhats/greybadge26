/*
 * GreyFlag 802.15.4 sniffer  (queue-based, ISR-safe)
 *
 * Passively captures raw IEEE 802.15.4 frames on a fixed channel and dumps
 * them as hex over the USB-serial console. Intended for participants to
 * capture the broadcaster's encrypted Data frame and parse it by hand.
 *
 * Output format (one line per frame):
 *   RX CH<ch> RSSI:<dbm> LQI:<n> LEN:<n>: <hex...>
 *
 * The <hex> begins at the MAC Frame Control field (the PSDU length byte is
 * NOT included). That is exactly the byte stream described in the
 * broadcaster's frame-layout comment — parse it against the 802.15.4 MHR +
 * auxiliary security header to recover KeySource, KeyIndex, SrcEUI64,
 * FrameCounter, ciphertext and MIC.
 *
 * Why a queue: esp_ieee802154_receive_done() is invoked from the radio
 * driver context (effectively an ISR). Doing a long printf loop or re-arming
 * the receiver there can stall the driver, trip the task watchdog, and drop
 * frames. So the callback does the minimum — copy the frame into a queue —
 * and a normal-priority task does the printing.
 */

#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_ieee802154.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

/* docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/wireshark-user-guide.html */

#define FIXED_CHANNEL   25      /* Thread + broadcaster both use this */
#define MAX_PSDU        127     /* 802.15.4 max PHY payload */
#define RX_QUEUE_DEPTH  16      /* frames buffered between ISR and printer task */

/* One captured frame, copied out of the driver buffer in the callback. */
typedef struct {
    uint8_t len;                /* PSDU length (FC .. end, no length byte, no FCS) */
    int8_t  rssi;
    uint8_t lqi;
    uint8_t channel;
    uint8_t psdu[MAX_PSDU];     /* frame[1..len] — starts at Frame Control */
} sniff_frame_t;

static QueueHandle_t s_rx_queue;
static const char   *TAG = "sniffer";

/* ── radio callbacks ──────────────────────────────────────────────────────── */

/*
 * Driver/ISR context. Keep this SHORT. Copy the frame into the queue and
 * return — no printf, no blocking calls. The driver re-arms RX itself in
 * promiscuous continuous-receive, so we do not call esp_ieee802154_receive()
 * from here.
 */
void esp_ieee802154_receive_done(uint8_t *frame,
                                 esp_ieee802154_frame_info_t *info)
{
    BaseType_t hp_task_woken = pdFALSE;
    sniff_frame_t f;

    uint8_t len = frame[0];
    if (len == 0 || len > MAX_PSDU) {
        return;                 /* malformed length, drop */
    }

    f.len     = len;
    f.rssi    = info->rssi;
    f.lqi     = info->lqi;
    f.channel = info->channel;
    memcpy(f.psdu, &frame[1], len);   /* skip the length byte */

    /* Non-blocking ISR-safe enqueue. If the queue is full we drop the frame
       rather than stall the driver. */
    xQueueSendFromISR(s_rx_queue, &f, &hp_task_woken);
    portYIELD_FROM_ISR(hp_task_woken);
}

/* We only receive; these are required stubs. */
void esp_ieee802154_transmit_done(const uint8_t *frame,
                                  const uint8_t *ack,
                                  esp_ieee802154_frame_info_t *ack_info) {}

void esp_ieee802154_transmit_failed(const uint8_t *frame,
                                    esp_ieee802154_tx_error_t error) {}

/* ── printer task (normal context) ────────────────────────────────────────── */

static void printer_task(void *pv)
{
    sniff_frame_t f;

    while (1) {
        if (xQueueReceive(s_rx_queue, &f, portMAX_DELAY) != pdTRUE) {
            continue;
        }

        printf("RX CH%d RSSI:%d LQI:%d LEN:%d: ",
               f.channel, f.rssi, f.lqi, f.len);
        for (int i = 0; i < f.len; i++) {
            printf("%02x", f.psdu[i]);
        }
        printf("\n");

        esp_ieee802154_receive();   /* re-arm RX for the next frame */
    }
}


/* ── app_main ─────────────────────────────────────────────────────────────── */

void app_main(void)
{
    nvs_flash_init();

    s_rx_queue = xQueueCreate(RX_QUEUE_DEPTH, sizeof(sniff_frame_t));
    if (s_rx_queue == NULL) {
        ESP_LOGE(TAG, "failed to create rx queue");
        return;
    }

    printf("\n");
    printf("=== GreyFlag 802.15.4 sniffer ===\n");
    printf("listening on CH%d (promiscuous)\n", FIXED_CHANNEL);
    printf("hex starts at Frame Control\n");
    printf("=================================\n\n");

    esp_ieee802154_enable();
    esp_ieee802154_set_promiscuous(true);   /* pass all frames up, no addr/PAN/CRC filtering */
    esp_ieee802154_set_channel(FIXED_CHANNEL);

    /* Start the printer task BEFORE arming RX so no early frame is lost. */
    xTaskCreate(printer_task, "printer", 4096, NULL, 5, NULL);

    esp_ieee802154_receive();               /* arm continuous receive */

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}