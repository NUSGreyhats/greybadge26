#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_ieee802154.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "mbedtls/ccm.h"

static const char *TAG = "broadcaster";

// ── must match organiser_commissioner exactly ─────────────────────────────────
static const uint8_t NETWORK_KEY[16] = {
    0xAA, 0xAD, 0xBE, 0xEB, 0xCA, 0xAC, 0xBA, 0xDD,
    0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF
};
// ─────────────────────────────────────────────────────────────────────────────

static const char *FLAG = "flag{Thread_N3tw0rk_Key_0wns_All}";

#define CHANNEL             15
#define BROADCAST_PAN_ID    0x1337
#define BROADCAST_INTERVAL  10000       // ms between transmissions
#define MIC_LEN             4           // ENC-MIC-32
#define SEC_LEVEL           0x05        // 802.15.4 security level: ENC-MIC-32
                                        // Key ID Mode 0 (implicit) → no key ID field
#define NVS_NS              "broadcaster"
#define NVS_KEY_CTR         "frame_ctr"

static uint32_t           g_frame_ctr = 0;
static uint8_t            g_eui64[8];          // our source extended address
static uint8_t            s_tx_buf[150];        // static: must outlive transmit_done
static SemaphoreHandle_t  s_tx_done;

// ── frame counter persistence ─────────────────────────────────────────────────
static void load_frame_ctr(void)
{
    nvs_handle_t h;
    if (nvs_open(NVS_NS, NVS_READONLY, &h) == ESP_OK) {
        nvs_get_u32(h, NVS_KEY_CTR, &g_frame_ctr);
        nvs_close(h);
    }
    // jump forward by 100 in case we crashed between saves
    g_frame_ctr += 100;
    ESP_LOGI(TAG, "frame counter loaded: %lu", (unsigned long)g_frame_ctr);

    // persist the new starting value immediately
    nvs_handle_t hw;
    if (nvs_open(NVS_NS, NVS_READWRITE, &hw) == ESP_OK) {
        nvs_set_u32(hw, NVS_KEY_CTR, g_frame_ctr);
        nvs_commit(hw);
        nvs_close(hw);
    }
}

static void save_frame_ctr(void)
{
    nvs_handle_t h;
    if (nvs_open(NVS_NS, NVS_READWRITE, &h) == ESP_OK) {
        nvs_set_u32(h, NVS_KEY_CTR, g_frame_ctr);
        nvs_commit(h);
        nvs_close(h);
    }
}

// ── 802.15.4 callbacks ────────────────────────────────────────────────────────
void esp_ieee802154_transmit_done(const uint8_t *frame,
                                   const uint8_t *ack,
                                   esp_ieee802154_frame_info_t *ack_info)
{
    xSemaphoreGive(s_tx_done);
    esp_ieee802154_receive();   // return to RX state
}

void esp_ieee802154_transmit_failed(const uint8_t *frame,
                                     esp_ieee802154_tx_error_t error)
{
    ESP_LOGW(TAG, "TX failed: %d", error);
    xSemaphoreGive(s_tx_done);
    esp_ieee802154_receive();
}

void esp_ieee802154_receive_done(uint8_t *frame,
                                  esp_ieee802154_frame_info_t *frame_info)
{
    // broadcaster ignores received frames
}

// ── frame construction and transmission ───────────────────────────────────────
// Frame layout (Key ID Mode 0, no key identifier field):
//
//  [FC 2B][Seq 1B][DstPAN 2B][DstAddr 2B][SrcEUI64 8B]   ← MAC header
//  [SecCtrl 1B][FrameCtr 4B]                               ← Aux Sec Header
//  [Ciphertext NB][MIC 4B]                                 ← secured payload
//
// Security Control byte = 0x05:
//   bits[2:0] = 101  (Security Level 5 = ENC-MIC-32)
//   bits[4:3] = 00   (Key ID Mode 0 = implicit, no key field)
//   bits[7:5] = 000  (reserved)
//
// AAD = everything from FC through end of Aux Sec Header (20 bytes)
// Nonce = SrcEUI64(8B) || FrameCtr(4B,LE) || SecLevel(1B)  = 13 bytes
//
static void transmit_flag_frame(void)
{
    size_t flag_len = strlen(FLAG);

    // ── frame counter as 4 little-endian bytes ───────────────────────────────
    uint8_t ctr_le[4] = {
        (uint8_t)(g_frame_ctr & 0xFF),
        (uint8_t)((g_frame_ctr >>  8) & 0xFF),
        (uint8_t)((g_frame_ctr >> 16) & 0xFF),
        (uint8_t)((g_frame_ctr >> 24) & 0xFF),
    };

    // ── frame control bytes ──────────────────────────────────────────────────
    // Type=Data(001), Security=1, Pending=0, ACK=0, PAN compress=1,
    // Reserved=0, DstMode=short(10), Version=2006(01), SrcMode=extended(11)
    uint8_t fc[2] = { 0x49, 0xD8 };

    // ── sequence number (low byte of counter, gives 0-255 rotation) ──────────
    uint8_t seq = (uint8_t)(g_frame_ctr & 0xFF);

    // ── destination: broadcast on PAN 0x1337 ─────────────────────────────────
    uint8_t dst_pan[2] = {
        (uint8_t)(BROADCAST_PAN_ID & 0xFF),
        (uint8_t)(BROADCAST_PAN_ID >> 8),
    };
    uint8_t dst_addr[2] = { 0xFF, 0xFF };

    // ── AAD: MAC header + Aux Security Header (20 bytes total) ───────────────
    // Participants must feed this exact byte sequence into cipher.update()
    uint8_t aad[20];
    int ai = 0;
    memcpy(&aad[ai], fc,       2); ai += 2;
    aad[ai++] = seq;
    memcpy(&aad[ai], dst_pan,  2); ai += 2;
    memcpy(&aad[ai], dst_addr, 2); ai += 2;
    memcpy(&aad[ai], g_eui64,  8); ai += 8;
    aad[ai++] = SEC_LEVEL;              // Security Control byte
    memcpy(&aad[ai], ctr_le,   4); ai += 4;
    // ai == 20

    // ── nonce: SrcEUI64 || FrameCtr(LE) || SecLevel ──────────────────────────
    // Bytes come directly from the frame in the order they appear on the wire.
    // Participants read these from the sniffed frame without any byte-swapping.
    uint8_t nonce[13];
    memcpy(nonce,     g_eui64, 8);
    memcpy(nonce + 8, ctr_le,  4);
    nonce[12] = SEC_LEVEL;

    // ── AES-128-CCM* encryption ───────────────────────────────────────────────
    // We use the raw Network Key directly (not the Thread-derived MAC Key).
    // This is a deliberate design choice for the CTF — participants who try
    // the Thread key derivation path will get a different key and fail.
    uint8_t ciphertext[128];
    uint8_t mic[MIC_LEN];

    mbedtls_ccm_context ccm;
    mbedtls_ccm_init(&ccm);
    mbedtls_ccm_setkey(&ccm, MBEDTLS_CIPHER_ID_AES, NETWORK_KEY, 128);
    int ret = mbedtls_ccm_encrypt_and_tag(
        &ccm,
        flag_len,
        nonce, sizeof(nonce),
        aad,   sizeof(aad),
        (const uint8_t *)FLAG,
        ciphertext,
        mic, MIC_LEN
    );
    mbedtls_ccm_free(&ccm);

    if (ret != 0) {
        ESP_LOGE(TAG, "CCM encrypt failed: %d", ret);
        return;
    }

    // ── assemble final frame into static buffer ───────────────────────────────
    // frame[0] = PSDU length (everything that follows, FCS added by hardware)
    int fi = 1;
    memcpy(&s_tx_buf[fi], fc,         2);        fi += 2;
    s_tx_buf[fi++] = seq;
    memcpy(&s_tx_buf[fi], dst_pan,    2);        fi += 2;
    memcpy(&s_tx_buf[fi], dst_addr,   2);        fi += 2;
    memcpy(&s_tx_buf[fi], g_eui64,    8);        fi += 8;
    s_tx_buf[fi++] = SEC_LEVEL;                  // Security Control
    memcpy(&s_tx_buf[fi], ctr_le,     4);        fi += 4;
    memcpy(&s_tx_buf[fi], ciphertext, flag_len); fi += flag_len;
    memcpy(&s_tx_buf[fi], mic,        MIC_LEN);  fi += MIC_LEN;

    s_tx_buf[0] = (uint8_t)(fi - 1); // PSDU length excludes the length byte

    ESP_LOGI(TAG, "TX frame_ctr=%lu psdu_len=%d", (unsigned long)g_frame_ctr, s_tx_buf[0]);

    xSemaphoreTake(s_tx_done, 0);            // clear any stale signal
    esp_ieee802154_transmit(s_tx_buf, false); // false = no CCA

    // wait for hardware to finish (1 second timeout is generous for one frame)
    xSemaphoreTake(s_tx_done, pdMS_TO_TICKS(1000));

    g_frame_ctr++;
    save_frame_ctr();
}

static void broadcaster_task(void *pv)
{
    while (1) {
        transmit_flag_frame();
        vTaskDelay(pdMS_TO_TICKS(BROADCAST_INTERVAL));
    }
}

void app_main(void)
{
    nvs_flash_init();
    load_frame_ctr();

    s_tx_done = xSemaphoreCreateBinary();

    esp_ieee802154_enable();

    // get our hardware EUI-64 (bytes in frame-wire order: LSB first)
    esp_ieee802154_get_extended_address(g_eui64);

    ESP_LOGI(TAG, "EUI-64 (frame/nonce byte order): "
             "%02x %02x %02x %02x %02x %02x %02x %02x",
             g_eui64[0], g_eui64[1], g_eui64[2], g_eui64[3],
             g_eui64[4], g_eui64[5], g_eui64[6], g_eui64[7]);
    ESP_LOGI(TAG, "(participants read these bytes directly from the sniffed frame)");

    esp_ieee802154_set_channel(CHANNEL);
    esp_ieee802154_set_panid(BROADCAST_PAN_ID);
    esp_ieee802154_set_extended_address(g_eui64);
    esp_ieee802154_set_promiscuous(false);
    esp_ieee802154_receive();

    ESP_LOGI(TAG, "broadcasting on CH%d PAN 0x%04X every %ds",
             CHANNEL, BROADCAST_PAN_ID, BROADCAST_INTERVAL / 1000);

    xTaskCreate(broadcaster_task, "broadcaster", 8192, NULL, 5, NULL);
}
