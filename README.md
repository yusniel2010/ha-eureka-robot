# Eureka Robot (Local)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yusniel2010&repository=ha-eureka-robot&category=integration)
[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=eureka_robot)

## Instalar la integración

Requisitos: Home Assistant 2025.12 o posterior, HACS instalado y una Eureka J15 Pro Ultra accesible desde la red de Home Assistant.

1. Pulsa **Open in HACS**, añade el repositorio y descarga la integración.
2. Reinicia **Home Assistant**.
3. Pulsa **Add integration**, o ve a **Ajustes → Dispositivos y servicios → Añadir integración → Eureka Robot (Local)**.
4. Elige **Buscar en la red local** o **Introducir IP manualmente**.
5. Si buscas en la red, confirma la subred, selecciona el dispositivo y confirma el modelo.
6. Completa la configuración y comprueba que se haya creado una entidad `vacuum`.

Reserva la IP del robot en el router. Si cambia, usa **Reconfigurar** en la integración.

### Instalación manual

1. Copia `custom_components/eureka_robot` a `/config/custom_components/eureka_robot`.
2. Reinicia Home Assistant.
3. Añade **Eureka Robot (Local)** desde Dispositivos y servicios.

## Añadir la tarjeta al dashboard

1. Configura primero la integración; descargarla desde HACS no completa este paso.
2. Recarga completamente el navegador. En la aplicación móvil, ciérrala y vuelve a abrirla.
3. Abre el dashboard → **Editar → Añadir tarjeta**.
4. Busca **Eureka Robot**, selecciónala y elige la entidad de tu aspiradora.

También puedes usar **Añadir tarjeta → Manual**:

```yaml
type: custom:eureka-robot-card
entity: vacuum.eureka_j15_pro_ultra
```

Sustituye `vacuum.eureka_j15_pro_ultra` por el identificador real creado por tu integración.

### Si aparece «Custom element doesn't exist: eureka-robot-card»

1. Confirma que la integración ya está configurada y que existe la entidad `vacuum`.
2. Activa **Modo avanzado** en tu perfil de Home Assistant si no aparece el menú de recursos.
3. Ve a **Ajustes → Paneles de control → ⋮ → Recursos → Añadir recurso**.
4. Introduce:
   - **URL:** `/eureka_robot/eureka-robot-card.js?v=0.2.0`
   - **Tipo:** **Módulo JavaScript**.
5. Guarda y recarga completamente el navegador (`Ctrl+Shift+R` / `Cmd+Shift+R`).
6. Vuelve a añadir la tarjeta mediante el YAML anterior.

Para comprobar que el archivo está disponible, abre `/eureka_robot/eureka-robot-card.js?v=0.2.0` detrás de la dirección habitual de tu Home Assistant. Debe mostrarse código JavaScript. Si aparece **404**, comprueba la instalación y reinicia Home Assistant antes de volver a intentarlo.

Si administras los recursos en YAML, añade este elemento a tu lista `lovelace.resources` existente:

```yaml
- url: /eureka_robot/eureka-robot-card.js?v=0.2.0
  type: module
```

No añadas el mismo recurso varias veces.

## Actualizar

1. Descarga la nueva versión desde HACS.
2. Reinicia Home Assistant.
3. Recarga el navegador o vuelve a abrir la aplicación móvil.

## English installation

1. Click **Open in HACS**, add the repository and download the integration.
2. Restart Home Assistant.
3. Click **Add integration**, or open **Settings → Devices & services → Add integration → Eureka Robot (Local)**.
4. Choose local network search or enter the robot IP manually. Complete setup and verify the vacuum entity exists.
5. Reload the browser, edit your dashboard and add the **Eureka Robot** card. Select your vacuum entity.

If the card is missing, add `/eureka_robot/eureka-robot-card.js?v=0.2.0` under **Settings → Dashboards → ⋮ → Resources** as a **JavaScript module**, then reload the browser. The resource URL must return JavaScript, not 404. Use the manual card YAML above with your actual entity ID.
