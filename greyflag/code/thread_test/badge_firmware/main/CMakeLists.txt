idf_component_register(SRCS "main.c"
                        INCLUDE_DIRS "."
                        REQUIRES openthread nvs_flash esp_netif esp_event)
