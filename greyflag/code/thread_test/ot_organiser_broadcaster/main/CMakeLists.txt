idf_component_register(SRCS "main.c"
                        INCLUDE_DIRS "."
                        REQUIRES ieee802154 nvs_flash freertos mbedtls esp_hw_support)
