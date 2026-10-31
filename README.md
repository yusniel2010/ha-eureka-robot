# Eureka Robot (Local)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yusniel2010&repository=ha-eureka-robot&category=integration)
[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=eureka_robot)

Control and monitor a **Eureka J15 Pro Ultra** from Home Assistant **over your local network**: no Eureka account, no cloud, no token. Includes a dashboard card.

[Versión en español más abajo](#versión-en-español)

> **Work in progress.** Unofficial project, not affiliated with or endorsed by Eureka or Midea. Only the J15 Pro Ultra has been tested: if you have another Eureka model, please try it and [open an issue](https://github.com/yusniel2010/ha-eureka-robot/issues) with what works and what doesn't.

## Requirements

- Home Assistant 2026.3 or newer, with [HACS](https://hacs.xyz).
- The robot set up in the Eureka app and connected to Wi-Fi.
- Home Assistant and the robot on networks that can reach each other (the robot listens on TCP port 12127).
- A reserved (fixed) IP address for the robot in your router is recommended.

## Installation

1. Click **Open in HACS** above, add the repository and download **Eureka Robot (Local)**.
2. Restart Home Assistant.
3. Click **Add integration** above, or go to **Settings → Devices & services → Add integration → Eureka Robot (Local)**.
4. Choose **Search automatically**. Home Assistant scans its own networks; you don't need to enter a subnet.
   - If the robot isn't found, retry, choose **Enter IP manually**, or use **Search another network (advanced)**.
5. Select the robot, confirm the model and finish. A `vacuum` entity is created.

Setup fields:

| Field | Description |
|---|---|
| Search automatically | Scans the private networks of Home Assistant's enabled network adapters for robots answering on TCP 12127. |
| IP address (manual) | The robot's IP address or hostname. Setup checks that the robot answers before creating the entry. |
| Network (advanced) | A private network in CIDR form (for example `192.168.20.0/24`) when the robot is on a different, routed network. |
| Confirm model | Required: only the J15 Pro Ultra has been tested. |

**Automatic discovery:** when the robot joins the network (or renews its IP), Home Assistant can show it under **Discovered** in **Devices & services**; confirm the model to add it.

**IP changes:** the integration identifies the robot by its MAC address, so if the robot gets a new IP, Home Assistant updates it automatically when it sees the robot on the network. You can also open the integration and use **Reconfigure**.

### Manual installation

1. Copy `custom_components/eureka_robot` to `/config/custom_components/eureka_robot`.
2. Restart Home Assistant and add **Eureka Robot (Local)** from **Devices & services**.

## What you get

| Type | Entities |
|---|---|
| Vacuum | Start, pause, stop, return to dock, suction level, **clean area** (rooms mapped to your Home Assistant areas). Room list in the `rooms` attribute. |
| Sensors | Battery, status, station status, cleaned area, cleaning time, robot fault, station fault (readable text; raw code in the `code` attribute). |
| Binary sensors | Problem, mop installed, water shortage. |
| Selects | Cleaning mode, water level, room. |
| Buttons | Wash mops, empty dust, dry mops, stop drying, clean station, **check water**, **clean room** (cleans the room picked in the Room select). Station buttons work only while the robot is docked. |
| Service | `eureka_robot.clean_rooms`: clean selected room IDs from the `rooms` attribute. |

**Check water:** after refilling the clean-water tank, the station keeps the "tank empty" alert (red light) until it pumps water again. This button starts a mop wash, stops it as soon as the alert clears (about 2 seconds) and reports an error if the tank still reads empty. You'll hear the station briefly.

### Action: `eureka_robot.clean_rooms`

Cleans selected rooms with the robot's current suction, water level and cleaning mode.

| Field | Required | Description |
|---|---|---|
| `rooms` | yes | 1–10 room IDs from the vacuum's `rooms` attribute. |
| `repeats` | no | Passes per room, 1–3 (default 1). |

```yaml
action: eureka_robot.clean_rooms
target:
  entity_id: vacuum.eureka_j15_pro_ultra
data:
  rooms: [3, 7]
  repeats: 1
```

## Rooms

The robot only reports room numbers locally (names live in the Eureka cloud), so rooms start as `Room 1`, `Room 2`, and so on. Map them to your Home Assistant areas once:

1. **Find which number is which room:** pick a room in the **Room** select and press **Clean room**. Watch where the robot goes, then dock it.
2. **Map them:** open the vacuum entity's settings, go to its area mapping, and assign each `Room N` to a Home Assistant area (Kitchen, Bedroom…). Leave unused ones empty.
3. **Clean by area:** use the built-in `vacuum.clean_area` action, or the dashboard card. Mapped rooms show their area name in the card, the Room select and the `rooms` attribute.

```yaml
action: vacuum.clean_area
target:
  entity_id: vacuum.eureka_j15_pro_ultra
data:
  cleaning_area_id: [kitchen, living_room]
```

If the robot's rooms change (for example after re-mapping your home in the Eureka app), Home Assistant shows a repair asking you to map the areas again.

## Dashboard card

Shows status, battery, cleaning controls, mode/water/suction, station actions and room chips (with your area names once mapped). Robot and station faults appear in a banner at the top; when the clean-water tank is empty, the banner offers **Check water**.

1. Set up the integration first. The card is registered automatically; you don't need to add a resource.
2. Fully reload the browser (on the mobile app, close and reopen it).
3. Edit a dashboard → **Add card** → search **Eureka Robot** → pick your vacuum entity.

Or add it manually (**Add card → Manual**), replacing the entity ID with yours:

```yaml
type: custom:eureka-robot-card
entity: vacuum.eureka_j15_pro_ultra
```

### "Custom element doesn't exist: eureka-robot-card"

1. Check that the integration is set up and the `vacuum` entity exists.
2. Enable **Advanced mode** in your user profile if you don't see Resources.
3. Go to **Settings → Dashboards → ⋮ → Resources → Add resource**:
   - **URL:** `/eureka_robot/eureka-robot-card.js?v=0.5.2`
   - **Type:** JavaScript module
4. Save and fully reload the browser (`Ctrl+Shift+R` / `Cmd+Shift+R`).

Opening that URL on your Home Assistant address must show JavaScript code. A **404** means the integration isn't installed or loaded; restart Home Assistant.

If you manage resources in YAML, add this once to `lovelace.resources`:

```yaml
- url: /eureka_robot/eureka-robot-card.js?v=0.5.2
  type: module
```

## Updating

1. Download the new version in HACS.
2. Restart Home Assistant.
3. Reload the browser or reopen the mobile app.

## Removing

1. Go to **Settings → Devices & services → Eureka Robot (Local)**, open the **⋮** menu on the entry and choose **Delete**.
2. Remove the card from your dashboards.
3. To uninstall the files, open **HACS → Eureka Robot (Local) → ⋮ → Remove**, then restart Home Assistant.

The robot and the Eureka app keep working; the integration doesn't change anything on the robot or your account.

## Troubleshooting

- **Commands sometimes fail:** the robot refuses some local connections when busy. The integration retries refused commands automatically; if a command still reports "outcome unknown", check the robot's state before trying again.
- **Robot unavailable:** check that its IP hasn't changed (use **Reconfigure**) and that Home Assistant can reach TCP port 12127 on it.
- **Debug logs:** add to `configuration.yaml`, restart and reproduce the problem:

  ```yaml
  logger:
    logs:
      custom_components.eureka_robot: debug
  ```

## Known issues

- Pause now sends the work-mode pause command, but it hasn't been confirmed on a live robot yet: [#1](https://github.com/yusniel2010/ha-eureka-robot/issues/1). Please report if it doesn't pause yours.

## Contributing

Bug reports, ideas and pull requests are welcome in this repository: [open an issue](https://github.com/yusniel2010/ha-eureka-robot/issues) or send a pull request against `main`. Please don't include your robot's IP, serial number or account details in issues or logs.

## License

[MIT](LICENSE)

---

# Versión en español

Controla y monitorea una **Eureka J15 Pro Ultra** desde Home Assistant **por tu red local**: sin cuenta de Eureka, sin nube y sin token. Incluye una tarjeta para el dashboard.

> **En desarrollo.** Proyecto no oficial, no afiliado ni respaldado por Eureka ni Midea. Solo se ha probado con la J15 Pro Ultra: si tienes otro modelo de Eureka, pruébala y [abre un issue](https://github.com/yusniel2010/ha-eureka-robot/issues) con lo que funciona y lo que no.

## Requisitos

- Home Assistant 2026.3 o posterior, con [HACS](https://hacs.xyz).
- El robot configurado en la app de Eureka y conectado al Wi-Fi.
- Home Assistant y el robot en redes que se puedan comunicar (el robot escucha en el puerto TCP 12127).
- Se recomienda reservar una IP fija para el robot en el router.

## Instalación

1. Pulsa **Open in HACS** arriba, añade el repositorio y descarga **Eureka Robot (Local)**.
2. Reinicia Home Assistant.
3. Pulsa **Add integration** arriba, o ve a **Ajustes → Dispositivos y servicios → Añadir integración → Eureka Robot (Local)**.
4. Elige **Buscar automáticamente**. Home Assistant revisa sus propias redes; no hace falta escribir la subred.
   - Si no encuentra el robot, reintenta, elige **Introducir IP manualmente** o usa **Buscar en otra red (avanzado)**.
5. Selecciona el robot, confirma el modelo y termina. Se crea una entidad `vacuum`.

Campos de configuración:

| Campo | Descripción |
|---|---|
| Buscar automáticamente | Revisa las redes privadas de los adaptadores de red activos de Home Assistant buscando robots que respondan en el puerto TCP 12127. |
| Dirección IP (manual) | La IP o el nombre de host del robot. Antes de crear la entrada se comprueba que el robot responda. |
| Red (avanzado) | Una red privada en formato CIDR (por ejemplo `192.168.20.0/24`) cuando el robot está en otra red enrutada. |
| Confirmar modelo | Obligatorio: solo se ha probado con la J15 Pro Ultra. |

**Descubrimiento automático:** cuando el robot se conecta a la red (o renueva su IP), Home Assistant puede mostrarlo en **Descubiertos** dentro de **Dispositivos y servicios**; confirma el modelo para añadirlo.

**Cambios de IP:** la integración identifica al robot por su dirección MAC, así que si recibe una IP nueva, Home Assistant la actualiza sola al verlo en la red. También puedes abrir la integración y usar **Reconfigurar**.

### Instalación manual

1. Copia `custom_components/eureka_robot` a `/config/custom_components/eureka_robot`.
2. Reinicia Home Assistant y añade **Eureka Robot (Local)** desde **Dispositivos y servicios**.

## Qué incluye

| Tipo | Entidades |
|---|---|
| Aspiradora | Iniciar, pausar, detener, volver a la base, nivel de succión, **limpiar área** (habitaciones asignadas a tus áreas de Home Assistant). Lista de cuartos en el atributo `rooms`. |
| Sensores | Batería, estado, estado de la base, área limpiada, tiempo de limpieza, falla del robot, falla de la base (texto legible; código en el atributo `code`). |
| Sensores binarios | Problema, mopa instalada, sin agua. |
| Selectores | Modo de limpieza, nivel de agua, habitación. |
| Botones | Lavar mopas, vaciar polvo, secar mopas, detener secado, limpiar base, **revisar agua**, **limpiar habitación** (limpia la elegida en el selector Habitación). Los botones de la base solo funcionan con el robot en la base. |
| Servicio | `eureka_robot.clean_rooms`: limpia los cuartos elegidos del atributo `rooms`. |

**Revisar agua:** después de rellenar el tanque de agua limpia, la base mantiene la alerta de "tanque vacío" (luz roja) hasta que vuelve a bombear agua. Este botón inicia un lavado de mopas, lo detiene en cuanto la alerta se borra (unos 2 segundos) y avisa si el tanque sigue vacío. Se oye la base un momento.

### Acción: `eureka_robot.clean_rooms`

Limpia los cuartos elegidos con la succión, el nivel de agua y el modo de limpieza actuales del robot.

| Campo | Obligatorio | Descripción |
|---|---|---|
| `rooms` | sí | De 1 a 10 IDs de cuarto del atributo `rooms` de la aspiradora. |
| `repeats` | no | Pasadas por cuarto, de 1 a 3 (por defecto 1). |

```yaml
action: eureka_robot.clean_rooms
target:
  entity_id: vacuum.eureka_j15_pro_ultra
data:
  rooms: [3, 7]
  repeats: 1
```

## Habitaciones

Localmente el robot solo reporta números de habitación (los nombres se guardan en la nube de Eureka), así que al principio aparecen como `Room 1`, `Room 2`, etc. Asígnalas a tus áreas de Home Assistant una sola vez:

1. **Descubre cuál es cuál:** elige una habitación en el selector **Habitación** y pulsa **Limpiar habitación**. Mira adónde va el robot y luego mándalo a la base.
2. **Asígnalas:** abre los ajustes de la entidad de la aspiradora, entra en la asignación de áreas y asigna cada `Room N` a un área de Home Assistant (Cocina, Dormitorio…). Deja vacías las que no uses.
3. **Limpia por área:** usa la acción nativa `vacuum.clean_area` o la tarjeta del dashboard. Las habitaciones asignadas muestran el nombre del área en la tarjeta, en el selector Habitación y en el atributo `rooms`.

```yaml
action: vacuum.clean_area
target:
  entity_id: vacuum.eureka_j15_pro_ultra
data:
  cleaning_area_id: [cocina, sala]
```

Si cambian las habitaciones del robot (por ejemplo, al volver a mapear la casa en la app de Eureka), Home Assistant muestra una reparación para asignar las áreas de nuevo.

## Tarjeta del dashboard

Muestra estado, batería, controles de limpieza, modo/agua/succión, acciones de la base y botones de habitaciones (con el nombre de tus áreas una vez asignadas). Las fallas del robot y de la base aparecen en un aviso arriba; si el tanque de agua limpia está vacío, el aviso ofrece **Revisar agua**.

1. Configura primero la integración. La tarjeta se registra sola; no hace falta añadir un recurso.
2. Recarga el navegador por completo (en la app móvil, ciérrala y vuelve a abrirla).
3. Edita un dashboard → **Añadir tarjeta** → busca **Eureka Robot** → elige tu aspiradora.

O añádela a mano (**Añadir tarjeta → Manual**), cambiando el ID de entidad por el tuyo:

```yaml
type: custom:eureka-robot-card
entity: vacuum.eureka_j15_pro_ultra
```

### «Custom element doesn't exist: eureka-robot-card»

1. Comprueba que la integración esté configurada y que exista la entidad `vacuum`.
2. Activa el **Modo avanzado** en tu perfil si no ves Recursos.
3. Ve a **Ajustes → Paneles de control → ⋮ → Recursos → Añadir recurso**:
   - **URL:** `/eureka_robot/eureka-robot-card.js?v=0.5.2`
   - **Tipo:** Módulo JavaScript
4. Guarda y recarga el navegador por completo (`Ctrl+Shift+R` / `Cmd+Shift+R`).

Esa URL, abierta en la dirección de tu Home Assistant, debe mostrar código JavaScript. Un **404** significa que la integración no está instalada o cargada; reinicia Home Assistant.

Si administras los recursos en YAML, añade esto una sola vez a `lovelace.resources`:

```yaml
- url: /eureka_robot/eureka-robot-card.js?v=0.5.2
  type: module
```

## Actualizar

1. Descarga la nueva versión en HACS.
2. Reinicia Home Assistant.
3. Recarga el navegador o vuelve a abrir la app móvil.

## Eliminar

1. Ve a **Ajustes → Dispositivos y servicios → Eureka Robot (Local)**, abre el menú **⋮** de la entrada y elige **Eliminar**.
2. Quita la tarjeta de tus dashboards.
3. Para desinstalar los archivos, abre **HACS → Eureka Robot (Local) → ⋮ → Eliminar** y reinicia Home Assistant.

El robot y la app de Eureka siguen funcionando; la integración no cambia nada en el robot ni en tu cuenta.

## Solución de problemas

- **A veces falla un comando:** el robot rechaza algunas conexiones locales cuando está ocupado. La integración reintenta sola los comandos rechazados; si aun así dice "outcome unknown", revisa el estado del robot antes de repetirlo.
- **Robot no disponible:** revisa que su IP no haya cambiado (usa **Reconfigurar**) y que Home Assistant llegue al puerto TCP 12127 del robot.
- **Logs de depuración:** añade esto a `configuration.yaml`, reinicia y reproduce el problema:

  ```yaml
  logger:
    logs:
      custom_components.eureka_robot: debug
  ```

## Problemas conocidos

- Pausar ahora manda el comando de pausa del modo de trabajo, pero aún no está confirmado con el robot real: [#1](https://github.com/yusniel2010/ha-eureka-robot/issues/1). Avisa si no pausa el tuyo.

## Contribuir

Los reportes de errores, ideas y pull requests son bienvenidos en este repositorio: [abre un issue](https://github.com/yusniel2010/ha-eureka-robot/issues) o envía un pull request contra `main`. No incluyas la IP, el número de serie ni datos de tu cuenta en issues o logs.

## Licencia

[MIT](LICENSE)
