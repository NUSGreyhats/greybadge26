/*
 * ot_organiser_broadcaster — second organiser
 *
 * Transmits an AES-CCM-encrypted 802.15.4 Data frame on CH25 / PAN 0x1337
 * every BROADCAST_INTERVAL_MS milliseconds.
 *
 * Frame layout (wire order):
 *   [FC:2][Seq:1][DstPAN:2][DstAddr:2][SrcEUI64:8]          <- MHR
 *   [SecCtrl:1][FrameCounter:4][KeySource:4][KeyIndex:1]     <- Aux Security Header
 *   [Ciphertext:N][MIC:4]                                    <- payload + tag
 *
 * Security Control = 0x15:
 *   bits [2:0] = 101  Security Level 5 (ENC-MIC-32)
 *   bits [4:3] = 10   Key ID Mode 2 (4-octet KeySource + 1-octet KeyIndex)
 *
 * Thread key derivation (Thread spec §4.3):
 *   KeyMaterial = HMAC-SHA256(NetworkKey, KeySource(4B BE) || 0x00 || "Thread")
 *   MAC Key     = KeyMaterial[0:16]
 *   KeyIndex    = (KeySequence & 0x7F) + 1
 *
 * Nonce (13B): SrcEUI64(8) || FrameCounter(4 LE) || SecLevel(1 = 0x05)
 * AAD   (25B): all bytes from FC through KeyIndex inclusive
 */

#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_ieee802154.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "psa/crypto.h"

/* ── CTF configuration ────────────────────────────────────────────────── */

#define BROADCASTER_CHANNEL     25
#define BROADCASTER_PAN_ID      0x1337
#define BROADCAST_INTERVAL_MS   5000

/* Fixed for the entire CTF — broadcaster has no Thread stack, nothing rotates it */
#define KEY_SEQUENCE  0u
#define KEY_INDEX     ((uint8_t)((KEY_SEQUENCE & 0x7Fu) + 1u))   /* = 1 */

static const uint8_t NETWORK_KEY[16] = {
    0xAA, 0xAD, 0xBE, 0xEB, 0xCA, 0xAC, 0xBA, 0xDD,
    0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF
};

static const char FLAG[] = "grey{B0und_By_Akai_Ito}";

/* ── globals ──────────────────────────────────────────────────────────── */

static const char *TAG = "broadcaster";

static uint8_t           s_eui64[8];
static uint8_t           s_mac_key[16];
static uint32_t          s_frame_counter = 0;
static SemaphoreHandle_t s_tx_done_sem;

/* PSDU length byte + MHR (13B) + Aux Sec Header (10B) + payload + MIC (4B)
   MHR  = FC(2) + Seq(1) + DstPAN(2) + DstAddr(2) + SrcEUI64(8) = 15
   AuxSH= SecCtrl(1) + FrameCounter(4) + KeySource(4) + KeyIndex(1) = 10  */
static uint8_t s_frame_buf[1 + 15 + 10 + sizeof(FLAG) + 4 + 2];  /* +2 for FCS */

/* ── Thread key derivation ────────────────────────────────────────────── */

//https://github.com/openthread/openthread/blob/main/src/core/thread/key_manager.cpp
static void derive_mac_key(void)
{
    /* HMAC-SHA256(NetworkKey, KeySequence(4B BE) || "Thread") */
    uint8_t input[10];
    input[0] = (uint8_t)(KEY_SEQUENCE >> 24);
    input[1] = (uint8_t)(KEY_SEQUENCE >> 16);
    input[2] = (uint8_t)(KEY_SEQUENCE >>  8);
    input[3] = (uint8_t)(KEY_SEQUENCE);
    memcpy(input + 4, "Thread", 6);

    psa_key_attributes_t attrs = PSA_KEY_ATTRIBUTES_INIT;
    psa_set_key_usage_flags(&attrs, PSA_KEY_USAGE_SIGN_MESSAGE);
    psa_set_key_algorithm(&attrs, PSA_ALG_HMAC(PSA_ALG_SHA_256));
    psa_set_key_type(&attrs, PSA_KEY_TYPE_HMAC);
    psa_set_key_bits(&attrs, sizeof(NETWORK_KEY) * 8);
    psa_key_id_t key;
    psa_import_key(&attrs, NETWORK_KEY, sizeof(NETWORK_KEY), &key);

    uint8_t km[32];
    size_t  km_len;
    psa_mac_compute(key, PSA_ALG_HMAC(PSA_ALG_SHA_256),
                    input, sizeof(input),
                    km, sizeof(km), &km_len);
    psa_destroy_key(key);

    memcpy(s_mac_key, km + 16, 16);
}

/* ── 802.15.4 callbacks ───────────────────────────────────────────────── */

void esp_ieee802154_receive_done(uint8_t *frame,
                                  esp_ieee802154_frame_info_t *info) {}

void esp_ieee802154_transmit_done(const uint8_t *frame,
                                   const uint8_t *ack,
                                   esp_ieee802154_frame_info_t *ack_info)
{
    xSemaphoreGiveFromISR(s_tx_done_sem, NULL);
}

void esp_ieee802154_transmit_failed(const uint8_t *frame,
                                     esp_ieee802154_tx_error_t error)
{
    ESP_LOGE(TAG, "tx failed: %d", (int)error);
    xSemaphoreGiveFromISR(s_tx_done_sem, NULL);
}

/* ── frame builder ────────────────────────────────────────────────────── */

/*
 * Frame Control = 0xC849:
 *   bits [2:0]  = 001  Data
 *   bit  3      = 1    Security Enabled
 *   bit  4      = 0    Frame Pending
 *   bit  5      = 0    Ack Request
 *   bit  6      = 1    PAN ID Compression
 *   bits [11:10]= 10   Dst Addr Mode: short
 *   bits [13:12]= 00   Frame Version 0
 *   bits [15:14]= 11   Src Addr Mode: extended
 */
#define FRAME_CONTROL  0xC849u
#define SEC_CTRL       0x15u   /* SecLevel=5, KeyIDMode=2 */

static void build_and_transmit(void)
{
    uint8_t seq = (uint8_t)(s_frame_counter & 0xFF);

    /* KeySource = KEY_SEQUENCE as 4 bytes big-endian */
    const uint8_t key_source[4] = {
        (uint8_t)(KEY_SEQUENCE >> 24),
        (uint8_t)(KEY_SEQUENCE >> 16),
        (uint8_t)(KEY_SEQUENCE >>  8),
        (uint8_t)(KEY_SEQUENCE),
    };

    /* ── AAD: FC through KeyIndex inclusive (25 bytes) ──────────────── */
    uint8_t aad[25];
    int a = 0;
    aad[a++] = (uint8_t)(FRAME_CONTROL & 0xFF);
    aad[a++] = (uint8_t)(FRAME_CONTROL >> 8);
    aad[a++] = seq;
    aad[a++] = (uint8_t)(BROADCASTER_PAN_ID & 0xFF);
    aad[a++] = (uint8_t)(BROADCASTER_PAN_ID >> 8);
    aad[a++] = 0xFF;                              /* dst addr lo (broadcast) */
    aad[a++] = 0xFF;                              /* dst addr hi */
    memcpy(aad + a, s_eui64, 8); a += 8;         /* SrcEUI64 */
    aad[a++] = SEC_CTRL;
    aad[a++] = (uint8_t)(s_frame_counter);
    aad[a++] = (uint8_t)(s_frame_counter >>  8);
    aad[a++] = (uint8_t)(s_frame_counter >> 16);
    aad[a++] = (uint8_t)(s_frame_counter >> 24);
    memcpy(aad + a, key_source, 4); a += 4;      /* KeySource */
    aad[a++] = KEY_INDEX;                         /* KeyIndex */
    /* a == 25 */

    /* ── Nonce: SrcEUI64(8) || FrameCounter(4 LE) || SecLevel(1) ────── */
    uint8_t nonce[13];
    memcpy(nonce, s_eui64, 8);
    nonce[8]  = (uint8_t)(s_frame_counter);
    nonce[9]  = (uint8_t)(s_frame_counter >>  8);
    nonce[10] = (uint8_t)(s_frame_counter >> 16);
    nonce[11] = (uint8_t)(s_frame_counter >> 24);
    nonce[12] = 0x05;

    /* ── AES-128-CCM encrypt with derived MAC Key ───────────────────── */
    size_t  flag_len = strlen(FLAG);
    uint8_t ciphertext[sizeof(FLAG)];
    uint8_t mic[4];

    psa_key_attributes_t ccm_attrs = PSA_KEY_ATTRIBUTES_INIT;
    psa_set_key_usage_flags(&ccm_attrs, PSA_KEY_USAGE_ENCRYPT);
    psa_set_key_algorithm(&ccm_attrs, PSA_ALG_AEAD_WITH_SHORTENED_TAG(PSA_ALG_CCM, 4));
    psa_set_key_type(&ccm_attrs, PSA_KEY_TYPE_AES);
    psa_set_key_bits(&ccm_attrs, 128);
    psa_key_id_t ccm_key;
    psa_import_key(&ccm_attrs, s_mac_key, 16, &ccm_key);

    /* PSA outputs ciphertext||tag contiguously */
    uint8_t enc_out[sizeof(FLAG) + 4];
    size_t  enc_out_len;
    psa_status_t psa_ret = psa_aead_encrypt(
        ccm_key, PSA_ALG_AEAD_WITH_SHORTENED_TAG(PSA_ALG_CCM, 4),
        nonce, sizeof(nonce),
        aad,   sizeof(aad),
        (const uint8_t *)FLAG, flag_len,
        enc_out, sizeof(enc_out), &enc_out_len);
    psa_destroy_key(ccm_key);

    if (psa_ret != PSA_SUCCESS) {
        ESP_LOGE(TAG, "AES-CCM failed: %d", (int)psa_ret);
        return;
    }

    memcpy(ciphertext, enc_out, flag_len);
    memcpy(mic, enc_out + flag_len, 4);

    /* ── Assemble PSDU in s_frame_buf ───────────────────────────────── */
    /* s_frame_buf[0] = PSDU length (filled last); s_frame_buf[1..] = frame bytes */
    int f = 1;
    s_frame_buf[f++] = (uint8_t)(FRAME_CONTROL & 0xFF);
    s_frame_buf[f++] = (uint8_t)(FRAME_CONTROL >> 8);
    s_frame_buf[f++] = seq;
    s_frame_buf[f++] = (uint8_t)(BROADCASTER_PAN_ID & 0xFF);
    s_frame_buf[f++] = (uint8_t)(BROADCASTER_PAN_ID >> 8);
    s_frame_buf[f++] = 0xFF;
    s_frame_buf[f++] = 0xFF;
    memcpy(s_frame_buf + f, s_eui64, 8);    f += 8;
    s_frame_buf[f++] = SEC_CTRL;
    s_frame_buf[f++] = (uint8_t)(s_frame_counter);
    s_frame_buf[f++] = (uint8_t)(s_frame_counter >>  8);
    s_frame_buf[f++] = (uint8_t)(s_frame_counter >> 16);
    s_frame_buf[f++] = (uint8_t)(s_frame_counter >> 24);
    memcpy(s_frame_buf + f, key_source, 4); f += 4;
    s_frame_buf[f++] = KEY_INDEX;
    memcpy(s_frame_buf + f, ciphertext, flag_len); f += (int)flag_len;
    memcpy(s_frame_buf + f, mic, 4);                f += 4;
    s_frame_buf[0] = (uint8_t)(f - 1 + 2);   /* PSDU length excludes the length byte */

    s_frame_counter++;

    esp_ieee802154_transmit(s_frame_buf, false);
    xSemaphoreTake(s_tx_done_sem, pdMS_TO_TICKS(500));
}

/* ── broadcast task ───────────────────────────────────────────────────── */

static void broadcast_task(void *pv)
{
    while (1) {
        build_and_transmit();
        ESP_LOGI(TAG, "frame #%lu tx (PAN 0x%04X CH%d key_seq=%u)",
                 (unsigned long)(s_frame_counter - 1),
                 BROADCASTER_PAN_ID, BROADCASTER_CHANNEL, KEY_SEQUENCE);
        vTaskDelay(pdMS_TO_TICKS(BROADCAST_INTERVAL_MS));
    }
}

/* ── app_main ─────────────────────────────────────────────────────────── */

void app_main(void)
{
    nvs_flash_init();
    psa_crypto_init();

    s_tx_done_sem = xSemaphoreCreateBinary();

    esp_read_mac(s_eui64, ESP_MAC_IEEE802154);
    derive_mac_key();

    printf("\n");
    printf("=== GreyFlag broadcaster ===\n");
    printf("channel   : %d\n",     BROADCASTER_CHANNEL);
    printf("PAN ID    : 0x%04X\n", BROADCASTER_PAN_ID);
    printf("key seq   : %u  ->  key index %u\n", KEY_SEQUENCE, KEY_INDEX);
    printf("mac key   : ");
    for (int i = 0; i < 16; i++) printf("%02x", s_mac_key[i]);
    printf("\n");
    printf("EUI-64    : ");
    for (int i = 0; i < 8; i++) printf("%02x", s_eui64[i]);
    printf("\n");
    printf("============================\n\n");

    esp_ieee802154_enable();
    esp_ieee802154_set_promiscuous(false);
    esp_ieee802154_set_panid(BROADCASTER_PAN_ID);
    esp_ieee802154_set_channel(BROADCASTER_CHANNEL);
    esp_ieee802154_set_extended_address(s_eui64);
    esp_ieee802154_receive();

    xTaskCreate(broadcast_task, "broadcaster", 4096, NULL, 5, NULL);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(10000));
    }
}
