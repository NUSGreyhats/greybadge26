/*
 * OpenThread platform configuration for the GreyFlag badge.
 *
 * The ESP32-C6 has a native IEEE 802.15.4 radio, so the radio runs in
 * RADIO_MODE_NATIVE (no external RCP). Host connection is NONE (the CLI is
 * driven in-process via otCliInputLine) and OpenThread stores its dataset in
 * the "nvs" partition.
 */
#pragma once

#include "esp_openthread_types.h"

#define ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG()              \
    {                                                      \
        .radio_mode = RADIO_MODE_NATIVE,                   \
    }

#define ESP_OPENTHREAD_DEFAULT_HOST_CONFIG()               \
    {                                                       \
        .host_connection_mode = HOST_CONNECTION_MODE_NONE, \
    }

#define ESP_OPENTHREAD_DEFAULT_PORT_CONFIG()    \
    {                                           \
        .storage_partition_name = "nvs",        \
        .netif_queue_size = 10,                 \
        .task_queue_size = 10,                  \
    }
