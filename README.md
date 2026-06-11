<div align="center">

<img src="https://img.shields.io/badge/ESP32-IoT-blue?style=for-the-badge&logo=espressif&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-Python-green?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/WebSocket-Real--Time-orange?style=for-the-badge&logo=socket.io&logoColor=white" />
<img src="https://img.shields.io/badge/Voice-Web%20Speech%20API-purple?style=for-the-badge&logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />

<br/><br/>

# ⚡ SmartRoom — IoT Assistive Control System

### IoT-based Lighting & Fan Control for People with Mobility Impairments

**ESP32 · Flask REST API · WebSocket · Voice Control · Emergency SOS**

[🖥️ Live Demo](#demo) · [📖 Docs](#api-endpoints) · [🚀 Quick Start](#quick-start) · [📬 Contact](#contact)

</div>

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Hardware Requirements](#hardware-requirements)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [ESP32 Setup](#esp32-setup)
- [Voice Commands](#voice-commands)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 About the Project

**SmartRoom** is an open-source IoT assistive room control system designed to empower individuals with mobility impairments, elderly users, and residents of rehabilitation facilities to independently control room appliances — without touching a physical switch.

> *"Designed with empathy, built with precision — a smart room system that adapts to the user, not the other way around."*

### 🚩 Problem
Mobility-challenged individuals struggle with conventional switches. Standard room appliances are inaccessible, fostering dependence and reducing quality of life.

### 💡 Solution
A Flask-backed IoT system that lets users control lights and fans via:
- 🖥️ **Web Dashboard** — large accessible buttons, real-time status
- 🎙️ **Voice Commands** — hands-free via Web Speech API
- 📱 **Mobile Interface** — fully responsive, touch-optimised
- 🆘 **Emergency SOS** — one tap notifies caregivers instantly

---

## ✨ Features

| Feature | Description |
|---|---|
| 💡 **Remote Light Control** | Toggle lights ON/OFF from any device on the network |
| 🌀 **Fan Speed (5 Levels)** | Smooth PWM-based fan speed adjustment (OFF, 1–5) |
| 📡 **Real-Time WebSocket Sync** | All connected clients update instantly via flask-socketio |
| 🎙️ **Voice Control** | Chrome Web Speech API — "Turn on the light", "Set fan to level 3" |
| 🚨 **Emergency SOS Alert** | Triggers WebSocket broadcast + caregiver email via Flask-Mail |
| 📊 **Action Logs** | Server-side log of last 100 actions with source attribution |
| 🌙 **Dark/Light Mode** | Full theme toggle with smooth CSS transitions |
| ♿ **Accessibility Mode** | Larger text, bigger touch targets for motor-impaired users |
| 📱 **Mobile-First Design** | Responsive layout optimised for smartphones and tablets |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER INTERFACES                    │
│  🖥️ Web Dashboard  │  🎙️ Voice  │  📱 Mobile        │
└──────────────────────────┬──────────────────────────┘
                           │  HTTP REST + WebSocket
                           ▼
┌─────────────────────────────────────────────────────┐
│              🐍 FLASK BACKEND (app.py)               │
│                                                      │
│  REST API  ──  flask-socketio  ──  flask-mail        │
│  /api/light    WebSocket broker    Email alerts      │
│  /api/fan      Real-time push      SOS dispatch      │
│  /api/sos      Multi-client sync                     │
└──────────────────────────┬──────────────────────────┘
                           │  HTTP Heartbeat (every 5s)
                           ▼
┌─────────────────────────────────────────────────────┐
│              🔌 ESP32 MICROCONTROLLER                │
│                                                      │
│   GPIO 26 ──► Relay Ch.1 ──► 💡 Room Light          │
│   GPIO 27 ──► Relay Ch.2 ──► 🌀 Ceiling Fan (PWM)   │
│   GPIO 14 ──► Push Button ──► 🆘 SOS Trigger        │
└─────────────────────────────────────────────────────┘
```

### Data Flow
1. User clicks dashboard or speaks a command
2. Browser sends `POST /api/light` or `POST /api/fan` to Flask
3. Flask updates in-memory state and broadcasts `state_update` via WebSocket
4. All browser tabs update instantly
5. ESP32 polls `/api/esp32/heartbeat` every 5s and receives target state
6. ESP32 actuates relay → physical appliance changes

---

## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![SocketIO](https://img.shields.io/badge/flask--socketio-5.3-orange)
![CORS](https://img.shields.io/badge/flask--cors-4.0-lightgrey)

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript&logoColor=black)
![SocketIO](https://img.shields.io/badge/Socket.IO-Client-black?logo=socket.io)

### Hardware
![ESP32](https://img.shields.io/badge/ESP32-DevKit_v1-red?logo=espressif)
![Arduino](https://img.shields.io/badge/Arduino-IDE-00979D?logo=arduino)

---

## 🔧 Hardware Requirements

| Component | Specification | Qty | Approx. Cost |
|---|---|---|---|
| ESP32 DevKit v1 | 240MHz, Wi-Fi 802.11 b/g/n | 1 | ₹350 |
| 4-Channel Relay Module | 5V coil, 10A/250VAC, optocoupler | 1 | ₹150 |
| 5V DC Power Supply | 2A, USB or barrel jack | 1 | ₹120 |
| Jumper Wires | Male-to-male, male-to-female | 1 set | ₹50 |
| Push Button | Momentary NO, 6×6mm | 1 | ₹10 |
| **Total** | | | **~₹680** |

### Wiring
```
ESP32 GPIO 26  ──►  Relay IN1  ──►  Light circuit
ESP32 GPIO 27  ──►  Relay IN2  ──►  Fan circuit (PWM)
ESP32 GPIO 14  ──►  Push button ──► GND  (SOS)
ESP32 GND      ──►  Relay GND
ESP32 VIN/5V   ──►  Relay VCC
```

> ⚠️ **Safety Warning:** Relay modules switch mains voltage (230V AC). Ensure proper insulation and never touch live terminals. If unsure, consult a licensed electrician.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip
- Google Chrome (for voice control)
- Arduino IDE (for ESP32 firmware)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/smartroom-iot.git
cd smartroom-iot
```

### 2. Install Python Dependencies
```bash
pip install flask flask-socketio flask-cors flask-mail python-dotenv eventlet
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
SECRET_KEY=your-random-secret-string
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
ALERT_EMAIL=caregiver@email.com
CONTACT_EMAIL=nithin.ise24@cmrit.ac.in
```

> 💡 **Gmail App Password:** Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — enable 2FA first, then generate an app password.

### 4. Run the Server
```bash
python app.py
```

Open your browser at **http://localhost:5000** 🎉

---

## 📡 API Endpoints

Base URL: `http://localhost:5000`

### Device Control

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `GET` | `/api/status` | — | Full device state + client count |
| `GET` | `/api/light` | — | Current light state |
| `POST` | `/api/light` | `{"state": true}` or `{"toggle": true}` | Set or toggle light |
| `GET` | `/api/fan` | — | Current fan speed |
| `POST` | `/api/fan` | `{"speed": 0-5}` | Set fan speed (0 = OFF) |
| `POST` | `/api/sos` | `{"triggered": true, "source": "web"}` | Trigger SOS alert |
| `POST` | `/api/esp32/heartbeat` | `{"ip": "...", "firmware": "1.0.0"}` | ESP32 liveness ping |
| `POST` | `/api/contact` | `{"name","email","subject","message"}` | Contact form email |
| `GET` | `/api/logs` | `?limit=20` | Last N action logs |
| `DELETE` | `/api/logs` | — | Clear logs |

### Example Requests

```bash
# Toggle the light
curl -X POST http://localhost:5000/api/light \
  -H "Content-Type: application/json" \
  -d '{"toggle": true}'

# Set fan to level 3
curl -X POST http://localhost:5000/api/fan \
  -H "Content-Type: application/json" \
  -d '{"speed": 3}'

# Trigger SOS
curl -X POST http://localhost:5000/api/sos \
  -H "Content-Type: application/json" \
  -d '{"triggered": true, "source": "web"}'

# Get system status
curl http://localhost:5000/api/status
```

### WebSocket Events

| Event | Direction | Description |
|---|---|---|
| `state_update` | Server → All Clients | Fired on any device state change |
| `sos_alert` | Server → All Clients | Fired when SOS is triggered |
| `client_action` | Client → Server | Send action directly over WebSocket |
| `ping_server` | Client → Server | Keep-alive probe |

---

## 🔌 ESP32 Setup

### Arduino IDE Setup
1. Install [Arduino IDE](https://www.arduino.cc/en/software)
2. Add ESP32 board: **File → Preferences → Additional Board Manager URLs:**
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. **Tools → Board → ESP32 Arduino → ESP32 Dev Module**

### Required Libraries
Install via **Sketch → Include Library → Manage Libraries:**
- `HTTPClient` (built-in with ESP32)
- `ArduinoJson` by Benoit Blanchon
- `WiFi` (built-in with ESP32)

### ESP32 Firmware (sketch)

Create a new sketch with this code:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ── Configuration ──────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.X:5000"; // Your Flask server IP

// ── GPIO Pins ──────────────────────────────
#define LIGHT_RELAY_PIN  26
#define FAN_RELAY_PIN    27
#define SOS_BUTTON_PIN   14
#define LED_PIN          2

// ── State ──────────────────────────────────
bool  lightState  = false;
int   fanSpeed    = 0;
bool  lastBtnState = HIGH;

void setup() {
  Serial.begin(115200);
  pinMode(LIGHT_RELAY_PIN, OUTPUT);
  pinMode(FAN_RELAY_PIN,   OUTPUT);
  pinMode(SOS_BUTTON_PIN,  INPUT_PULLUP);
  pinMode(LED_PIN,         OUTPUT);

  // Relays are active-LOW — HIGH = OFF
  digitalWrite(LIGHT_RELAY_PIN, HIGH);
  digitalWrite(FAN_RELAY_PIN,   HIGH);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
  digitalWrite(LED_PIN, HIGH);
}

void loop() {
  // ── Check SOS Button ──
  bool btnState = digitalRead(SOS_BUTTON_PIN);
  if (btnState == LOW && lastBtnState == HIGH) {
    triggerSOS();
    delay(200);
  }
  lastBtnState = btnState;

  // ── Heartbeat every 5 seconds ──
  sendHeartbeat();
  delay(5000);
}

void sendHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(String(SERVER_URL) + "/api/esp32/heartbeat");
  http.addHeader("Content-Type", "application/json");

  String body = "{\"ip\":\"" + WiFi.localIP().toString() + "\",\"firmware\":\"1.0.0\"}";
  int code = http.POST(body);

  if (code == 200) {
    String response = http.getString();
    StaticJsonDocument<256> doc;
    deserializeJson(doc, response);

    bool  newLight = doc["data"]["current_state"]["light"];
    int   newFan   = doc["data"]["current_state"]["fan"];

    if (newLight != lightState) {
      lightState = newLight;
      digitalWrite(LIGHT_RELAY_PIN, lightState ? LOW : HIGH);
      Serial.println("Light: " + String(lightState ? "ON" : "OFF"));
    }
    if (newFan != fanSpeed) {
      fanSpeed = newFan;
      int pwm = map(fanSpeed, 0, 5, 0, 255);
      analogWrite(FAN_RELAY_PIN, pwm);
      Serial.println("Fan: Level " + String(fanSpeed));
    }
  }
  http.end();
}

void triggerSOS() {
  Serial.println("SOS triggered!");
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/api/sos");
  http.addHeader("Content-Type", "application/json");
  http.POST("{\"triggered\":true,\"source\":\"esp32\"}");
  http.end();
}
```

> Replace `YOUR_WIFI_SSID`, `YOUR_WIFI_PASSWORD`, and the server IP with your actual values.

---

## 🎙️ Voice Commands

Open the dashboard in **Google Chrome** and click the microphone button. Supported commands:

| Say This | Action |
|---|---|
| *"Turn on the light"* | Light → ON |
| *"Turn off the light"* | Light → OFF |
| *"Set fan to level 3"* | Fan → Level 3 |
| *"Fan off"* | Fan → OFF |
| *"Turn on all"* | Light ON + Fan Level 3 |
| *"Turn off all"* | Light OFF + Fan OFF |
| *"SOS"* / *"Emergency"* / *"Help"* | SOS Alert sent |

> 🎙️ Voice control only works in **Google Chrome**. Firefox and Safari do not support the Web Speech API.

**Microphone permission denied?**
1. Click the 🔒 lock icon in the Chrome address bar
2. Set **Microphone** → **Allow**
3. Refresh the page

---

## 📁 Project Structure

```
smartroom-iot/
│
├── app.py                  # Flask backend — REST API + WebSocket
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── README.md               # This file
│
├── templates/
│   └── index.html          # Full dashboard (served by Flask)
│
├── static/                 # Optional: CSS/JS if split out
│   ├── css/
│   └── js/
│
└── esp32/
    └── smartroom.ino       # ESP32 Arduino firmware
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in your values:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Flask session secret (make it random) | `abc123xyz...` |
| `FLASK_DEBUG` | Enable debug mode | `true` |
| `PORT` | Server port | `5000` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | Your Gmail address | `you@gmail.com` |
| `MAIL_PASSWORD` | Gmail App Password | `xxxx xxxx xxxx xxxx` |
| `ALERT_EMAIL` | SOS alert recipient | `caregiver@email.com` |
| `CONTACT_EMAIL` | Contact form recipient | `nithin.ise24@cmrit.ac.in` |

> 🔒 **Never commit your `.env` file to Git.** The `.gitignore` already excludes it.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/add-temperature-sensor`
3. Commit your changes: `git commit -m "Add DHT11 temperature monitoring"`
4. Push to your branch: `git push origin feature/add-temperature-sensor`
5. Open a Pull Request

### Roadmap / Ideas
- [ ] SQLite database for persistent state and history
- [ ] JWT authentication for multi-user access
- [ ] DHT11/22 temperature & humidity monitoring
- [ ] React Native mobile app
- [ ] Docker deployment support
- [ ] HTTPS / WSS (SSL) support
- [ ] Google Home / Alexa integration

---

## 📄 License

Distributed under the MIT License.

```
MIT License — Copyright (c) 2026 Nithin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to deal in the Software without restriction, including the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software.
```

---

## 📬 Contact

**Nithin**
Department of Information Science & Engineering
CMR Institute of Technology, Bengaluru

📧 [nithin.ise24@cmrit.ac.in](mailto:nithin.ise24@cmrit.ac.in)
📞 +91 63622 18469
🔗 [github.com/YOUR_USERNAME/smartroom-iot](https://github.com/YOUR_USERNAME/smartroom-iot)

---

<div align="center">

Built with ❤️ for accessibility and independence

⭐ **Star this repo if it helped you!** ⭐

</div>
