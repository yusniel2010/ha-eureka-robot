# Eureka Robot (Local)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yusniel2010&repository=ha-eureka-robot&category=integration)
[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=eureka_robot)

Control and monitor a **Eureka J15 Pro Ultra** from Home Assistant **over your local network**: no Eureka account, no cloud, no token. Includes a dashboard card.

[Versión en español más abajo](#versión-en-español)

> Unofficial project. Not affiliated with or endorsed by Eureka or Midea. Only the J15 Pro Ultra has been tested.

## Requirements

- Home Assistant 2025.12 or newer, with [HACS](https://hacs.xyz).
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

If the robot's IP changes, open the integration and use **Reconfigure**.

### Manual installation

1. Copy `custom_components/eureka_robot` to `/config/custom_components/eureka_robot`.
2. Restart Home Assistant and add **Eureka Robot (Local)** from **Devices & services**.

## What you get

| Type | Entities |
|---|---|
| Vacuum | Start, pause, stop, return to dock, suction level. Room list in the `rooms` attribute. |
| Sensors | Battery, status, station status, cleaned area, cleaning time, robot fault, station fault (readable text; raw code in the `code` attribute). |
| Binary sensors | Problem, mop installed, water shortage. |
| Selects | Cleaning mode, water level. |
| Buttons | Wash mops, empty dust, dry mops, stop drying, clean station, **check water**. Station buttons work only while the robot is docked. |
| Service | `eureka_robot.clean_rooms`: clean selected room IDs from the `rooms` attribute. |

**Check water:** after refilling the clean-water tank, the station keeps the "tank empty" alert (red light) until it pumps water again. This button starts a mop wash, stops it as soon as the alert clears (about 2 seconds) and reports an error if the tank still reads empty. You'll hear the station briefly.

## Dashboard card

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
   - **URL:** `/eureka_robot/eureka-robot-card.js?v=0.3.0`
   - **Type:** JavaScript module
4. Save and fully reload the browser (`Ctrl+Shift+R` / `Cmd+Shift+R`).

Opening that URL on your Home Assistant address must show JavaScript code. A **404** means the integration isn't installed or loaded; restart Home Assistant.

If you manage resources in YAML, add this once to `lovelace.resources`:

```yaml
- url: /eureka_robot/eureka-robot-card.js?v=0.3.0
  type: module
```

## Updating

1. Download the new version in HACS.
2. Restart Home Assistant.
3. Reload the browser or reopen the mobile app.

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

- Pause sends the wrong command: [#1](https://github.com/yusniel2010/ha-eureka-robot/issues/1).

## Contributing

Bug reports, ideas and pull requests are welcome in this repository: [open an issue](https://github.com/yusniel2010/ha-eureka-robot/issues) or send a pull request against `main`. Please don't include your robot's IP, serial number or account details in issues or logs.

## License

[MIT](LICENSE)

---

# Versión en español

Controla y monitorea una **Eureka J15 Pro Ultra** desde Home Assistant **por tu red local**: sin cuenta de Eureka, sin nube y sin token. Incluye una tarjeta para el dashboard.

> Proyecto no oficial. No está afiliado ni respaldado por Eureka ni Midea. Solo se ha probado con la J15 Pro Ultra.

## Requisitos

- Home Assistant 2025.12 o posterior, con [HACS](https://hacs.xyz).
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

Si cambia la IP del robot, abre la integración y usa **Reconfigurar**.

### Instalación manual

1. Copia `custom_components/eureka_robot` a `/config/custom_components/eureka_robot`.
2. Reinicia Home Assistant y añade **Eureka Robot (Local)** desde **Dispositivos y servicios**.

## Qué incluye

| Tipo | Entidades |
|---|---|
| Aspiradora | Iniciar, pausar, detener, volver a la base, nivel de succión. Lista de cuartos en el atributo `rooms`. |
| Sensores | Batería, estado, estado de la base, área limpiada, tiempo de limpieza, falla del robot, falla de la base (texto legible; código en el atributo `code`). |
| Sensores binarios | Problema, mopa instalada, sin agua. |
| Selectores | Modo de limpieza, nivel de agua. |
| Botones | Lavar mopas, vaciar polvo, secar mopas, detener secado, limpiar base, **revisar agua**. Los botones de la base solo funcionan con el robot en la base. |
| Servicio | `eureka_robot.clean_rooms`: limpia los cuartos elegidos del atributo `rooms`. |

**Revisar agua:** después de rellenar el tanque de agua limpia, la base mantiene la alerta de "tanque vacío" (luz roja) hasta que vuelve a bombear agua. Este botón inicia un lavado de mopas, lo detiene en cuanto la alerta se borra (unos 2 segundos) y avisa si el tanque sigue vacío. Se oye la base un momento.

## Tarjeta del dashboard

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
   - **URL:** `/eureka_robot/eureka-robot-card.js?v=0.3.0`
   - **Tipo:** Módulo JavaScript
4. Guarda y recarga el navegador por completo (`Ctrl+Shift+R` / `Cmd+Shift+R`).

Esa URL, abierta en la dirección de tu Home Assistant, debe mostrar código JavaScript. Un **404** significa que la integración no está instalada o cargada; reinicia Home Assistant.

Si administras los recursos en YAML, añade esto una sola vez a `lovelace.resources`:

```yaml
- url: /eureka_robot/eureka-robot-card.js?v=0.3.0
  type: module
```

## Actualizar

1. Descarga la nueva versión en HACS.
2. Reinicia Home Assistant.
3. Recarga el navegador o vuelve a abrir la app móvil.

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

- Pausar manda el comando equivocado: [#1](https://github.com/yusniel2010/ha-eureka-robot/issues/1).

## Contribuir

Los reportes de errores, ideas y pull requests son bienvenidos en este repositorio: [abre un issue](https://github.com/yusniel2010/ha-eureka-robot/issues) o envía un pull request contra `main`. No incluyas la IP, el número de serie ni datos de tu cuenta en issues o logs.

## Licencia

[MIT](LICENSE)
