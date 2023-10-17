/* Get Start Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "nvs_flash.h"

#include "esp_mac.h"
#include "rom/ets_sys.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "esp_netif.h"
#include "esp_now.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "driver/gpio.h"

#define CONFIG_LESS_INTERFERENCE_CHANNEL    11

static const uint8_t CONFIG_CSI_SEND_MAC[] = {0x1a, 0x00, 0x00, 0x00, 0x00, 0x00};
static const char *TAG = "csi_recv";
char csi_str[2000];
char pkt_str[100];
int seen_csi = 0;
int seen_pkt = 0;

// byte led_pin = 0;
typedef struct
{
    uint16_t frame_ctrl;
    uint16_t duration_id;
    uint8_t addr1[6]; // Destination MAC
    uint8_t addr2[6]; // Source MAC
    uint8_t addr3[6]; // BSSID
    uint16_t sequence_ctrl;
    uint8_t addr4[6]; // Possible fourth address
} __attribute__((packed)) ieee80211_header_t;

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

static void wifi_csi_rx_cb(void *ctx, wifi_csi_info_t *info)
{
    
    if (!info || !info->buf) 
    {
        ESP_LOGW(TAG, "<%s> wifi_csi_cb", esp_err_to_name(ESP_ERR_INVALID_ARG));
        return;
    }

    if (memcmp(info->mac, CONFIG_CSI_SEND_MAC, 6)) 
    {
        return;
    }

    static int s_count = 0;
    const wifi_pkt_rx_ctrl_t *rx_ctrl = &info->rx_ctrl;

//    if (!s_count) {
//        ESP_LOGI(TAG, "================ CSI RECV ================");
//        ets_printf("type,mac,rssi,rate,sig_mode,mcs,bandwidth,smoothing,not_sounding,aggregation,stbc,fec_coding,sgi,noise_floor,ampdu_cnt,channel,secondary_channel,local_timestamp,sig_len,rx_state,len,first_word,data\n");
//    }

    sprintf(csi_str, "CSI_DATA," MACSTR ",%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d",
            MAC2STR(info->mac), rx_ctrl->rssi, rx_ctrl->rate, rx_ctrl->sig_mode,
            rx_ctrl->mcs, rx_ctrl->cwb, rx_ctrl->smoothing, rx_ctrl->not_sounding,
            rx_ctrl->aggregation, rx_ctrl->stbc, rx_ctrl->fec_coding, rx_ctrl->sgi,
            rx_ctrl->noise_floor, rx_ctrl->ampdu_cnt, rx_ctrl->channel, rx_ctrl->secondary_channel,
            rx_ctrl->timestamp, rx_ctrl->sig_len, rx_ctrl->rx_state);

    sprintf(csi_str + strlen(csi_str), ",%d,%d,[%d", info->len, info->first_word_invalid, info->buf[0]);

    for (int i = 1; i < info->len; i++) {
        sprintf(csi_str + strlen(csi_str), ";%d", info->buf[i]);
    }
    sprintf(csi_str + strlen(csi_str), "]");

    ets_printf("%s \n", csi_str);

//  if (seen_pkt == 1) {
//        ets_printf("csi-callback, %s, %s \n", csi_str, pkt_str);
//        seen_pkt = 0;
//        seen_csi = 0;
//      } else {
//        seen_csi = 1;
//    }
}

static void wifi_sniffer_packet_handler(void *buff, wifi_promiscuous_pkt_type_t type)
{
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buff;

    ieee80211_header_t *hdr = (ieee80211_header_t *)pkt->payload;

    // Compare the source MAC address
    if (memcmp(hdr->addr2, CONFIG_CSI_SEND_MAC, 6) == 0)
    {
        sprintf(pkt_str, "PKT_ID, %d, %d", pkt->payload[39], pkt->payload[40]);
    }
    ets_printf("%s \n", pkt_str);

//     if (seen_csi == 1){
//      ets_printf("Sniffer, %s, %s \n", csi_str, pkt_str);
//      seen_pkt = 0;
//      seen_csi = 0;
//    } else {
//      seen_pkt = 1;
//    }
}

static void wifi_csi_init()
{
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    // ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(g_wifi_radar_config->wifi_sniffer_cb));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&wifi_sniffer_packet_handler));

    /**< default config */
    wifi_csi_config_t csi_config = {
        .lltf_en           = true,
        .htltf_en          = true,
        .stbc_htltf2_en    = true,
        .ltf_merge_en      = true,
        .channel_filter_en = true,
        .manu_scale        = false,
        .shift             = false,
    };
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(wifi_csi_rx_cb, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}

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
//     gpio_config_t io_conf2;

//     // Set pins as output mode and without internal pull-up resistors
//     io_conf2.mode = GPIO_MODE_OUTPUT;
//     io_conf2.pin_bit_mask = ((1ULL << 1) | (1ULL << 7) | (1ULL << 8) |
//                             (1ULL << 2) | (1ULL << 4) | (1ULL << 5) |
//                             (1ULL << 6));
    
//     io_conf2.pull_down_en = 0;
//     io_conf2.pull_up_en = 0;
//     io_conf2.intr_type = GPIO_INTR_DISABLE;

//     gpio_config(&io_conf2);

    gpio_set_direction(GPIO_NUM_1, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_4, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_5, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_6, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_7, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_NUM_8, GPIO_MODE_OUTPUT);


    // default, set TX and RX to their own chip antennas
    // esptx_set_independent_antenna(false, false);    //  
    esptx_set_independent_antenna(true,true);

    //  esptx_disconnect_txrx_wiwi();

    // WiFi.mode(WIFI_STA);
    // WiFi.disconnect();
    // delay(100);
}

void app_main()
{
    // gpio_config_t io_conf;
    // // Configure pins 36 and 37 as input
    // io_conf.mode = GPIO_MODE_INPUT;
    // io_conf.pin_bit_mask = ((1ULL << 36) | (1ULL << 37));
    // io_conf.pull_up_en = 0;   // You can change this based on requirements
    // io_conf.pull_down_en = 0; // You can change this based on requirements
    // io_conf.intr_type = GPIO_INTR_DISABLE;
    // gpio_config(&io_conf);

    gpio_set_direction(GPIO_NUM_36, GPIO_MODE_INPUT);
    gpio_set_direction(GPIO_NUM_37, GPIO_MODE_INPUT);
    //Initialize NVS

    if (!gpio_get_level(36) && !gpio_get_level(37))
    {
        esptx_setup();
        ets_printf("\n**********   This is TX ESP   ***********\n");
    }
    else if (gpio_get_level(36) && !gpio_get_level(37))
    {
        ets_printf("\n**********   This is RX ESP   ***********\n");
    }

        esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    wifi_init();
    wifi_csi_init();
}
