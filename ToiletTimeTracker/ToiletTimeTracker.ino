#if defined(ESP8266)
  #include <ESP8266WiFi.h>
#else
 #include <WiFi.h>
#endif

#include <MySQL.h>
#include "secrets.h"

WiFiClient client;
MySQL sql(&client, dbHost, dbPort);
#define MAX_QUERY_LEN 512

const char* toilet_table = "toilet";
const char* device_param_table = "device_specific_parameters";


#if CONFIG_IDF_TARGET_ESP32 // ESP32/PICO-D4
#include "esp32/rom/rtc.h"
#elif CONFIG_IDF_TARGET_ESP32S2
#include "esp32s2/rom/rtc.h"
#elif CONFIG_IDF_TARGET_ESP32C2
#include "esp32c2/rom/rtc.h"
#elif CONFIG_IDF_TARGET_ESP32C3
#include "esp32c3/rom/rtc.h"
#elif CONFIG_IDF_TARGET_ESP32S3
#include "esp32s3/rom/rtc.h"
#elif CONFIG_IDF_TARGET_ESP32C6
#include "esp32c6/rom/rtc.h"
#elif CONFIG_IDF_TARGET_ESP32H2
#include "esp32h2/rom/rtc.h"
#else
#error Target CONFIG_IDF_TARGET is not supported
#endif

int ledPin = 2;                 // choose the pin for the LED
int inputPin = 13;              // choose the input pin (for PIR sensor)
int pirState = LOW;             // we start, assuming no motion detected
int val = 0;                    // variable for reading the pin status
unsigned long c_time, c_time_start;
unsigned long delay_value = 0;

static const char insertToiletQuery[] PROGMEM = R"string_literal(
INSERT INTO `%s`
  (`mac_addr`, `duration`, `toilet_id`)
  VALUES ('%s', '%lu', '%lu');
)string_literal";


static const char insertParamQuery[] PROGMEM = R"string_literal(
INSERT INTO `%s`
  (`mac_addr`, `delay_value`)
  VALUES ('%s', '%lu');
)string_literal";

static const char updateParamQuery[] PROGMEM = R"string_literal(
UPDATE `%s` SET
  delay_value = '%lu'
  WHERE mac_addr = '%s';
)string_literal";

static const char selectParamQuery[] PROGMEM = R"string_literal(
SELECT
  `mac_addr`,
  `delay_value`
  FROM %s
  WHERE mac_addr = '%s'
  ORDER BY id DESC LIMIT 1;
)string_literal";


// Variadic function that will execute the query selected with passed parameters
bool queryExecute(DataQuery_t& data, const char* queryStr, ...) {
  if (sql.connected()) {
    char buf[MAX_QUERY_LEN];
    va_list args;
    va_start (args, queryStr);
    vsnprintf (buf, sizeof(buf), queryStr, args);
    va_end (args);

    Serial.printf("Executing SQL query: %s\n", buf);
    // Execute the query
    return sql.query(data, buf);
  }
  return false;
}

int insert_or_update_delay_value_for_this_device(const char* mac_addr, int delay) {
    DataQuery_t data;

    if (queryExecute(data, selectParamQuery, device_param_table, mac_addr)) {
      Serial.println("selectParamQuery executed.");
      if (data.recordCount) {
        // Print formatted content of table
        sql.printResult(data);
        Serial.print('\n');
        Serial.print("delay in db = ");
        Serial.println(data.getRowValue(0, "delay_value"));

        //update
        if (delay != atoi(data.getRowValue(0, "delay_value"))) {
          if (queryExecute(data, updateParamQuery, device_param_table, delay, mac_addr)) {
            Serial.print("updateParamQuery executed. New Param added: mac_addr=");
            Serial.print(mac_addr);
            Serial.print(" delay=");
            Serial.println(delay);
          }
        }
        else {
          Serial.println("same delay value, don't need to update again.");
        }

      }
    }
    else
    {
      //insert
      Serial.print("Param not existed for device: ");
      Serial.println(mac_addr);

      if (queryExecute(data, insertParamQuery, device_param_table,
          WiFi.macAddress().c_str(),
          delay)
      )
      {
        Serial.print("insertParamQuery executed. New Param added: mac_addr=");
        Serial.print(mac_addr);
        Serial.print(" delay=");
        Serial.println(delay);
      }
      Serial.println();

    }

    Serial.print('\n');
    return delay;
}

int get_delay_value_from_db(const char* mac_addr) {
    DataQuery_t data;
    int delay = 0;
    if (queryExecute(data, selectParamQuery, device_param_table, mac_addr)) {
      if (data.recordCount) {
        Serial.print("delay_value = ");
        Serial.println(data.getRowValue(0, "delay_value"));
        delay = atoi(data.getRowValue(0, "delay_value"));
      }
    }
    return delay;
}

void setup() {
  Serial.begin(115200);
  Serial.println("******************************************************");
  Serial.print("Connecting to WiFI");

  WiFi.begin(ssid, wifiPwd);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected, IP address: ");
  Serial.println(WiFi.localIP());

  //Open MySQL session
  Serial.print("Connecting to ");
  Serial.println(dbHost);

	if (sql.connect(user, password, database)) {
    Serial.println();
  }

  Serial.println();
  delay(2000);

  //update delay value once, and comment it after it take effect.
  //insert_or_update_delay_value_for_this_device(WiFi.macAddress().c_str(), 0);

  //get delay value from db.
  delay_value = get_delay_value_from_db(WiFi.macAddress().c_str());

  pinMode(ledPin, OUTPUT);      // declare LED as output
  pinMode(inputPin, INPUT);     // declare sensor as input

}

void loop() {
  DataQuery_t data;
  val = digitalRead(inputPin);  // read input value
  
  if (val == HIGH)	// check if the input is HIGH
  {            
    digitalWrite(ledPin, HIGH);  // turn LED ON
    if (pirState == LOW) 
	  {
      c_time_start = millis();
      Serial.print("Motion detected! current time:");	// print on output change
      Serial.println(c_time_start);	// print on output change
      pirState = HIGH;
    }
  } 
  else 
  {
    digitalWrite(ledPin, LOW); // turn LED OFF
    if (pirState == HIGH)
	  {
      c_time = millis();
      Serial.print("Motion ended! duration=");	// print on output change
      unsigned long duration;
      if  (c_time - c_time_start < delay_value){
        duration = 0;
      }
      else {
        duration = c_time - c_time_start - delay_value;
      }
      Serial.println(duration);	// print duration

      if (queryExecute( data, insertToiletQuery, toilet_table,
          WiFi.macAddress().c_str(),
          duration,
          toilet_id)
         )
      {
        Serial.println("INSERT query executed. New record added to toilet_table");
      }
      pirState = LOW;
    }
  }
}
