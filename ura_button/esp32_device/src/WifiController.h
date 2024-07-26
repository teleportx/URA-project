#ifndef WIFICONTROLLER_H
#define WIFICONTROLLER_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>
#include <map>

namespace WiFiController {
    extern std::map<String, String> saved;

    void setup(AsyncWebServer *server);
    void connect();
    void handle();
}

#endif WIFICONTROLLER_H
