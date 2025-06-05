# 🛡️ Bot del Gremio — Sistema de Rangos y Flags para Discord

Este bot está diseñado para gestionar un sistema de **rangos progresivos** tipo RPG, con comandos visuales como `!perfil`, validación de **flags secretas**, y organización automática del servidor en **canales por rango**.

---

## 📦 Funcionalidades Principales

### 👤 Sistema de Perfil
- Comando `!perfil`: genera una tarjeta de perfil con avatar, insignia, nivel, XP y barra de progreso visual.
- Asigna automáticamente el primer rango ("F") si no tienes uno.

### 🏆 Rangos
- Rangos en orden: `F`, `E`, `D`, `C`, `B`, `A`, `S`, `SS`, `SSS`, `Gran Maestro`.
- XP personalizada por rango para subir de nivel.
- Colores de barra y fondo configurables por rango.

### 🛠️ Comando de Setup Automático
- Comando `!setup_canales` (admin):
  - Crea todos los roles, categorías y canales para cada rango.
  - Establece permisos de visibilidad únicos por rango.
  - Incluye canales de voz por rango.
  - Crea estructura privada exclusiva para el rango `Gran Maestro`.

### 🎯 Flags Secretas
- Canal `enviar-flag`: visible para todos, pero no permite leer mensajes previos.
- Los usuarios introducen flags sin que se revelen, el bot responde si es correcta o no.
- Flags almacenadas en archivo `flags.json`.

### 🔧 Comandos Administrativos

| Comando             | Descripción                                              |
|---------------------|----------------------------------------------------------|
| `!setup_canales`    | Crea todos los roles, canales y categorías por rango.    |
| `!bajar_rango @user`| Baja de rango a un usuario al siguiente inferior.        |
| `!ver_flags`        | Muestra las flags actualmente activas.                   |
| `!borrar_flag nombre`| Elimina una flag del sistema.                           |
| `!anuncio mensaje`  | Envía un anuncio embebido al canal.                      |

---

## 🐳 Docker

### Requisitos
- Docker
- Docker Compose (opcional)

### Ejecución
```bash
docker build -t gremio-bot .
docker run -d --name bot --env DISCORD_TOKEN=tu_token_aqui gremio-bot
```

### Ejecución_Windows
```bash
docker build -t gremio-bot .
docker run -d --name bot -e DISCORD_TOKEN="DC_TOKEN" -v "${PWD}\perfiles.json:/app/perfiles.json" -v "${PWD}\flags.json:/app/flags.json" medieval-bot