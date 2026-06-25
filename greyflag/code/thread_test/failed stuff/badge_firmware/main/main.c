#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_openthread.h"
#include "esp_openthread_types.h"
#include "esp_vfs_eventfd.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "openthread/dataset.h"
#include "openthread/instance.h"
#include "openthread/joiner.h"
#include "openthread/thread.h"
#include "openthread/udp.h"

#define JOINER_CREDENTIAL  "Grey9999"
#define WELCOME_PORT        1234
#define WELCOME_MSG         "Welcome to GreyFlag IoT network"

static otUdpSocket s_udp_socket;
static bool        s_welcome_sent = false;

static void send_welcome(otInstance *inst)
{
    if (s_welcome_sent) return;

    otMessage *msg = otUdpNewMessage(inst, NULL);
    if (!msg) return;

    if (otMessageAppend(msg, WELCOME_MSG, strlen(WELCOME_MSG)) != OT_ERROR_NONE) {
        otMessageFree(msg);
        return;
    }

    otMessageInfo info;
    memset(&info, 0, sizeof(info));
    info.mPeerAddr.mFields.m8[0]  = 0xff;
    info.mPeerAddr.mFields.m8[1]  = 0x03;
    info.mPeerAddr.mFields.m8[15] = 0x01;
    info.mPeerPort = WELCOME_PORT;

    if (otUdpOpen(inst, &s_udp_socket, NULL, NULL) != OT_ERROR_NONE) {
        otMessageFree(msg);
        return;
    }

    otError err = otUdpSend(inst, &s_udp_socket, msg, &info);
    if (err != OT_ERROR_NONE) {
        otMessageFree(msg);
    }

    otUdpClose(inst, &s_udp_socket);
    s_welcome_sent = true;
}

static void thread_state_changed(otChangedFlags changed, void *ctx)
{
    if (!(changed & OT_CHANGED_THREAD_ROLE)) return;

    otInstance *inst = (otInstance *)ctx;
    otDeviceRole role = otThreadGetDeviceRole(inst);
    const char *roles[] = { "disabled", "detached", "child", "router", "leader" };
    printf("[JOINER] role -> %s\n", roles[role]);

    if (role == OT_DEVICE_ROLE_CHILD || role == OT_DEVICE_ROLE_ROUTER) {
        send_welcome(inst);
    }
}

static void joiner_callback(otError error, void *context)
{
    otInstance *inst = (otInstance *)context;
    if (error == OT_ERROR_NONE) {
        printf("[JOINER] join succeeded — attaching\n");
        otThreadSetEnabled(inst, true);
    } else {
        printf("[JOINER] join FAILED: %d\n", error);
    }
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // eventfd required by esp_openthread_launch_mainloop
    esp_vfs_eventfd_config_t efd_config = { .max_fds = 2 };
    ESP_ERROR_CHECK(esp_vfs_eventfd_register(&efd_config));


    printf("\n");
    printf("================================\n");
    printf("  GreyFlag IoT badge\n");
    printf("  Our brand-new IoT platform.\n");
    printf("  Joiner credential: %s\n", JOINER_CREDENTIAL);
    printf("================================\n\n");

    esp_openthread_platform_config_t config = {
        .radio_config = { .radio_mode = RADIO_MODE_NATIVE },
        .host_config  = { .host_connection_mode = HOST_CONNECTION_MODE_NONE },
        .port_config  = {
            .storage_partition_name = "nvs",
            .netif_queue_size       = 10,
            .task_queue_size        = 10,
        },
    };

    ESP_ERROR_CHECK(esp_openthread_init(&config));
    otInstance *instance = esp_openthread_get_instance();

    otSetStateChangedCallback(instance, thread_state_changed, instance);

    otOperationalDataset dataset;
    if (otDatasetGetActive(instance, &dataset) == OT_ERROR_NONE) {
        printf("[JOINER] already joined, re-attaching\n");
        otIp6SetEnabled(instance, true);
        otThreadSetEnabled(instance, true);
    } else {
        printf("[JOINER] first boot, starting joiner\n");
        otIp6SetEnabled(instance, true);
        otJoinerStart(instance,
                      JOINER_CREDENTIAL,
                      NULL, NULL, NULL, NULL, NULL,
                      joiner_callback,
                      instance);
    }

    // app_main never returns — same pattern as the commissioner
    esp_openthread_launch_mainloop();
}