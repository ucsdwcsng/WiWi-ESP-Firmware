/* Get Start Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "nvs_flash.h"
#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "esp_netif.h"
#include "esp_now.h"
#include "driver/gpio.h"
#include "esp_system.h"
#include "nvs_flash.h" 
#include "esp_system.h"

#define CONFIG_LESS_INTERFERENCE_CHANNEL    11
#define CONFIG_SEND_FREQUENCY               1000  // Hz
#define CONFIG_NUM_PKTS_BURST               10
#define CONFIG_INTERBURST_INTERVAL          1  // sec

static const uint8_t CONFIG_CSI_SEND_MAC[] = {0x1a, 0x00, 0x00, 0x00, 0x00, 0x00};
static const char *TAG = "csi_send";

static void wifi_init()
{
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    ESP_ERROR_CHECK(esp_netif_init());
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_bandwidth(ESP_IF_WIFI_STA, WIFI_BW_HT40));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_ERROR_CHECK(esp_wifi_config_espnow_rate(ESP_IF_WIFI_STA, WIFI_PHY_RATE_MCS0_SGI));
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));

    ESP_ERROR_CHECK(esp_wifi_set_channel(CONFIG_LESS_INTERFERENCE_CHANNEL, WIFI_SECOND_CHAN_BELOW));
    ESP_ERROR_CHECK(esp_wifi_set_mac(WIFI_IF_STA, CONFIG_CSI_SEND_MAC));
}

void esptx_set_independent_antenna(bool tx_sma, bool rx_sma)
{

    // turn off attenuators
    gpio_set_level(1, 1);
    // select TX path
    gpio_set_level(7, 1);
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

    // esptx_set_independent_antenna(false, false); 
     esptx_set_independent_antenna(true,true);
}


void app_main(){
  gpio_set_direction(GPIO_NUM_36, GPIO_MODE_INPUT);
  gpio_set_direction(GPIO_NUM_37, GPIO_MODE_INPUT);

  if (!gpio_get_level(36) && !gpio_get_level(37))
  {
    esptx_setup();
    printf("\n**********   This is TX ESP   ***********\n");
  }
  else if (gpio_get_level(36) && !gpio_get_level(37))
  {
    printf("\n**********   This is RX ESP   ***********\n");
  }

  /**
   * @breif Initialize NVS
   */
  esp_err_t ret = nvs_flash_init();
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
  {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /**
     * @breif Initialize Wi-Fi
     */
    wifi_init();

    /**
     * @breif Initialize ESP-NOW
     *        ESP-NOW protocol see: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_now.html
     */
    ESP_ERROR_CHECK(esp_now_init());
    ESP_ERROR_CHECK(esp_now_set_pmk((uint8_t *)"pmk1234567890123"));

    esp_now_peer_info_t peer = {
        .channel = CONFIG_LESS_INTERFERENCE_CHANNEL,
        .ifidx = WIFI_IF_STA,
        .encrypt = false,
        .peer_addr = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff},
    };
    ESP_ERROR_CHECK(esp_now_add_peer(&peer));

    ESP_LOGI(TAG, "================ CSI SEND ================");
    ESP_LOGI(TAG, "wifi_channel: %d, send_frequency: %d, mac: " MACSTR,
             CONFIG_LESS_INTERFERENCE_CHANNEL, CONFIG_SEND_FREQUENCY, MAC2STR(CONFIG_CSI_SEND_MAC));

    u_int32_t pktid = 0;
    while (true) {
      for (uint32_t count = 0; count < CONFIG_NUM_PKTS_BURST; ++count) {
        esp_err_t ret = esp_now_send(peer.peer_addr, &pktid, sizeof(uint32_t));

        if (ret != ESP_OK) {
          ESP_LOGW(TAG, "<%s> ESP-NOW send error", esp_err_to_name(ret));
        }
        pktid += 1;
        usleep(1000 * 1000 / CONFIG_SEND_FREQUENCY);
        ESP_LOGI(TAG, "packet id: %lu", pktid);

      }
      usleep(1000000 * CONFIG_INTERBURST_INTERVAL);
    }
}
