#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_openthread.h"
#include "esp_openthread_types.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_vfs_eventfd.h"
#include "openthread/commissioner.h"
#include "openthread/dataset.h"
#include "openthread/dataset_ftd.h"
#include "openthread/instance.h"
#include "openthread/thread.h"
#include "openthread/thread_ftd.h"

#define JOINER_CREDENTIAL  "CTFKEY99"
#define NETWORK_CHANNEL    15
#define NETWORK_PAN_ID     0x1234
#define NETWORK_NAME       "greyflag"

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
        otInstance *inst = (otInstance *)ctx;   // pass inst as ctx below

        otExtAddress wildcard;
        memset(&wildcard, 0xFF, sizeof(wildcard));
        otError err = otCommissionerAddJoiner(inst, &wildcard,
                                              JOINER_CREDENTIAL, 0xFFFFFFFF);
        printf("[COMM] AddJoiner returned: %d\n", err);
        if (err == OT_ERROR_NONE) {
            printf("[COMM] ready — credential: %s\n", JOINER_CREDENTIAL);
        }
    }
}

static void joiner_event_cb(otCommissionerJoinerEvent event,
                             const otJoinerInfo *joiner_info,
                             const otExtAddress *joiner_id,
                             void *ctx)
{
    if (event == OT_COMMISSIONER_JOINER_FINALIZE) {
        printf("[COMM] badge joined successfully\n");
    } else if (event == OT_COMMISSIONER_JOINER_END) {
        printf("[COMM] joiner session ended\n");
    }
}

static void try_start_commissioner(otInstance *inst)
{
    if (s_commissioner_started) return;

    otDeviceRole role = otThreadGetDeviceRole(inst);
    const char *roles[] = { "disabled", "detached", "child", "router", "leader" };
    printf("[COMM] try_start_commissioner: role = %s\n", roles[role]);

    if (role != OT_DEVICE_ROLE_LEADER && role != OT_DEVICE_ROLE_ROUTER) {
        printf("[COMM] not ready yet, waiting for role change\n");
        return;
    }

    otError err = otCommissionerStart(inst,
                                      commissioner_state_cb,
                                      joiner_event_cb,
                                      inst);   // ← pass inst here, not NULL
                                      // in try_start_commissioner:

    printf("[COMM] otCommissionerStart returned: %d\n", err);
    if (err != OT_ERROR_NONE) return;

    s_commissioner_started = true;

    otExtAddress wildcard;
    memset(&wildcard, 0xFF, sizeof(wildcard));
    err = otCommissionerAddJoiner(inst, &wildcard, JOINER_CREDENTIAL, 0xFFFFFFFF);
    printf("[COMM] AddJoiner returned: %d\n", err);
    printf("[COMM] ready — credential: %s\n", JOINER_CREDENTIAL);
}

static void thread_state_changed(otChangedFlags changed, void *ctx)
{
    if (!(changed & OT_CHANGED_THREAD_ROLE)) return;
    printf("[COMM] state change callback fired\n");
    try_start_commissioner((otInstance *)ctx);
}

void app_main(void)
{
    nvs_flash_init();
    esp_netif_init();
    esp_event_loop_create_default();

    printf("[ORGANISER] commissioner starting\n");

    esp_openthread_platform_config_t config = {
        .radio_config = {
            .radio_mode = RADIO_MODE_NATIVE,
        },
        .host_config = {
            .host_connection_mode = HOST_CONNECTION_MODE_NONE,
        },
        .port_config = {
            .storage_partition_name = "nvs",
            .netif_queue_size       = 10,
            .task_queue_size        = 10,
        },
    };

    esp_vfs_eventfd_config_t efd_config = ESP_VFS_EVENTD_CONFIG_DEFAULT();
    esp_vfs_eventfd_register(&efd_config);

    esp_openthread_init(&config);
    otInstance *inst = esp_openthread_get_instance();

    // Register BEFORE enabling Thread so we catch the first role transition
    otSetStateChangedCallback(inst, thread_state_changed, inst);

    otOperationalDataset dataset;
    memset(&dataset, 0, sizeof(dataset));
    otDatasetCreateNewNetwork(inst, &dataset);

    dataset.mChannel = NETWORK_CHANNEL;
    dataset.mComponents.mIsChannelPresent = true;

    dataset.mPanId = NETWORK_PAN_ID;
    dataset.mComponents.mIsPanIdPresent = true;

    memcpy(dataset.mNetworkKey.m8, NETWORK_KEY, OT_NETWORK_KEY_SIZE);
    dataset.mComponents.mIsNetworkKeyPresent = true;

    memset(dataset.mNetworkName.m8, 0, sizeof(dataset.mNetworkName.m8));
    strncpy(dataset.mNetworkName.m8, NETWORK_NAME, OT_NETWORK_NAME_MAX_SIZE);
    dataset.mComponents.mIsNetworkNamePresent = true;

    otDatasetSetActive(inst, &dataset);
    otIp6SetEnabled(inst, true);
    otThreadSetEnabled(inst, true);

    printf("[COMM] Thread enabled, current role: %d\n",
           otThreadGetDeviceRole(inst));

    // No separate commissioner task — state callback handles everything
    esp_openthread_launch_mainloop();
}