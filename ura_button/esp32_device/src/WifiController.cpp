#include "WifiController.h"
#include "IterablePreferences.h"

#include <ArduinoJson.h>
#include <AsyncJson.h>
#include <nvs.h>
#include <Preferences.h>
#include <WiFiMulti.h>

using namespace WiFiController;

std::map<String, String> WiFiController::saved;
String available;

Preferences preferences;

WiFiMulti wifiMulti;

void get_available(AsyncWebServerRequest *request) {
    request->send(200, "application/json", available);
}

void get_saved(AsyncWebServerRequest *request) {
    JsonDocument payload;
    JsonArray array = payload.to<JsonArray>();

    for (const auto& [k, v] : saved) {
        JsonDocument now;
        now["ssid"] = k;
        now["password"] = v;
        array.add(now);
    }

    String data_s;
    serializeJson(payload, data_s);

    request->send(200, "application/json", data_s);
}


void add_saved(AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
    JsonDocument json;
    DeserializationError err = deserializeJson(json, data);
    if (err) {
        request->send(400, "application/json", R"({"detail": "Invalid json"})");
        return;
    }

    if (saved.size() >= 30) {
        request->send(400, "application/json", R"({"detail": "Cannot add more than 30 wifi networks"})");
        return;
    }

    if (not json["ssid"].is<String>()) {
        request->send(400, "application/json", R"({"detail": "Invalid ssid field type"})");
        return;
    }

    if (json["ssid"].as<String>().length() > 128) {
        request->send(413, "application/json", R"({"detail": "Len of ssid cannot be more than 128"})");
        return;
    }

    if (not json["password"].is<String>()) {
        request->send(400, "application/json", R"({"detail": "Invalid password field type"})");
        return;
    }

    if (json["password"].as<String>().length() > 128) {
        request->send(413, "application/json", R"({"detail": "Len of pass cannot be more than 128"})");
        return;
    }

    saved[json["ssid"]] = json["password"].as<String>();
    preferences.putString(json["ssid"], json["password"].as<String>());

    request->send(204);
}

void delete_saved(AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
    JsonDocument json;
    DeserializationError err = deserializeJson(json, data);
    if (err) {
        request->send(400, "application/json", R"({"detail": "Invalid json"})");
        return;
    }

    if (not json["ssid"].is<String>()) {
        request->send(400, "application/json", R"({"detail": "Invalid ssid field type"})");
        return;
    }

    if (json["ssid"].as<String>().length() > 128) {
        request->send(413, "application/json", R"({"detail": "Len of ssid cannot be more than 128"})");
        return;
    }

    if (saved.count(json["ssid"]) == 0) {
        request->send(404, "application/json", R"({"detail": "Can't find saved wifi with provided ssid"})");
        return;
    }

    saved.erase(json["ssid"].as<String>());
    preferences.remove(json["ssid"]);

    request->send(204);
}


void WiFiController::setup(AsyncWebServer *server) {
    WiFi.mode(WIFI_STA);

    // scan wifis
    int n = WiFi.scanNetworks();

    JsonDocument payload;
    JsonArray array = payload.to<JsonArray>();

    for (int i = 0; i < n; ++i) {
        JsonDocument now;
        now["ssid"] = WiFi.SSID(i);
        now["rssi"] = WiFi.RSSI(i);
        array.add(now);
    }

    serializeJson(payload, available);

    // Begining preferences
    preferences.begin("wifi", false);

    IterablePreferences prefs;
    prefs.foreach ("wifi", [](const char* key, nvs_type_t type) {
        saved[key] = preferences.getString(key);
    });
    prefs.end();

    // Registering endpoints
    server->on("/wifi/available/", HTTP_GET, get_available);
    server->on("/wifi/", HTTP_GET, get_saved);
    server->on("/wifi/", HTTP_POST, [](AsyncWebServerRequest *){}, nullptr, add_saved);
    server->on("/wifi/", HTTP_DELETE, [](AsyncWebServerRequest *){}, nullptr, delete_saved);

    // Connecting Wifi
    for (const auto& [k, v] : saved) {
        wifiMulti.addAP(k.c_str(), v.c_str());
    }

    connect();
}

constexpr long long INF = 1e18;
constexpr long long waiting_network = 30000;
long long last_not_connected = INF;

void WiFiController::connect() {
    if (wifiMulti.run() == WL_CONNECTED) {
        last_not_connected = INF;

        Serial.println("Wifi connected");
        Serial.println(WiFi.SSID());
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());

    } else {
        if (last_not_connected == INF) {
            last_not_connected = millis();
        }

        if ((millis() - last_not_connected) >= waiting_network) {
            Serial.println("Can't connect to Wifi. Starting AP...");

            WiFi.disconnect();
            WiFi.mode(WIFI_AP);
            WiFi.softAP("URA_BUTTON", "aboba123");

            IPAddress ip(192, 168, 1, 1);    //setto IP Access Point same as gateway
            IPAddress mask(255, 255, 255, 0);
            WiFi.softAPConfig(ip, ip, mask);

            Serial.print("Set IP: ");
            Serial.println(ip);

        } else {
            Serial.print("Can't connect to Wifi. Starting AP in ");
            Serial.print(waiting_network - ((millis() - last_not_connected)));
            Serial.println("ms");
        }
    }
}

void WiFiController::handle() {
    if (WiFi.getMode() != WIFI_MODE_AP and not WiFi.isConnected()) {
        Serial.println("Lost WiFi connection");
        connect();
    }
}


