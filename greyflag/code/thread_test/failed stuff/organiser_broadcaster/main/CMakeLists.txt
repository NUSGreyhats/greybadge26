idf_component_register(SRCS "main.c"
                        INCLUDE_DIRS "."
                        REQUIRES esp_ieee802154 nvs_flash mbedtls freertos)
