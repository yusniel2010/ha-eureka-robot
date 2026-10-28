# Eureka Robot (Local)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yusniel2010&repository=ha-eureka-robot&category=integration)
[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=eureka_robot)

Local Home Assistant integration for **Eureka J15 Pro Ultra (750Y000R)**. Connects directly to TCP **12127**. No Eureka account, cloud, tokens or Python runtime dependencies.

**Experimental v0.2.0.** The transport and some commands were tested on a real robot during research. Additional commands come from the official J15 control panel's protocol tables and encoder functions. This build passes simulator, Home Assistant and browser tests; the new controls still need physical local-transport validation. Other models are unsupported.

## Installation

Requires **Home Assistant 2025.12+**; tested with **2026.2.3**. HACS must already be installed. Home Assistant must reach the robot's TCP port 12127.

1. Click **Open in HACS** above. Add the custom integration repository when prompted and download it.
2. Restart Home Assistant.
3. Click **Add integration** above, or open Settings → Devices & services → Add integration → **Eureka Robot (Local)**.
4. Choose **Search local network** or **Enter IP manually**.

The first badge opens the repository in HACS; it does not silently install files or bypass the restart. The second starts configuration after installation. If your browser asks for your Home Assistant URL, enter your usual HA address.

Manual alternative: copy `custom_components/eureka_robot` to `/config/custom_components/eureka_robot`, restart and add the integration. Remove it through Devices & services; uninstall its files through HACS if no longer needed.

## How local discovery works

Discovery is started explicitly from the integration's setup menu. It does not run continuously in the background.

- Defaults to a `/24` subnet around an enabled Home Assistant IPv4 interface. You can edit it, for example `192.168.1.0/24`.
- Scans only private IPv4 ranges (`10.x`, `172.16–31.x`, `192.168.x`), at most **256 addresses**, with **16 concurrent** short probes.
- Sends only the read-only B8 status query on TCP 12127; an open port alone is insufficient.
- Lists devices returning a valid checksummed B8 status frame. This confirms protocol compatibility, **not exact model identity**: confirm that the selected address belongs to your J15 Pro Ultra before adding it.
- Already configured IPs are filtered. Cancelling setup cancels pending probes.

The robot did not advertise an mDNS/Matter service during research, so this integration does not claim automatic mDNS discovery. If the robot is on another VLAN, choose its reachable subnet or enter its IP manually. A sleeping robot, port contention, firewall or a slow response may cause a missed scan; manual setup uses longer retries.

Reserve the robot's IP in the router. Use **Reconfigure** to change it later; entity/device IDs are preserved. Duplicate detection uses the configured host because a local serial-number query is not available. Avoid adding the same robot under a second hostname.

## Controls and evidence

All controls below are connected to standard HA entities and the bundled card.

| Function | Source / B8 body | Exposure |
|---|---|---|
| Status and battery | Captured and queried locally: `aa 01 01` | Vacuum, sensors |
| Pause / stop | Captured and replayed locally: `aa 01 99 00`, `aa 01 01 07` | Vacuum |
| Whole-house start / resume | Panel `work_mode`: `aa 01 01 04` / `aa 01 01 06` | Vacuum; resume when a mission exists |
| Return to station | Panel `work_mode.charge`: `aa 01 01 01` | Vacuum dock action |
| Suction | Panel `cmdSetSuctionMode`: `aa 01 50 <level>` | Vacuum fan speed |
| Water | Panel `cmdSetWaterMode`: `aa 01 51 <value>` | Select; legacy levels or 1–30, based on reported encoding |
| Cleaning mode | Panel `cmdSetMopMode`: `aa 01 58 <mode>` | Select: vacuum, mop, both, vacuum then mop |
| Wash mops | Panel `cmdSetCleanMop`: `aa 01 99 01` | Station button |
| Empty dust | Panel `cmdSetCleanAndDustMop(2,1)`: `aa 01 5a 02 01` | Station button |
| Dry / stop drying | Panel `cmdRagDrying`: `aa 01 5c 01` / `00` | Station buttons |
| Clean station basin | Captured `cmdAutoClean`: `aa 01 5b 01` | Station button |
| Room list | Panel `requestMapRoomInfoList`: `aa 02 28`, v1/v2 replies | Vacuum `rooms` attribute |
| Room cleaning | Panel `cmdRoomModeClean`, ten padded records | `eureka_robot.clean_rooms` + card |
| Cleaned area / minutes / mop presence / fault codes | Panel status offsets and bit fields | Sensors and binary sensors |

**Corrections to earlier research:** the captured 115-byte `aa 01 03 …` packet selects room ID 3, not whole-house cleaning. It is now a room-command fixture, not the default start command. `0x5B` cleans the station basin; `0x99 01` requests mop washing. Default start and resume use the panel's dedicated work-mode commands.

Station buttons require a docked status. Unknown fault codes are exposed as raw codes, not invented descriptions. Room names are cloud metadata; local rooms use neutral labels such as “Room 3”. The card localizes those labels to Spanish when appropriate.

Consumable counters in the panel are cloud-derived; this local integration does not invent their values. Maps, video, cloud history, reset, OTA, remote control movement and provisioning settings are not included.

## Dashboard

The integration serves and registers its card automatically. Add **Eureka Robot** from the dashboard card picker, or use:

```yaml
type: custom:eureka-robot-card
entity: vacuum.eureka_j15_pro_ultra
```

Use your actual vacuum entity ID. The card follows HA's theme, supports English/Spanish, discovers renamed sibling entities by device, and shows:

- State, battery, cleaned area and time.
- Start/resume, pause, stop and dock.
- Cleaning mode, water and suction settings.
- Mop wash, dust emptying, drying and basin cleaning.
- Room chips, repeat count and “Clean selected”.

Offline/pending controls are disabled. Service errors appear in the card. No separate resource entry is needed; reload the browser after installation/update.

## Automations and room cleaning

Use standard `vacuum.start`, `vacuum.pause`, `vacuum.stop`, `vacuum.return_to_base`, `vacuum.set_fan_speed`, `select.select_option` and `button.press` actions.

```yaml
action: eureka_robot.clean_rooms
target:
  entity_id: vacuum.eureka_j15_pro_ultra
data:
  rooms: [3, 7]
  repeats: 1
```

Room IDs must exist in the current local `rooms` attribute, be unique and contain 1–10 entries. Repeats: 1–3. Cleaning uses the latest reported supported cleaning mode, suction and water settings. Rooms refresh every 10 minutes and when a mission finishes. If the optional room query is unsupported/unavailable, basic controls continue working and room cleaning remains unavailable.

## Connection and limitations

One short-lived connection per request, written immediately after connect. Requests are serialized because the robot appears to accept one client at a time. Do not run another local client or research capture tools alongside the integration.

Status polls every 10 seconds idle and 3 seconds while active. Three failed polls mark entities unavailable; recovery is automatic. Offline startup retries. Queries and failed connections retry up to three times. After possible command delivery, a missing acknowledgement reports an **unknown outcome** and requests fresh status; the integration never blindly replays the command.

Port 12127 is undocumented, unauthenticated and unencrypted. Keep it on a trusted LAN and do not expose it to the internet. Firmware changes can break it. A corrupt length field can delay parsing until the bounded request timeout; read-only queries reconnect/retry.

## Español

Integración **local** para Eureka J15 Pro Ultra, sin cuenta ni nube. Incluye aspiradora, regreso a base, succión, agua, cuatro modos de limpieza, lavado/secado de mopas, vaciado, limpieza de bandeja, habitaciones y sensores. Las funciones ampliadas se obtuvieron de las tablas y codificadores del panel oficial; **todavía requieren pruebas físicas por conexión local**.

**Instalación:** botón azul **Open in HACS** → añadir repositorio y descargar → reiniciar Home Assistant → **Add integration**. Los botones no omiten la descarga ni el reinicio.

**Buscar aspiradora:** al configurar, elige **Buscar en la red local**. Confirma o modifica la subred, por ejemplo `192.168.1.0/24`. Se consulta el puerto 12127 y se validan respuestas B8; la búsqueda no mueve el robot. Selecciona la IP y confirma que corresponde a tu J15 Pro Ultra. También puedes introducirla manualmente. Si está en otra VLAN, HA debe tener acceso a ella. Reserva la IP en el router; para cambiarla después, usa **Reconfigurar**.

La tarjeta incluida conecta todos los controles y permite seleccionar habitaciones y repeticiones. Los nombres locales son “Habitación 3”, etc.; los nombres personalizados y los contadores de consumibles del panel dependen de la nube. No se incluyen mapas, vídeo, historial ni restablecimiento de fábrica.

## License

MIT. Independent project; not affiliated with Eureka, Midea or Robozone. Original robot icon. No vendor app files, captures, device identities, private network addresses, account credentials or certificates are distributed.
