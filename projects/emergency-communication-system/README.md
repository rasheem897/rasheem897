# Emergency Communication System for Remote Regions

**Academic team project | May 2025**  
**Focus:** Embedded systems, long-range wireless communication and emergency alerting

## Overview

This project explores a low-power emergency communication system for remote areas where cellular coverage is unreliable or unavailable. The design separates the user-operated transmitter from a stationary receiver: an emergency button press triggers an ESP32-based device to send an alert over LoRa, and the receiver can relay an SMS alert through a GSM module.

The report also describes user feedback through an OLED display and a two-way acknowledgement concept.

## Problem being addressed

People in remote, mountainous or rural locations may not be able to depend on ordinary cellular calls. The report positions LoRa as the local long-range link between the wearable transmitter and a receiver, with GSM/SMS used by the receiver to notify configured contacts.

## Proposed system flow

1. The user presses the emergency push button on the transmitter.
2. The transmitter ESP32 processes the event and prepares the alert/location payload.
3. A LoRa radio link carries the payload to a stationary receiver.
4. The receiver ESP32 parses the received packet.
5. A GSM module is instructed to send an SMS alert to configured phone numbers.
6. The transmitter OLED and receiver-side display provide status feedback; a receiver acknowledgement back to the transmitter is described as a two-way feedback mechanism.

## Components and tools described in the report

| Component / tool | Purpose in the proposed system |
|---|---|
| ESP32 microcontrollers | Control and processing in transmitter and receiver |
| LoRa transceiver modules | Long-range, low-power communication between the two units |
| GSM module | SMS alert delivery from the receiver |
| Push button | User-triggered emergency event |
| OLED display | Transmitter status and feedback |
| LCD/display at receiver | Local received-alert information, as shown in the architecture description |
| Lithium battery | Wearable transmitter power source |
| Embedded C and Arduino IDE | Firmware development approach described in the report |

## Engineering topics covered

- Two-unit transmitter/receiver architecture
- Embedded microcontroller input handling
- LoRa packet transmission and reception
- GSM modem control for SMS alerts
- Location payload handling
- Display-based status feedback
- Power consumption and battery-life considerations
- Security and privacy considerations for location data

## Important implementation notes

The academic report is not fully consistent on some implementation details. These are documented here rather than treated as settled facts:

- **Location source:** the abstract refers to RSSI-based location data, while the architecture and detailed operation discuss GPS coordinates and describe GPS as potentially included. RSSI is a signal-strength measurement, not itself a GPS coordinate. The final location-acquisition method needs confirmation from the firmware/hardware.
- **Mobile app and cloud:** the abstract describes cloud storage and a connected mobile application, but the detailed report keeps several app, cloud and continuous-tracking behaviors at a high level. The supplied report does not include app source code, backend code or API specifications.
- **Acknowledgement:** two-way acknowledgement is described as a feature, but the packet format, retry behavior and failure handling are not specified in enough detail to reproduce it.
- **Measured performance:** the report does not provide a verified LoRa range test, message-delivery latency, packet-loss rate or measured battery runtime.

## Security and future work

The report identifies encryption of LoRa/SMS location data, secure cloud handling, clearer data-retention policies, more complete GPS integration, power optimization, and backup communication paths as areas requiring further work.

## Repository status

This page is based on the submitted academic project report. The report PDF is not published here because it contains student identifiers and other academic-personal details. Firmware, wiring diagrams, component part numbers, build instructions and test logs have not yet been supplied for this repository. Add verified source files and measured test results before presenting this as a reproducible build.

## Team and contribution

The report presents this as a team project but does not provide a reliable task-by-task breakdown of each member's individual contribution. Personal ownership should be added only after the actual work split is confirmed.

## Safety note

This is an academic prototype/concept, not a certified emergency communications product or a replacement for local emergency services.
