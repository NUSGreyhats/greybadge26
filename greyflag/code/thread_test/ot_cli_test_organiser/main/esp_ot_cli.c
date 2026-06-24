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
#include "openthread/commissioner.h"
#include "openthread/dataset.h"
#include "openthread/dataset_ftd.h"
#include "openthread/instance.h"
#include "openthread/thread.h"
#include "openthread/thread_ftd.h"

#define JOINER_CREDENTIAL "CTFKEY99"

static const uint8_t NETWORK_KEY[OT_NETWORK_KEY_SIZE] = {
    0xAA, 0xAD, 0xBE, 0xEB, 0xCA, 0xAC, 0xBA, 0xDD,
    0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF
};

static bool s_commissioner_started = false;

static void commissioner_state_cb(otCommissionerState state, void *ctx)
{
    const char *names[] = { "disabled", "petition", "active" };
    printf("[COMM] state -> %s\n", names[state]);
    if (state == OT_COMMISSIONER_STATE_ACTIVE) {
        otInstance *inst = (otInstance *)ctx;
        // NULL EUI-64 = accept ANY joiner (true wildcard, same as CLI's "*")
        otError err = otCommissionerAddJoiner(inst, NULL, JOINER_CREDENTIAL, 3600);
        printf("[COMM] AddJoiner returned: %d\n", err);
        if (err == OT_ERROR_NONE)
            printf("[COMM] ready — credential: %s\n", JOINER_CREDENTIAL);
    }
}

static void joiner_event_cb(otCommissionerJoinerEvent event,
                            const otJoinerInfo *info,
                            const otExtAddress *id, void *ctx)
{
    if (event == OT_COMMISSIONER_JOINER_FINALIZE)
        printf("[COMM] badge joined successfully\n");
    else if (event == OT_COMMISSIONER_JOINER_END)
        printf("[COMM] joiner session ended\n");
}

static void try_start_commissioner(otInstance *inst)
{
    if (s_commissioner_started) return;
    otDeviceRole role = otThreadGetDeviceRole(inst);
    if (role != OT_DEVICE_ROLE_LEADER && role != OT_DEVICE_ROLE_ROUTER) return;
    otError err = otCommissionerStart(inst, commissioner_state_cb, joiner_event_cb, inst);
    printf("[COMM] otCommissionerStart returned: %d\n", err);
    if (err != OT_ERROR_NONE) return;
    s_commissioner_started = true;
}

static void thread_state_changed(otChangedFlags changed, void *ctx)
{
    if (!(changed & OT_CHANGED_THREAD_ROLE)) return;
    try_start_commissioner((otInstance *)ctx);
}

#if CONFIG_OPENTHREAD_STATE_INDICATOR_ENABLE
#include "ot_led_strip.h"
#endif

#if CONFIG_OPENTHREAD_CLI_ESP_EXTENSION
#include "esp_ot_cli_extension.h"
#endif // CONFIG_OPENTHREAD_CLI_ESP_EXTENSION

#define TAG "ot_esp_cli"

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

    // after esp_openthread_start(&config); in the ot_cli example's app_main:

    esp_openthread_lock_acquire(portMAX_DELAY);
    otInstance *inst = esp_openthread_get_instance();

    otSetStateChangedCallback(inst, thread_state_changed, inst);

    otOperationalDataset dataset;
    memset(&dataset, 0, sizeof(dataset));
    otDatasetCreateNewNetwork(inst, &dataset);
    dataset.mChannel = 25;
    dataset.mComponents.mIsChannelPresent = true;
    dataset.mPanId = 0x1234;
    dataset.mComponents.mIsPanIdPresent = true;
    memcpy(dataset.mNetworkKey.m8, NETWORK_KEY, OT_NETWORK_KEY_SIZE);
    dataset.mComponents.mIsNetworkKeyPresent = true;
    memset(dataset.mNetworkName.m8, 0, sizeof(dataset.mNetworkName.m8));
    strncpy(dataset.mNetworkName.m8, "GreyFlag", OT_NETWORK_NAME_MAX_SIZE);
    dataset.mComponents.mIsNetworkNamePresent = true;
    otDatasetSetActive(inst, &dataset);

    otIp6SetEnabled(inst, true);
    otThreadSetEnabled(inst, true);
    esp_openthread_lock_release();

#if CONFIG_OPENTHREAD_CLI_ESP_EXTENSION
    esp_cli_custom_command_init();
#endif
#if CONFIG_OPENTHREAD_STATE_INDICATOR_ENABLE
    ESP_ERROR_CHECK(esp_openthread_state_indicator_init(esp_openthread_get_instance()));
#endif
#if CONFIG_OPENTHREAD_NETWORK_AUTO_START
    //ot_network_auto_start();
#endif
}
