#include <Arduino.h>
#include <Bounce2.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

#include "WifiController.h"

namespace PIN {
    constexpr unsigned int BUTTON_1 = 33;
    constexpr unsigned int BUTTON_2 = 25;
    constexpr unsigned int BUTTON_3 = 26;

    constexpr unsigned int LED_1 = 12;
    constexpr unsigned int LED_2 = 14;
    constexpr unsigned int LED_3 = 27;
}

Bounce2::Button button1 = Bounce2::Button();
Bounce2::Button button2 = Bounce2::Button();
Bounce2::Button button3 = Bounce2::Button();

AsyncWebServer webServer(80);

void setup() {
    pinMode(PIN::LED_1, OUTPUT);
    pinMode(PIN::LED_2, OUTPUT);
    pinMode(PIN::LED_3, OUTPUT);

    Serial.begin(115200);

    button1.attach(PIN::BUTTON_1, INPUT_PULLUP);
    button1.interval(5);
    button1.setPressedState(false);

    button2.attach(PIN::BUTTON_2, INPUT_PULLUP);
    button2.interval(5);
    button2.setPressedState(false);

    button3.attach(PIN::BUTTON_3, INPUT_PULLUP);
    button3.interval(5);
    button3.setPressedState(false);

    WiFiController::setup(&webServer);

    webServer.begin();
}

void loop() {
    WiFiController::handle();
}