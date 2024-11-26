#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

//=====================================
// Pin Definitions
//=====================================
#define DHT_PIN 22   // DHT22: Temperatura ambiente
#define TRIG_PIN 5   // HC-SR04: Trigger
#define ECHO_PIN 18  // HC-SR04: Echo
#define PIR_PIN 19   // PIR: Detecção de movimento
#define LDR_PIN 34   // LDR: Nível de luz
#define LIGHT_PIN 26 // Relé para iluminação
#define FAN_PIN 27   // Relé para ventilação

// I2C Pins
#define SDA_PIN 21 // Serial Data
#define SCL_PIN 23 // Serial Clock

//=====================================
// Constants
//=====================================
#define DHT_TYPE DHT22        // Modelo do sensor DHT
#define MIN_LIGHT 10.0        // Nível mínimo de luz (%)
#define TEMP_THRESHOLD 22.0   // Temperatura limite para ventilação (°C)
#define PRESENCE_TIMEOUT 5000 // Timeout de presença (5 s)
#define LDR_SAMPLES 5         // Amostras para média do LDR

//=====================================
// Instâncias Globais
//=====================================
static DHT dht(DHT_PIN, DHT_TYPE);
static LiquidCrystal_I2C lcd(0x27, 16, 2);

//=====================================
// Estados do Sistema
//=====================================
static bool isLightActive = false;
static bool isFanActive = false;
static bool isPresenceActive = false;
static unsigned long presenceTimer = 0;
static float lastDistance = -1;

//=====================================
// Funções dos Sensores
//=====================================
float readUltrasonic()
{
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    return duration * 0.034 / 2;
}

bool readPIR()
{
    return digitalRead(PIR_PIN);
}

float readLDR()
{
    long total = 0;
    for (int i = 0; i < LDR_SAMPLES; i++)
    {
        total += analogRead(LDR_PIN);
        delay(10);
    }
    float average = total / LDR_SAMPLES;
    return (average / 4095.0) * 100;
}

//=====================================
// Controle de Dispositivos
//=====================================
void controlLight(bool active)
{
    if (isLightActive != active)
    {
        digitalWrite(LIGHT_PIN, active);
        isLightActive = active;
        Serial.printf("=== Iluminação %s ===", active ? "LIGADA" : "DESLIGADA");
        Serial.println("");
    }
}

void controlFan(bool active)
{
    if (isFanActive != active)
    {
        digitalWrite(FAN_PIN, active);
        isFanActive = active;
        Serial.printf("=== Ar Condicionado %s ===\nTemperatura: %.2f°C",
                      active ? "LIGADO" : "DESLIGADO",
                      dht.readTemperature());
        Serial.println("");
    }
}

//=====================================
// Detecção de Presença
//=====================================
void runPresenceTrigger()
{
    isPresenceActive = true;
    presenceTimer = millis(); // Reseta timer
    controlLight(true);       // Liga iluminação
}

void checkPresence(bool motion, float distance)
{
    // Detecta mudança na distância
    bool distanceChanged = false;
    if (lastDistance >= 0)
    {
        distanceChanged = abs(distance - lastDistance) > 20; // Mudança maior que 20cm
        if (distanceChanged)
        {
            Serial.printf("====== Mudança na Distância ===\nAnterior: %.2fcm\nAtual: %.2fcm", lastDistance, distance);
            Serial.println("");
        }
    }
    lastDistance = distance;

    // Verifica sensores
    if (motion || distanceChanged)
    {
        Serial.println("=== Presença Detectada ===");
        Serial.printf("Motivo: %s", motion ? "Sensor PIR" : "Mudança na Distância");
        Serial.println("");
        runPresenceTrigger();
    }

    // Verifica timeout
    if (isPresenceActive && (millis() - presenceTimer >= PRESENCE_TIMEOUT))
    {
        Serial.println("=== Timeout de Presença ===");
        Serial.println("Status: Presença Finalizada");
        Serial.println("");
        isPresenceActive = false;
    }
}

//=====================================
// Interface LCD
//=====================================
void updateLCD(float temp, float light)
{
    lcd.clear();

    if (isPresenceActive)
    {
        // Quando há presença, mostra apenas o status centralizado
        lcd.setCursor(0, 0);
        lcd.print("   Presenca");
        lcd.setCursor(0, 1);
        lcd.print("  Detectada");
    }
    else
    {
        // Sem presença, mostra todas as informações
        // Linha 1: Iluminação e Temperatura
        lcd.setCursor(0, 0);
        lcd.printf("Ilum:%s T:%.1fC", isLightActive ? "ON " : "OFF", temp);

        // Linha 2: Luz Ambiente e Ventilação
        lcd.setCursor(0, 1);
        lcd.printf("Luz:%.1f%% AC:%s", light, isFanActive ? "ON " : "OFF");
    }
}

//=====================================
// Setup
//=====================================
void setup()
{
    Serial.begin(115200);

    // Configura I2C e LCD
    Wire.begin(SDA_PIN, SCL_PIN);
    lcd.init();
    lcd.backlight();

    // Configura sensores
    dht.begin();
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(PIR_PIN, INPUT);
    pinMode(LIGHT_PIN, OUTPUT);
    pinMode(FAN_PIN, OUTPUT);

    // Estado inicial
    digitalWrite(LIGHT_PIN, LOW);
    digitalWrite(FAN_PIN, LOW);
}

//=====================================
// Loop Principal
//=====================================
void loop()
{
    // Lê sensores
    float temperature = dht.readTemperature();
    float lightLevel = readLDR();
    bool motion = readPIR();
    float distance = readUltrasonic();

    if (!isnan(temperature))
    {
        // Log periódico (a cada 1 segundos)
        static unsigned long lastLog = 0;
        if (millis() - lastLog >= 1000)
        {
            Serial.println("\n");
            Serial.println("=== Estado do Sistema ===");
            Serial.println("");
            Serial.printf("Temperatura: %.2f°C %s",
                          temperature, temperature > TEMP_THRESHOLD ? "(ALTA)" : "(NORMAL)");
            Serial.println("");
            Serial.printf("Luz Ambiente: %.2f%% %s",
                          lightLevel, lightLevel < MIN_LIGHT ? "(BAIXA)" : "(NORMAL)");
            Serial.println("");
            Serial.printf("Distância: %.2f cm",
                          distance);
            Serial.println("");
            Serial.printf("Movimento: %s",
                          motion ? "DETECTADO" : "NÃO DETECTADO");
            Serial.println("");
            Serial.printf("Presença: %s",
                          isPresenceActive ? "ATIVA" : "INATIVA");
            Serial.println("");
            Serial.printf("Iluminação: %s",
                          isLightActive ? "LIGADA" : "DESLIGADA");
            Serial.println("");
            Serial.printf("Ar Condicionado: %s",
                          isFanActive ? "LIGADO" : "DESLIGADO");
            Serial.println("");
            lastLog = millis();
        }

        // Controle de presença e iluminação
        checkPresence(motion, distance);

        // Controle automático baseado em sensores
        if (lightLevel < MIN_LIGHT)
        {
            controlLight(true);
        }
        else if (!isPresenceActive)
        {
            controlLight(false);
        }

        // Controle de ventilação
        controlFan(temperature > TEMP_THRESHOLD);

        // Atualiza interface
        updateLCD(temperature, lightLevel);
    }

    delay(500); // Delay menor para melhor responsividade
}
