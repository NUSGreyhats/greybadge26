#pragma once
/*
 * Speaker output via I2S TX on IO18 (DOUT), shared BCLK/LRCLK with the mic.
 * Plays WAV files stored in SPIFFS. Two formats are supported:
 *   - PCM 16-bit LE  (WAVE format tag 0x0001) — no decode, streamed directly
 *   - IMA ADPCM      (WAVE format tag 0x0011) — ~4:1, tiny integer decoder
 * The sample rate / channel count come from the WAV header, so nothing is
 * hardcoded. Mono is duplicated to L+R for the stereo I2S slot.
 *
 * To add audio:
 *   1. Convert your source to an 11 kHz mono WAV and place it in spiffs_data/:
 *        ADPCM:  ffmpeg -i in.mp3 -ar 11025 -ac 1 -c:a adpcm_ima_wav anone.wav
 *        PCM16:  ffmpeg -i in.mp3 -ar 11025 -ac 1 -c:a pcm_s16le    anone.wav
 *   2. idf.py -C main_firmware flash   (CMake builds + flashes the SPIFFS image)
 *
 * ADPCM is ~4x smaller than PCM16 for the same clip; PCM16 costs zero CPU.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <dirent.h>
#include "driver/i2s_std.h"
#include "esp_spiffs.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SPK_DOUT_PIN    18
#define SPK_BCLK_PIN    19
#define SPK_LRCLK_PIN   20
#define SPK_SPIFFS_BASE "/spiffs"

#define WAVE_FMT_PCM        0x0001
#define WAVE_FMT_IMA_ADPCM  0x0011

/* Master output cap to limit speaker current draw and avoid LiPo brownout.
 * Full-scale (32767) audio is scaled down so peaks reach at most SPK_OUTPUT_PEAK.
 * 2000/32767 ≈ 6% — raise SPK_OUTPUT_PEAK for more volume if the supply allows. */
#define SPK_OUTPUT_PEAK  2000

static i2s_chan_handle_t s_spk_tx = NULL;

/* ── I2S TX ──────────────────────────────────────────────────── */

static void spk_i2s_start(int sample_rate)
{
    if (s_spk_tx) {
        i2s_channel_disable(s_spk_tx);
        i2s_del_channel(s_spk_tx);
        s_spk_tx = NULL;
    }
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num  = 6;
    chan_cfg.dma_frame_num = 240;
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &s_spk_tx, NULL));

    i2s_std_config_t std_cfg = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG((uint32_t)sample_rate),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(16, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = SPK_BCLK_PIN,
            .ws   = SPK_LRCLK_PIN,
            .dout = SPK_DOUT_PIN,
            .din  = I2S_GPIO_UNUSED,
            .invert_flags = { false, false, false },
        },
    };
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(s_spk_tx, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(s_spk_tx));
}

static void spk_i2s_stop(void)
{
    if (!s_spk_tx) return;
    i2s_channel_disable(s_spk_tx);
    i2s_del_channel(s_spk_tx);
    s_spk_tx = NULL;
}

/* True if the user wants to stop playback (any key pressed). The pressed key
 * is consumed here so it doesn't leak into the speaker menu afterwards. */
static bool spk_should_stop(void)
{
    return fgetc(stdin) != EOF;
}

/* Write a buffer of mono int16 samples to I2S, duplicating to L+R.
 * Each sample is attenuated to the SPK_OUTPUT_PEAK cap before output.
 * Returns true if playback should be aborted (a key was pressed). */
static bool spk_write_mono(const int16_t *mono, int count)
{
    int16_t stereo[256 * 2];
    int i = 0;
    while (i < count) {
        int chunk = (count - i) > 256 ? 256 : (count - i);
        for (int j = 0; j < chunk; j++) {
            int32_t s = ((int32_t)mono[i + j] * SPK_OUTPUT_PEAK) / 32767;
            stereo[j * 2]     = (int16_t)s;
            stereo[j * 2 + 1] = (int16_t)s;
        }
        size_t written = 0;
        i2s_channel_write(s_spk_tx, stereo, chunk * 2 * sizeof(int16_t),
                          &written, pdMS_TO_TICKS(500));
        i += chunk;
        if (spk_should_stop()) return true;
    }
    return false;
}

/* ── IMA ADPCM decode tables ────────────────────────────────── */

static const int8_t ima_index_table[16] = {
    -1, -1, -1, -1, 2, 4, 6, 8,
    -1, -1, -1, -1, 2, 4, 6, 8,
};

static const int16_t ima_step_table[89] = {
    7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,50,55,60,66,73,80,
    88,97,107,118,130,143,157,173,190,209,230,253,279,307,337,371,408,449,494,
    544,598,658,724,796,876,963,1060,1166,1282,1411,1552,1707,1878,2066,2272,
    2499,2749,3024,3327,3660,4026,4428,4871,5358,5894,6484,7132,7845,8630,9493,
    10442,11487,12635,13899,15289,16818,18500,20350,22385,24623,27086,29794,32767
};

static int16_t ima_decode_nibble(uint8_t nibble, int *predictor, int *index)
{
    int step = ima_step_table[*index];
    int diff = step >> 3;
    if (nibble & 1) diff += step >> 2;
    if (nibble & 2) diff += step >> 1;
    if (nibble & 4) diff += step;
    if (nibble & 8) diff = -diff;

    int pred = *predictor + diff;
    if (pred >  32767) pred =  32767;
    if (pred < -32768) pred = -32768;
    *predictor = pred;

    int idx = *index + ima_index_table[nibble];
    if (idx < 0)  idx = 0;
    if (idx > 88) idx = 88;
    *index = idx;

    return (int16_t)pred;
}

/* ── WAV header parsing ─────────────────────────────────────── */

typedef struct {
    uint16_t format;
    uint16_t channels;
    uint32_t sample_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;
    uint16_t samples_per_block; /* ADPCM only */
    uint32_t data_size;
} wav_info_t;

static uint16_t rd_u16(const uint8_t *p) { return p[0] | (p[1] << 8); }
static uint32_t rd_u32(const uint8_t *p) {
    return p[0] | (p[1] << 8) | (p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* Parses RIFF/WAVE, leaves the file positioned at the start of PCM/ADPCM
 * sample data. Returns true on success. */
static bool wav_parse(FILE *f, wav_info_t *out)
{
    uint8_t hdr[12];
    if (fread(hdr, 1, 12, f) != 12) return false;
    if (memcmp(hdr, "RIFF", 4) != 0 || memcmp(hdr + 8, "WAVE", 4) != 0)
        return false;

    bool have_fmt = false;
    uint8_t chunk[8];
    while (fread(chunk, 1, 8, f) == 8) {
        uint32_t size = rd_u32(chunk + 4);
        if (memcmp(chunk, "fmt ", 4) == 0) {
            uint8_t fmt[40];
            uint32_t n = size > sizeof(fmt) ? sizeof(fmt) : size;
            if (fread(fmt, 1, n, f) != n) return false;
            out->format          = rd_u16(fmt + 0);
            out->channels        = rd_u16(fmt + 2);
            out->sample_rate     = rd_u32(fmt + 4);
            out->block_align     = rd_u16(fmt + 12);
            out->bits_per_sample = rd_u16(fmt + 14);
            out->samples_per_block = (n >= 20) ? rd_u16(fmt + 18) : 0;
            have_fmt = true;
            if (size > n) fseek(f, size - n, SEEK_CUR);
        } else if (memcmp(chunk, "data", 4) == 0) {
            out->data_size = size;
            return have_fmt; /* positioned at sample data */
        } else {
            fseek(f, size + (size & 1), SEEK_CUR); /* skip + pad to even */
        }
    }
    return false;
}

/* ── Playback ───────────────────────────────────────────────── */

static void play_wav(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) { printf("Cannot open: %s\n", path); return; }

    wav_info_t w = {0};
    if (!wav_parse(f, &w)) {
        printf("Not a supported WAV: %s\n", path);
        fclose(f);
        return;
    }
    if (w.channels != 1) {
        printf("Only mono WAV is supported (%s is %u ch)\n", path, w.channels);
        fclose(f);
        return;
    }

    printf("Playing %s  [%lu Hz, %s]  (press any key to stop)\n", path,
           (unsigned long)w.sample_rate,
           w.format == WAVE_FMT_IMA_ADPCM ? "IMA ADPCM" : "PCM16");
    spk_i2s_start((int)w.sample_rate);
    bool aborted = false;

    if (w.format == WAVE_FMT_PCM && w.bits_per_sample == 16) {
        int16_t buf[512];
        size_t got;
        while (!aborted && (got = fread(buf, sizeof(int16_t), 512, f)) > 0)
            aborted = spk_write_mono(buf, (int)got);

    } else if (w.format == WAVE_FMT_IMA_ADPCM) {
        uint8_t *block = malloc(w.block_align);
        int16_t *pcm   = malloc(w.samples_per_block * sizeof(int16_t));
        if (block && pcm) {
            size_t got;
            while (!aborted && (got = fread(block, 1, w.block_align, f)) >= 4) {
                /* per-block header (mono): predictor(i16), index(u8), reserved */
                int predictor = (int16_t)rd_u16(block);
                int index     = block[2];
                if (index > 88) index = 88;
                int out = 0;
                pcm[out++] = (int16_t)predictor;
                /* remaining bytes: two 4-bit samples each, low nibble first */
                for (size_t i = 4; i < got && out < w.samples_per_block; i++) {
                    pcm[out++] = ima_decode_nibble(block[i] & 0x0F, &predictor, &index);
                    if (out < w.samples_per_block)
                        pcm[out++] = ima_decode_nibble(block[i] >> 4, &predictor, &index);
                }
                aborted = spk_write_mono(pcm, out);
            }
        }
        free(block);
        free(pcm);

    } else {
        printf("Unsupported WAV format tag 0x%04X (bits=%u)\n",
               w.format, w.bits_per_sample);
    }

    spk_i2s_stop();
    fclose(f);
    printf(aborted ? "Playback stopped.\n" : "Playback complete.\n");
}

/* ── SPIFFS ─────────────────────────────────────────────────── */

static bool spiffs_mounted = false;

static void spk_mount_spiffs(void)
{
    if (spiffs_mounted) return;
    esp_vfs_spiffs_conf_t conf = {
        .base_path              = SPK_SPIFFS_BASE,
        .partition_label        = "storage",
        .max_files              = 8,
        .format_if_mount_failed = false,
    };
    esp_err_t ret = esp_vfs_spiffs_register(&conf);
    if (ret == ESP_OK || ret == ESP_ERR_INVALID_STATE)
        spiffs_mounted = true;
    else
        printf("SPIFFS mount failed: %s\n", esp_err_to_name(ret));
}

/* ── Speaker menu ───────────────────────────────────────────── */

#define MAX_TRACKS 16
#define TRACK_PATH_MAX 288   /* "/spiffs/" + up to 255-char d_name + NUL */
static char track_paths[MAX_TRACKS][TRACK_PATH_MAX];
static int  track_count = 0;

void setupSpeaker(void)
{
    spk_mount_spiffs();
    track_count = 0;

    printf("\n==========================\n");
    printf("  SPEAKER SAMPLES\n");
    printf("==========================\n");

    if (spiffs_mounted) {
        DIR *d = opendir(SPK_SPIFFS_BASE);
        if (d) {
            struct dirent *ent;
            while ((ent = readdir(d)) != NULL && track_count < MAX_TRACKS) {
                size_t len = strlen(ent->d_name);
                if (len > 4 && strcasecmp(ent->d_name + len - 4, ".wav") == 0) {
                    snprintf(track_paths[track_count], TRACK_PATH_MAX,
                             SPK_SPIFFS_BASE "/%s", ent->d_name);
                    printf("[%d] %s\n", track_count + 1, ent->d_name);
                    track_count++;
                }
            }
            closedir(d);
        }
    }

    if (track_count == 0) {
        printf("\nNo WAV files found on storage partition.\n");
        printf("Add mono .wav files to spiffs_data/ and reflash.\n");
    }

    printf("[0] Back\n");
    printf("Enter choice: ");
    fflush(stdout);
}

/* returns true if the user wants to go back to the main menu */
bool runSpeaker(char c)
{
    if (c == '\n' || c == '\r') return false;
    if (c == '0') return true;

    int idx = c - '1';
    if (idx >= 0 && idx < track_count) {
        play_wav(track_paths[idx]);
        setupSpeaker();
        return false;
    }

    printf("Invalid. Enter choice: ");
    fflush(stdout);
    return false;
}
