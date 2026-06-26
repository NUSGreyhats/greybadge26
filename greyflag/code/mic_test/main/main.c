#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include <math.h>

/* ── Front-of-stage mic station (standalone, no OpenThread) ──────────────
 * Participants inject a 3.3 V square wave into DIN and sweep the pitch up.
 * Each frequency tier is announced once; crossing 20 kHz (above human
 * hearing) reveals the real flag. 100 kHz sampling (proven on this board). */

#define I2S_BCLK_PIN   19
#define I2S_LRCLK_PIN  20
#define I2S_DIN_PIN    21
#define SAMPLE_RATE    100000
#define BUF_SAMPLES    512

#define NOISE_FLOOR    300          /* below this peak the line is "silent" */
#define FREQ_THRESHOLD 20000.0f     /* flag frequency (ultrasonic) */
#define REAL_FLAG      "grey{G0sh_i_can_see_your_mouth_moving_but_i_hear_nothing}"

static const char *TAG = "CTF_MIC";

/* Ascending frequency tiers; each is announced once as the pitch climbs. */
static const float tier_hz[] = { 1, 500, 2000, 5000, 10000, 15000 };
static const char *tier_msg[] = {
    "Oh, I think I hear something...",
    "Huh, is someone talking?",
    "Wow, you are a superb soprano!",
    "Whew - that's dog-whistle territory.",
    "Yikes, why did you turn this into an audio test?",
    "And this, is, to go, even. further. BEYOND!",
};
#define NTIERS ((int)(sizeof(tier_hz) / sizeof(tier_hz[0])))

void app_main(void)
{
    i2s_chan_handle_t rx;
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num  = 6;
    chan_cfg.dma_frame_num = 240;
    chan_cfg.auto_clear    = true;
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, NULL, &rx));

    i2s_std_config_t std_cfg = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(16, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED, .bclk = I2S_BCLK_PIN,
            .ws   = I2S_LRCLK_PIN,   .dout = I2S_GPIO_UNUSED,
            .din  = I2S_DIN_PIN,     .invert_flags = { false, false, false },
        },
    };
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(rx));
    ESP_LOGI(TAG, "Music to My Ear - listening at %d Hz. Sing me a song!", SAMPLE_RATE);

    int16_t *buf = malloc(BUF_SAMPLES * 2 * sizeof(int16_t));   /* stereo */
    int last_tier = -1;

    while (1) {
        size_t got = 0;
        i2s_channel_read(rx, buf, BUF_SAMPLES * 2 * sizeof(int16_t),
                         &got, pdMS_TO_TICKS(1000));
        int n = got / sizeof(int16_t);

        /* analyse LEFT slot only (every even sample) */
        int32_t peak = 0;
        int     zero_crossings = 0;
        int16_t prev = 0;

        for (int i = 0; i < n; i += 2) {
            int16_t s = buf[i];
            int32_t a = s < 0 ? -s : s;
            if (a > peak) peak = a;
            if ((prev >= 0 && s < 0) || (prev < 0 && s >= 0)) zero_crossings++;
            prev = s;
        }

        int   samples  = n / 2;
        float duration = (float)samples / SAMPLE_RATE;
        float freq     = duration > 0 ? (zero_crossings / 2.0f) / duration : 0.0f;

        /* Live readout: overwrite the same line in place (\r, no newline) so it
         * behaves like a counter instead of flooding the screen. Tier/flag
         * messages below print with a leading newline so they scroll as history. */
        int bar = peak / 500; if (bar > 40) bar = 40;
        char b[42] = {0};
        for (int i = 0; i < bar; i++) b[i] = '#';
        printf("\rPeak:%6ld  ~%.0f Hz  [%-40s]", (long)peak, freq, b);
        fflush(stdout);

        /* Silence: reset so the next person's sweep re-announces from scratch. */
        if (peak < NOISE_FLOOR) {
            last_tier = -1;
            vTaskDelay(pdMS_TO_TICKS(200));
            continue;
        }

        /* Determine current tier (the flag sits above all named tiers). */
        bool at_flag = (freq >= FREQ_THRESHOLD);
        int  tier = at_flag ? NTIERS : -1;
        if (!at_flag)
            for (int i = 0; i < NTIERS; i++)
                if (freq >= tier_hz[i]) tier = i;

        /* Announce only when climbing into a new, higher tier. */
        if (tier > last_tier) {
            if (at_flag) {
                printf("\n*** ...past everything a human could ever sing. ***\n");
                printf("*** FLAG: %s ***\n\n", REAL_FLAG);
            } else if (tier >= 0) {
                printf("\n%s  (~%.0f Hz)\n", tier_msg[tier], freq);
            }
        }
        last_tier = tier;

        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
