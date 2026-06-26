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

#define I2S_BCLK_PIN   19
#define I2S_LRCLK_PIN  20
#define I2S_DIN_PIN    21
#define SAMPLE_RATE    48000          /* slow & guessable */
#define BUF_SAMPLES    512           /* ~64ms of audio per read */

static const char *TAG = "CTF_MIC";

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
    ESP_LOGI(TAG, "Listening at %d Hz — feed me a tone!", SAMPLE_RATE);

    int16_t *buf = malloc(BUF_SAMPLES * 2 * sizeof(int16_t));   /* stereo */

    while (1) {
        size_t got = 0;
        i2s_channel_read(rx, buf, BUF_SAMPLES * 2 * sizeof(int16_t),
                         &got, pdMS_TO_TICKS(1000));
        int n = got / sizeof(int16_t);

        /* analyse LEFT slot only (every even sample) */
        int32_t peak = 0;
        int64_t sum_sq = 0;
        int     zero_crossings = 0;
        int16_t prev = 0;

        for (int i = 0; i < n; i += 2) {
            int16_t s = buf[i];
            int32_t a = s < 0 ? -s : s;
            if (a > peak) peak = a;
            sum_sq += (int32_t)s * s;
            if ((prev >= 0 && s < 0) || (prev < 0 && s >= 0)) zero_crossings++;
            prev = s;
        }

        int samples_left = n / 2;
        int rms = (samples_left > 0) ? (int)sqrt((double)sum_sq / samples_left) : 0;
        float duration_s = (float)samples_left / SAMPLE_RATE;
        float freq_hz    = (zero_crossings / 2.0f) / duration_s;

        /* visual level bar */
        int bar = peak / 500;  if (bar > 40) bar = 40;
        char b[42] = {0};
        for (int i = 0; i < bar; i++) b[i] = '#';

        ESP_LOGI(TAG, "Peak:%6ld RMS:%5d  ~%.0f Hz  [%-40s]",
                 (long)peak, rms, freq_hz, b);

        vTaskDelay(pdMS_TO_TICKS(200));
    }
}

static const float ch2_tier_hz[] = { 1, 500, 2000, 5000, 10000, 15000 };
static const char *ch2_tier_msg[] = {
    "Oh, I think I hear something...",
    "Huh, is someone talking?",
    "Wow, you are a superb soprano!",
    "Whew - that's dog-whistle territory.",
    "Yikes, why did you turn this into an audio test?",
    "And this, is, to go, even. further. BEYOND!",
};