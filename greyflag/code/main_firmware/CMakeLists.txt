cmake_minimum_required(VERSION 3.22)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(greyflag_badge)

# Build a SPIFFS image from spiffs_data/ (the .wav samples) and flash it to the
# "storage" partition automatically on `idf.py flash`. FLASH_IN_PROJECT ties it
# into the normal flash step so no separate spiffsgen/esptool command is needed.
spiffs_create_partition_image(storage spiffs_data FLASH_IN_PROJECT)
