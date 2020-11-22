#include <PubSubClient.h>
#include <WiFi.h>

// =============== Identifier ===============

const char* ssid = "Manee3.1";
const char* wifi_password = "20202020";

const char* mqtt_server = "192.168.68.103";
const char* mqtt_user = "user";
const char* mqtt_pass = "pass";
const char* clientID = "2";
char id = '2';

const char* mqtt_topic = "tar2cpu";

// =============== Initializations ===============

int active = 0;
float timer = 0;
float dur = 0;
int wasOn = 0;

const int buttonPin = 0;
const int ledPin = 2;

WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, wifiClient);

// =============== Message Structs ===============

// Structure of payload sent to CPU
typedef struct struct_t2c {
  char deviceID;
  short points;
} payload_t2c;
payload_t2c msg;


// Structure of payload received from CPU
typedef struct struct_c2t {
  char deviceID;
  float dur;
  short active;
} payload_c2t;
payload_c2t cmd;

// =============== Callback Functions ===============

void on_receive(char* topic, byte* payload, unsigned int length) {

  // Report received payload
  Serial.print("Length:\t\t");
  Serial.println(length);
  memcpy(&cmd, payload, length);
  Serial.print("Device ID:\t");
  Serial.println(cmd.deviceID);
  Serial.print("Duration:\t");
  Serial.println(cmd.dur);
  Serial.print("Status:\t\t");
  Serial.println(cmd.active);

  // Turn device on if deviceID matches
  if (cmd.deviceID == id || cmd.deviceID == 'A') {
    active = cmd.active;
    timer = cmd.dur;
    dur = timer;
    if (active == 1) {
      digitalWrite(ledPin, HIGH);
    }
    else {
      digitalWrite(ledPin, LOW);
    }
  }
  
}

// =============== Setup ===============

void setup() {

  // Declare pin modes
  pinMode(buttonPin, INPUT);
  pinMode(ledPin, OUTPUT);

  // Begin serial for debugging
  Serial.begin(115200);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to WiFi
  WiFi.begin(ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Connect to the MQTT broker
  if (client.connect(clientID, mqtt_user, mqtt_pass)) {
    Serial.println("Connected to MQTT broker");
  }
  else {
    Serial.println("Connection to MQTT broker failed...");
    return;
  }

  // Subscribe to topic "cpu2tar" and attach callback function
  client.subscribe("cpu2tar");
  client.setCallback(on_receive);

  // Set deviceID
  msg.deviceID = id;

}

// =============== Loop ===============

void loop() {

  // Start client listening loop
  client.loop();

  if (active == 1) {

    // Change wasOn to 1
    wasOn = 1;

    // Run down 'timer' when LED is on
    timer -= 1;
    delay(1);
    

    // Send packet hit when target is hit while active
    if (!digitalRead(buttonPin)) {

      // Compute points earned
      short points = (short) ((pow(timer, 2) / pow(dur, 2)) * 100);
      msg.points = points;

      // Publish packet to the broker
      Serial.println("Target hit");
      if (client.publish(mqtt_topic, (byte*) &msg, 4)) {
        Serial.println("Packet sent successfully");
        digitalWrite(ledPin, LOW);
        active = 0;
        timer = 0; dur = 0;
      }
      else {
        Serial.println("Message failed to send. Reconnecting to MQTT Broker...");
        client.connect(clientID, mqtt_user, mqtt_pass);
      }

      // Delay 500ms
      delay(500);

    }
  }

  if (active == 0) {

    // Send packet penalty when target is hit while inactive
    if (!digitalRead(buttonPin)) {

      // Deduct 5 points
      msg.points = -5;

      // Publish packet to the broker
      Serial.println("Target penalty");
      if (client.publish(mqtt_topic, (byte*) &msg, 4)) {
        Serial.println("Packet sent successfully");
        digitalWrite(ledPin, LOW);
        active = 0;
        timer = 0; dur = 0;
      }
      else {
        Serial.println("Message failed to send. Reconnecting to MQTT Broker...");
        client.connect(clientID, mqtt_user, mqtt_pass);
      }

      // Delay 500ms
      delay(500);

    }
  }

  // Turn LED off when timer runs out
  if (timer == 0) {
    if (wasOn == 1) {
      msg.points = 0;
      client.publish(mqtt_topic, (byte*) &msg, 4);
      wasOn = 0;
    }
    digitalWrite(ledPin, LOW);
    active = 0;
    dur = 0;
  }
  
}
