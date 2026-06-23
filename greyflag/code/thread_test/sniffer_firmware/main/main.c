#include <stdio.h>
#include "nvs_flash.h"
#include "esp_ieee802154.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Scan all 16 channels (11-26) or stay on one.
// Set to 0 to stay fixed on FIXED_CHANNEL.
#define SCAN_ALL_CHANNELS   0
#define FIXED_CHANNEL       15      // Thread + broadcaster both use this

// ── callbacks ─────────────────────────────────────────────────────────────────

void esp_ieee802154_receive_done(uint8_t *frame,
                                  esp_ieee802154_frame_info_t *info)
{
    // frame[0]       = PSDU length (does NOT include FCS — hardware strips it)
    // frame[1..len]  = raw MAC frame bytes starting from Frame Control
    //
    // Output format:  RX CH<n> RSSI:<n> LEN:<n>: <hex>
    //
    // The hex string after the colon is what you pass to decrypt_flag.py.
    // To identify broadcaster frames: look for bytes "37 13" at offset 3-4
    // (that is PAN ID 0x1337 in little-endian).

    uint8_t len = frame[0];
    printf("RX CH%d RSSI:%d LEN:%d: ",
           info->channel, info->rssi, len);
    for (int i = 1; i <= len; i++) {
        printf("%02x", frame[i]);
    }
    printf("\n");

    // put radio back in receive mode after each frame
    esp_ieee802154_receive();
}

// required stubs — broadcaster sends, we only receive
void esp_ieee802154_transmit_done(const uint8_t *frame,
                                   const uint8_t *ack,
                                   esp_ieee802154_frame_info_t *ack_info) {}

void esp_ieee802154_transmit_failed(const uint8_t *frame,
                                     esp_ieee802154_tx_error_t error) {}

// ── channel scanning task (only used when SCAN_ALL_CHANNELS=1) ────────────────

#if SCAN_ALL_CHANNELS
static void channel_scan_task(void *pv)
{
    int ch = 11;
    while (1) {
        esp_ieee802154_set_channel(ch);
        esp_ieee802154_receive();
        vTaskDelay(pdMS_TO_TICKS(500)); // 500 ms per channel
        if (++ch > 26) ch = 11;
    }
}
#endif

void app_main(void)
{
    nvs_flash_init();

    printf("\n");
    printf("=== GreyFlag 802.15.4 sniffer ===\n");
#if SCAN_ALL_CHANNELS
    printf("scanning CH11-CH26, 500ms per channel\n");
#else
    printf("listening on CH%d\n", FIXED_CHANNEL);
#endif
    printf("broadcaster frames: PAN ID bytes 37 13 at frame offset 3-4\n");
    printf("=================================\n\n");

    esp_ieee802154_enable();
    esp_ieee802154_set_promiscuous(true);   // disable PAN ID filtering
    esp_ieee802154_set_panid(0xFFFF);       // accept all PANs

#if SCAN_ALL_CHANNELS
    esp_ieee802154_set_channel(11);
    xTaskCreate(channel_scan_task, "scanner", 2048, NULL, 5, NULL);
#else
    esp_ieee802154_set_channel(FIXED_CHANNEL);
    esp_ieee802154_receive();
#endif

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
