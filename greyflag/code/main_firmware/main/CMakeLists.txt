idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES
        nvs_flash
        esp_event
        esp_netif
        esp_timer
        openthread
        vfs
        driver
        esp_driver_gpio
        esp_driver_ledc
        esp_driver_i2s
        esp_driver_usb_serial_jtag
        spiffs
        log
        freertos
)
