# HA GroupAlarm API

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/GamingonTour1/ha-groupalarm-api?style=for-the-badge&color=green)](https://github.com/GamingonTour1/ha-groupalarm-api/releases)
[![GitHub Stars](https://img.shields.io/github/stars/GamingonTour1/ha-groupalarm-api?style=for-the-badge&color=yellow)](https://github.com/GamingonTour1/ha-groupalarm-api/stargazers)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

Eine Home Assistant Integration für die **GroupAlarm API**, um Alarme, Einsätze und Rückmeldungen direkt in Home Assistant zu integrieren.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GamingonTour1&repository=ha-groupalarm-api&category=plugin)
---

## ⚡ Features

- 🔔 Abruf von aktuellen GroupAlarm Einsätzen
- 📡 Automatische Aktualisierung via Coordinator (Polling)
- 🧠 Ein zentraler Sensor mit allen Alarmdaten
- 🔁 Binary Sensor für aktiven Alarmstatus
- 🧾 Vollständige Alarmdetails (Message, Event, Feedback, Resources)
- 👤 Unterstützung für Organisationen
- ⚙️ Konfiguration via UI (Config Flow)
- 🚀 HACS kompatibel

---

## ⚙️ Installation

### HACS (empfohlen)

1. HACS → Integrationen → Custom Repository hinzufügen
2. URL einfügen: https://github.com/GamingonTour1/ha-groupalarm-api
3. Kategorie: **Integration**
4. Installieren
5. Home Assistant neu starten

---

## 🔧 Konfiguration

Nach der Installation:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

Du benötigst:

- 🔑 API Token (GroupAlarm Personal Access Token)
- 🏢 Organisations-ID
- 🏷️ Organisationsname

<p align="center">
  <img src="img/setup.png" width="400">
</p>

## 🔑 GroupAlarm API Token erstellen

Für die Einrichtung der Integration benötigst du einen **Personal Access Token** aus GroupAlarm.

So erstellst du ihn:

1. Öffne https://app.groupalarm.com
2. Melde dich mit deinem Account an
3. Klicke oben rechts auf dein Profilbild
4. Öffne **Profil**
<p align="center">
  <img src="img/profile.png" width="500">
</p>
5. Wechsle zum Tab **Sicherheit**
6. Scrolle nach unten zu **API-Schlüssel**
<p align="center">
  <img src="img/API-Key.png" width="500">
</p>
7. Erstelle einen neuen Token und kopiere ihn

⚠️ Bewahre den Token sicher auf – er wird später in Home Assistant benötigt.

---

## 📊 Entitäten

### Sensor

| Entity                     | Beschreibung |
|----------------------------|-------------|
| `sensor.NAME_latest_alarm` | Hauptsensor mit allen Alarmdaten |

**Attribute enthalten:**
- message
- event
- creator
- start/end time
- alarmResources
- optionalContent
- feedback

---

### Binary Sensor

| Entity                      | Beschreibung |
|-----------------------------|-------------|
| `binary_sensor.NAME_active` | Zeigt ob aktuell ein Alarm aktiv ist |

---

## 🔐 Sicherheit

API Token wird lokal in Home Assistant gespeichert und nicht extern übertragen.

---

## 📄 License

Proprietary – All rights reserved.
