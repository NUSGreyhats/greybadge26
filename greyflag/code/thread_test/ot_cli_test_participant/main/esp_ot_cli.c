/*
 * SPDX-FileCopyrightText: 2021-2026 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 *
 * OpenThread Command Line Example
 *
 * This example code is in the Public Domain (or CC0 licensed, at your option.)
 *
 * Unless required by applicable law or agreed to in writing, this
 * software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
 * CONDITIONS OF ANY KIND, either express or implied.
*/

#include <stdio.h>
#include <unistd.h>
#include <string.h>

#include "sdkconfig.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_netif_types.h"
#include "esp_openthread.h"
#include "esp_openthread_lock.h"
#include "esp_openthread_netif_glue.h"
#include "esp_openthread_types.h"
#include "esp_ot_config.h"
#include "esp_vfs_eventfd.h"
#include "nvs_flash.h"
#include "ot_examples_common.h"
#include "openthread/dataset.h"
#include "openthread/instance.h"
#include "openthread/thread.h"

#if CONFIG_OPENTHREAD_STATE_INDICATOR_ENABLE
#include "ot_led_strip.h"
#endif

#if CONFIG_OPENTHREAD_CLI_ESP_EXTENSION
#include "esp_ot_cli_extension.h"
#endif // CONFIG_OPENTHREAD_CLI_ESP_EXTENSION

#define TAG "ot_esp_cli"

#define JOINER_CREDENTIAL "GREYFLAG99"

static bool s_welcomed = false;
static bool s_attach_started = false;

static void participant_state_changed(otChangedFlags changed, void *ctx)
{
    otInstance *inst = (otInstance *)ctx;

    // When the joiner finishes, the active dataset gains a network key.
    // Detect that and auto-start Thread so the user needn't type "ot thread start".
    if (!s_attach_started) {
        otOperationalDataset dataset;
        if (otDatasetGetActive(inst, &dataset) == OT_ERROR_NONE &&
            dataset.mComponents.mIsNetworkKeyPresent &&
            otThreadGetDeviceRole(inst) == OT_DEVICE_ROLE_DISABLED) {
            s_attach_started = true;
            otThreadSetEnabled(inst, true);   // auto-attach
        }
    }

    if (changed & OT_CHANGED_THREAD_ROLE) {
        otDeviceRole role = otThreadGetDeviceRole(inst);
        if (!s_welcomed &&
            (role == OT_DEVICE_ROLE_CHILD || role == OT_DEVICE_ROLE_ROUTER)) {
            s_welcomed = true;
            printf("\nWelcome to the GreyFlag network\n\n");
        }
    }
}

void app_main(void)
{
    // Used eventfds:
    // * netif
    // * ot task queue
    // * radio driver
    esp_vfs_eventfd_config_t eventfd_config = {
        .max_fds = 3,
    };

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_vfs_eventfd_register(&eventfd_config));

    printf("================================\n");
    printf("  GreyFlag IoT badge\n");
    printf("  Our brand-new IoT platform.\n");
    printf("  Joiner credential: %s\n", JOINER_CREDENTIAL);
    printf("================================\n\n");

#if CONFIG_OPENTHREAD_CLI
    ot_console_start();
    ot_register_external_commands();
#endif

    static esp_openthread_config_t config = {
        .netif_config = ESP_NETIF_DEFAULT_OPENTHREAD(),
        .platform_config = {
            .radio_config = ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG(),
            .host_config = ESP_OPENTHREAD_DEFAULT_HOST_CONFIG(),
            .port_config = ESP_OPENTHREAD_DEFAULT_PORT_CONFIG(),
        },
    };

    ESP_ERROR_CHECK(esp_openthread_start(&config));

    esp_openthread_lock_acquire(portMAX_DELAY);
    otInstance *inst = esp_openthread_get_instance();
    otSetStateChangedCallback(inst, participant_state_changed, inst);
    esp_openthread_lock_release();

#if CONFIG_OPENTHREAD_CLI_ESP_EXTENSION
    esp_cli_custom_command_init();
#endif
#if CONFIG_OPENTHREAD_STATE_INDICATOR_ENABLE
    ESP_ERROR_CHECK(esp_openthread_state_indicator_init(esp_openthread_get_instance()));
#endif
#if CONFIG_OPENTHREAD_NETWORK_AUTO_START
    ot_network_auto_start();
#endif
}
