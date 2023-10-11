/*
 * SPDX-FileCopyrightText: 2010-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */

#include <stdio.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "driver/gpio.h"

/********** RF Switch path controls

RX Attenuator -> Controlled by ESPTX GPIO1 : default is low (max attenuation) , set high for zero attenuation
SW1 , ESPTX select -> Controlled by ESPTX GPIO7 : high for RF1 path (TX own antenna), low for RF2 path (WiWi path)
SW2 , ESPTX own antenna select -> Controlled by ESPTX GPIO8 / GPIO2: low/low for off , high/low for RF1 (SMA) , low/high for RF2 (Chip antenna on board)
SW3 , WiWi antenna select -> Controlled by ESPTX GPIO4 / GPIO5: low/low for off, high/low for RF1 (SMA) , low/high for RF2 (chip antenna on board)
SW4 , TX to WiWi or RX to WiWi -> Controlled by ESPTX GPIO6: high for output1 (TX), low for output2 (RX)

*********/

void esptx_set_independent_antenna(bool tx_sma, bool rx_sma)
{

    // turn off attenuators
    gpio_set_level(1, 1);
    // select TX path
    gpio_set_level(7, 1); //SW1
    // select TX antenna
    if (tx_sma)
    {
        gpio_set_level(8, 1);
        gpio_set_level(2, 0);
    }
    else
    {
        gpio_set_level(8, 0);
        gpio_set_level(2, 1);
    }
    // select WiWi (in this case RX) antenna
    if (rx_sma)
    {
        gpio_set_level(4, 1);
        gpio_set_level(5, 0);
    }
    else
    {
        gpio_set_level(4, 0);
        gpio_set_level(5, 1);
    }
    // select RX to WiWi antenna
    gpio_set_level(6, 0);
}

void esptx_setup()
{

    gpio_set_direction(GPIO_NUM_1, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_4, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_5, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_6, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_7, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_8, GPIO_MODE_OUTPUT);

    // default, set TX and RX to their own chip antennas
    // esptx_set_independent_antenna(false, false); //
    esptx_set_independent_antenna(true,true);

}

void app_main(void)
{

    gpio_set_direction(GPIO_NUM_36, GPIO_MODE_INPUT);
    gpio_set_direction(GPIO_NUM_37, GPIO_MODE_INPUT);
    // Initialize NVS

    if (!gpio_get_level(36) && !gpio_get_level(37))
    {
        esptx_setup();
        printf("\n**********   This is TX ESP   ***********\n");
    }
    else if (gpio_get_level(36) && !gpio_get_level(37))
    {
        printf("\n**********   This is RX ESP   ***********\n");
    }

    printf("Hello world!\n");

    /* Print chip information */
    esp_chip_info_t chip_info;
    uint32_t flash_size;
    esp_chip_info(&chip_info);
    printf("This is %s chip with %d CPU core(s), %s%s%s%s, ",
           CONFIG_IDF_TARGET,
           chip_info.cores,
           (chip_info.features & CHIP_FEATURE_WIFI_BGN) ? "WiFi/" : "",
           (chip_info.features & CHIP_FEATURE_BT) ? "BT" : "",
           (chip_info.features & CHIP_FEATURE_BLE) ? "BLE" : "",
           (chip_info.features & CHIP_FEATURE_IEEE802154) ? ", 802.15.4 (Zigbee/Thread)" : "");

    unsigned major_rev = chip_info.revision / 100;
    unsigned minor_rev = chip_info.revision % 100;
    printf("silicon revision v%d.%d, ", major_rev, minor_rev);
    if(esp_flash_get_size(NULL, &flash_size) != ESP_OK) {
        printf("Get flash size failed");
        return;
    }

    printf("%" PRIu32 "MB %s flash\n", flash_size / (uint32_t)(1024 * 1024),
           (chip_info.features & CHIP_FEATURE_EMB_FLASH) ? "embedded" : "external");

    printf("Minimum free heap size: %" PRIu32 " bytes\n", esp_get_minimum_free_heap_size());

    for (int i = 10; i >= 0; i--) {
        printf("Restarting in %d seconds...\n", i);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
    // printf("Restarting now.\n");
    // fflush(stdout);
    // esp_restart();
}
