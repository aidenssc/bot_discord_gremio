import discord
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageDraw, ImageFont
import json, os, requests
from io import BytesIO
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Archivos de datos
PERFILES_PATH = "perfiles.json"
FLAGS_PATH = "flags.json"
DESAFIOS_PATH = "desafios.json"

RANGOS = ["F", "E", "D", "C", "B", "A", "S", "SS", "SSS"]

XP_RANGOS = {
    "F": 0,
    "E": 1000,
    "D": 2500,
    "C": 5000,
    "B": 10000,
    "A": 20000,
    "S": 40000,
    "SS": 400000,
    "SSS": 560000
}
# ========================= UTILIDADES ==============================
def cargar_datos(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)
    
def guardar_datos(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def calcular_rango(xp):
    # Ordenar los rangos de mayor a menor XP requerida
    for rango, xp_necesaria in sorted(XP_RANGOS.items(), key=lambda item: item[1], reverse=True):
        if xp >= xp_necesaria:
            return rango
    return "F"  # Valor por defecto si no cumple ninguno

async def actualizar_rango_y_rol(miembro, perfil):
    xp = perfil["xp"]
    guild = miembro.guild

    rango_anterior = perfil.get("rango", "F")
    nuevo_rango = calcular_rango(xp)
    perfil["rango"] = nuevo_rango

    if nuevo_rango != rango_anterior:
        rol_anterior = get(guild.roles, name=rango_anterior)
        if rol_anterior and rol_anterior in miembro.roles:
            await miembro.remove_roles(rol_anterior)

        rol_nuevo = get(guild.roles, name=nuevo_rango)
        if rol_nuevo:
            await miembro.add_roles(rol_nuevo)

        canal_anuncios = get(guild.text_channels, name="comandos-del-bot")
        if canal_anuncios:
            await canal_anuncios.send(
                f"🏅 {miembro.mention} ha ascendido de `{rango_anterior}` a `{nuevo_rango}` con {xp} XP. ¡Felicidades!"
            )

from PIL import Image, ImageDraw, ImageFont
import os

def crear_imagen_perfil(nombre, rango, xp, nivel, avatar_path, insignia_path, output_path="perfil.png"):
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    # Estilos por rango
    ESTILOS_RANGOS = {
        "F": {"fondo": (80, 60, 40), "borde": (60, 50, 40), "barra_bg": (100, 80, 60), "barra_fg": (255, 180, 60)},
        "E": {"fondo": (60, 70, 90), "borde": (40, 50, 70), "barra_bg": (80, 90, 110), "barra_fg": (100, 140, 200)},
        "D": {"fondo": (70, 50, 70), "borde": (50, 30, 50), "barra_bg": (90, 70, 90), "barra_fg": (180, 100, 200)},
        "C": {"fondo": (50, 50, 50), "borde": (30, 30, 30), "barra_bg": (70, 70, 70), "barra_fg": (160, 160, 160)},
        "B": {"fondo": (40, 60, 80), "borde": (30, 50, 70), "barra_bg": (60, 80, 100), "barra_fg": (120, 180, 250)},
        "A": {"fondo": (40, 80, 40), "borde": (30, 70, 30), "barra_bg": (70, 120, 70), "barra_fg": (120, 255, 120)},
        "S": {"fondo": (60, 60, 90), "borde": (40, 40, 70), "barra_bg": (80, 80, 110), "barra_fg": (150, 150, 255)},
        "SS": {"fondo": (90, 70, 40), "borde": (70, 50, 30), "barra_bg": (110, 90, 60), "barra_fg": (255, 180, 100)},
        "SSS": {"fondo": (100, 60, 60), "borde": (80, 40, 40), "barra_bg": (130, 70, 70), "barra_fg": (255, 120, 120)},
        "Gran Maestro": {"fondo": (40, 30, 60), "borde": (30, 20, 50), "barra_bg": (0, 0, 0), "barra_fg": (0, 0, 0)},
        "Root": {"fondo": (20, 30, 25), "borde": (15, 25, 20), "barra_bg": (0, 0, 0), "barra_fg": (0, 0, 0)}
    }

    estilo = ESTILOS_RANGOS.get(rango, ESTILOS_RANGOS["F"])
    color_fondo = estilo["fondo"]
    color_borde = estilo["borde"]
    color_barra_bg = estilo["barra_bg"]
    color_barra_fg = estilo["barra_fg"]
    color_texto = (255, 220, 120)

    fuente_titulo = ImageFont.truetype("fuentes/medieval.ttf", 32)
    fuente_texto = ImageFont.truetype("fuentes/medieval.ttf", 20)

    margen = 20
    ancho_total = 500
    alto_total = 160
    alto_avatar = 80

    imagen = Image.new("RGBA", (ancho_total, alto_total), color_borde)
    draw = ImageDraw.Draw(imagen)

    draw.rectangle([5, 5, ancho_total - 5, alto_total - 5], fill=color_fondo)

    # Avatar redondo
    avatar = Image.open(avatar_path).resize((alto_avatar, alto_avatar)).convert("RGBA")
    mask = Image.new("L", (alto_avatar, alto_avatar), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, alto_avatar, alto_avatar), fill=255)
    avatar_redondo = ImageOps.fit(avatar, (alto_avatar, alto_avatar), centering=(0.5, 0.5))
    avatar_redondo.putalpha(mask)
    imagen.paste(avatar_redondo, (margen, margen), avatar_redondo)

    # Insignia
    insignia = Image.open(insignia_path).resize((70, 70)).convert("RGBA")
    imagen.paste(insignia, (ancho_total - margen - 70, margen), insignia)

    x_texto = margen + alto_avatar + 10
    y_base = margen
    draw.text((x_texto, y_base), nombre, font=fuente_titulo, fill=color_texto)
    y_base += 40
    draw.text((x_texto, y_base), f"Rango: {rango}", font=fuente_texto, fill=color_texto)
    y_base += 25


    if rango in ["Root", "Gran Maestro"]:
        texto_xp = "∞ XP (∞ Nivel)"
        mostrar_barra = False
    else:
        texto_xp = f"XP: {xp} (Nivel {nivel})"
        mostrar_barra = True

    draw.text((x_texto, y_base), texto_xp, font=fuente_texto, fill=color_texto)

    
    if mostrar_barra:
        xp_max = XP_RANGOS.get(rango)
        if not xp_max or xp_max == 0:
            xp_relativa = 0
            xp_max = 1  # evitar división por cero
        else:
            xp_relativa = xp % xp_max
        largo_max = ancho_total - x_texto - margen
        largo_barra = int((xp_relativa / xp_max) * largo_max)
        alto_barra = 14
        y_barra = y_base + 25
        radio = alto_barra // 2

        draw.rounded_rectangle([x_texto, y_barra, x_texto + largo_max, y_barra + alto_barra],
                               radius=radio, fill=color_barra_bg)

        if largo_barra > 0:
            draw.rounded_rectangle([x_texto, y_barra, x_texto + largo_barra, y_barra + alto_barra],
                                   radius=radio, fill=color_barra_fg)

    imagen.save(output_path)
    return output_path


# ========================= EVENTOS Y COMANDOS ==========================
# comando para completar una bandera
@bot.command()
async def flag(ctx, *, codigo):
    codigo = codigo.strip().upper()
    user_id = str(ctx.author.id)

    # Verificación de canal (insensible a mayúsculas)
    if ctx.guild and ctx.channel.name.lower() != "enviar-flag":
        await ctx.send("❌ Este comando solo puede usarse en el canal `#enviar-flag`.")
        return

    # Intentar borrar el mensaje original del usuario
    if ctx.guild:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            try:
                await ctx.author.send("⚠️ No pude borrar tu mensaje. Por favor, elimínalo manualmente para evitar spoilers.")
            except discord.Forbidden:
                pass  # No se puede contactar al usuario

    # Cargar datos con manejo de errores
    try:
        perfiles = cargar_datos(PERFILES_PATH)
        flags = cargar_datos(FLAGS_PATH)
    except FileNotFoundError:
        try:
            await ctx.author.send("⚠️ No se pudo acceder a los datos necesarios.")
        except discord.Forbidden:
            pass
        return

    if codigo not in flags:
        try:
            await ctx.author.send("❌ Flag no válida.")
        except discord.Forbidden:
            pass
        return

    # Datos de la flag
    flag_data = flags[codigo]
    nombre_flag = flag_data["nombre"]
    xp_base = flag_data["xp"]
    rango_flag = flag_data.get("rango", "F")

    # Crear perfil si no existe
    if user_id not in perfiles:
        perfiles[user_id] = {"xp": 0, "flags": [], "rango": "F"}

    if nombre_flag in perfiles[user_id]["flags"]:
        try:
            await ctx.author.send("⚠️ Ya has enviado esta flag.")
        except discord.Forbidden:
            pass
        return

    # Comparar rango del usuario con el de la flag
    RANGOS = ["F", "E", "D", "C", "B", "A", "S", "SS", "SSS"]
    rango_usuario = perfiles[user_id].get("rango", "F")

    try:
        idx_usuario = RANGOS.index(rango_usuario)
        idx_flag = RANGOS.index(rango_flag)
    except ValueError:
        idx_usuario = idx_flag = 0  # Fallback por seguridad

    # Cálculo de XP con bonificaciones
    if idx_usuario < idx_flag:
        xp_final = int(xp_base * 1.2)
        detalle = " (+20% bonus por menor rango)"
    elif idx_usuario > idx_flag:
        xp_final = int(xp_base * 0.8)
        detalle = " (–20% por mayor rango)"
    else:
        xp_final = xp_base
        detalle = ""

    # Registrar flag y XP
    perfiles[user_id]["xp"] += xp_final
    perfiles[user_id]["flags"].append(nombre_flag)
    await actualizar_rango_y_rol(ctx.author, perfiles[user_id])
    guardar_datos(PERFILES_PATH, perfiles)

    # Enviar resultado por DM
    try:
        await ctx.author.send(f"✅ Flag aceptada: **{nombre_flag}**.\nGanaste {xp_final} XP{detalle} ✨")
    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, no pude enviarte un DM. Asegúrate de tener los mensajes privados activados.")


# comando para mostrar el perfil de un usuario
@bot.command()
async def perfil(ctx):
    try:
        usuario = str(ctx.author.id)
        perfiles = cargar_datos(PERFILES_PATH)

        if usuario not in perfiles:
            perfiles[usuario] = {"xp": 0, "rango": "F", "flags": []}
            guardar_datos(PERFILES_PATH, perfiles)

            # Asignar rol de Discord automáticamente
            rol_f = discord.utils.get(ctx.guild.roles, name="F")
            if rol_f:
                await ctx.author.add_roles(rol_f)

        perfil = perfiles[usuario]
        xp = perfil["xp"]
        nivel = xp // 100
        rango = perfil.get("rango", "F")
        nombre = ctx.author.name

        # Descargar avatar
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        response = requests.get(avatar_url)
        avatar_path = f"temp_avatar_{usuario}.png"
        with open(avatar_path, "wb") as f:
            f.write(response.content)

        # Ruta de insignia según rango
        rango_normalizado = rango.replace(" ", "")  # "Gran Maestro" → "GranMaestro"
        insignia_path = f"img/rango_{rango_normalizado}.png"
        if not os.path.exists(insignia_path):
            insignia_path = "img/rango_F.png"  # Backup por si falta imagen

        # Crear imagen
        archivo_imagen = crear_imagen_perfil(
            nombre=nombre,
            rango=rango,
            xp=xp,
            nivel=nivel,
            avatar_path=avatar_path,
            insignia_path=insignia_path,
        )

        await ctx.send(file=discord.File(archivo_imagen))

        # Limpiar archivos temporales
        os.remove(archivo_imagen)
        os.remove(avatar_path)

    except Exception as e:
        await ctx.send(f"❌ Error al generar el perfil: {e}")
        print(e)
# Comando de las reglas
@bot.command()
async def reglas(ctx):
    texto = (
        "1. 🛡️ **Honor y respeto ante todo**: Trata a todos con cortesía.\n"
        "2. 🔍 **Nada de trampas**: Las flags deben obtenerse resolviendo retos.\n"
        "3. 🗣️ **No spam, ni flood**: Cuida los canales del gremio.\n"
        "4. 🧠 **Aprende y comparte**: Ayuda a tus compañeros.\n"
        "5. ⚖️ **El Gran Maestro tiene la última palabra**: Las decisiones administrativas son finales.\n"
        "6. ❌ **No se permite magia**: Las flag las tienes que sacar tu si alguen te la chiva sera perma ban para los dos.\n"
        "7. **No a los walthougth**: solo se permiten hacer para mandarlos a los administradores para que ellos valoren tu trabajo nada mas.\n"
        "\n"
        "Cualquier violación será castigada por los guardianes del gremio."
    )
    embed = discord.Embed(
        title="📜 Reglas del Gremio",
        description=texto,
        color=0x8B4513
    )
    embed.set_footer(text="Que el código os guíe.")
    await ctx.send(embed=embed)
#comando para que los usuarios vean sus flags
@bot.command()
async def misflags(ctx):
    """Muestra las flags recogidas por el jugador."""
    profiles = cargar_datos(PERFILES_PATH)
    user_id = str(ctx.author.id)

    if user_id not in profiles or not profiles[user_id]["flags"]:
        await ctx.send("❕ Aún no tienes flags recogidas.")
        return

    flags = profiles[user_id]["flags"]  # Esto tiene NOMBRES de flags

    lista = "\n".join([f"🏁 {flag}" for flag in flags])

    embed = discord.Embed(
        title=f"Flags recogidas de {ctx.author.display_name}",
        description=lista,
        color=discord.Colour.green()
    )
    await ctx.send(embed=embed)
#comando para bajar de rango a un usuario
@bot.command()
@commands.has_permissions(administrator=True)
async def bajar_rango(ctx, miembro: discord.Member):
    RANGOS = ["F", "E", "D", "C", "B", "A", "S", "SS", "SSS"]
    roles_usuario = [r.name for r in miembro.roles]
    
    for i, rango in enumerate(RANGOS):
        if rango in roles_usuario and i > 0:
            rol_actual = discord.utils.get(ctx.guild.roles, name=RANGOS[i])
            rol_anterior = discord.utils.get(ctx.guild.roles, name=RANGOS[i - 1])
            await miembro.remove_roles(rol_actual)
            await miembro.add_roles(rol_anterior)
            await ctx.send(f"🔻 {miembro.mention} ha sido bajado de rango a `{rol_anterior.name}`.")
            return

    await ctx.send("❌ El usuario ya tiene el rango más bajo o no tiene un rango válido.")
import json
# Comando para ver las banderas activas
@bot.command()
@commands.has_permissions(administrator=True)
async def ver_flags(ctx):
    try:
        with open("flags.json", "r") as f:
            flags = json.load(f)

        if not flags:
            await ctx.send("🚫 No hay flags activas.")
            return

        mensaje = "🏁 **Flags activas:**\n\n"
        for codigo, datos in flags.items():
            nombre = datos.get("nombre", "Sin nombre")
            xp = datos.get("xp", 0)
            rango = datos.get("rango", "F")
            creador = datos.get("creador", "Desconocido")
            mensaje += f"🔹 `{codigo}` - `{nombre}` | 💠 Rango: `{rango}` | ⭐ XP: `{xp}` | 👤 Creador: `{creador}`\n"

        await ctx.send(mensaje)

    except FileNotFoundError:
        await ctx.send("❌ El archivo de flags no existe.")

# Comando para borrar baderas
@bot.command()
@commands.has_permissions(administrator=True)
async def borrar_flag(ctx, nombre_flag):
    try:
        with open("flags.json", "r") as f:
            flags = json.load(f)

        if nombre_flag in flags:
            del flags[nombre_flag]
            with open("flags.json", "w") as f:
                json.dump(flags, f, indent=4)
            await ctx.send(f"🗑️ La flag `{nombre_flag}` ha sido eliminada.")
        else:
            await ctx.send("⚠️ Esa flag no existe.")
    except FileNotFoundError:
        await ctx.send("❌ El archivo de flags no existe.")
#Comando para agregar una bandera nueva
@bot.command()
@commands.has_permissions(administrator=True)
async def agregarflag(ctx, *, argumentos):
    try:
        # Separar partes usando "|"
        parte_codigo_xp_rango, nombre = argumentos.split("|", 1)
        partes = parte_codigo_xp_rango.strip().split()

        if len(partes) < 3:
            raise ValueError("Faltan argumentos.")

        codigo = partes[0].strip().upper()
        xp = int(partes[1])
        rango = partes[2].upper()
        nombre = nombre.strip()

    except ValueError:
        await ctx.send(
            "❌ Formato incorrecto. Usa: `!agregarflag <codigo> <xp> <rango> | <nombre>`\n"
            "Ejemplo: `!agregarflag FLAG123 50 D | Desafío de decodificación`"
        )
        return

    if xp <= 0:
        await ctx.send("❌ El valor de XP debe ser un número entero positivo.")
        return

    RANGOS_VALIDOS = ["F", "E", "D", "C", "B", "A", "S", "SS", "SSS"]
    if rango not in RANGOS_VALIDOS:
        await ctx.send(f"❌ Rango no válido. Usa uno de: {', '.join(RANGOS_VALIDOS)}")
        return

    flags = cargar_datos(FLAGS_PATH)

    if codigo in flags:
        await ctx.send(
            f"⚠️ La flag `{codigo}` ya existe con el nombre `{flags[codigo]['nombre']}`. "
            "Usa otro código o elimínala primero con `!borrar_flag`."
        )
        return

    # Guardar la nueva flag
    flags[codigo] = {
        "xp": xp,
        "nombre": nombre,
        "rango": rango
    }

    guardar_datos(FLAGS_PATH, flags)

    await ctx.send(
        f"✅ Flag `{codigo}` añadida con {xp} XP, rango `{rango}` y nombre: `{nombre}`."
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def anuncio(ctx, *, mensaje):
    embed = discord.Embed(
        title="📜 Comunicado del Gran Maestro",
        description=mensaje,
        color=0x8B4513  # Marrón oscuro
    )
    embed.set_footer(text="Por el honor del gremio")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def grantmaestro(ctx, miembro: discord.Member):
    perfiles = cargar_datos(PERFILES_PATH)
    user_id = str(miembro.id)

    # Crear el rol si no existe
    rol_nombre = "Gran Maestro"
    rol = discord.utils.get(ctx.guild.roles, name=rol_nombre)
    if not rol:
        rol = await ctx.guild.create_role(name=rol_nombre)
        await ctx.send(f"🎖️ Rol `{rol_nombre}` creado.")

    # Asignar el rol
    await miembro.add_roles(rol)
    await ctx.send(f"👑 {miembro.mention} ahora es un **Gran Maestro**.")

    # Actualizar el perfil
    if user_id not in perfiles:
        perfiles[user_id] = {"xp": 0, "flags": [], "rango": "F"}

    perfiles[user_id]["rango"] = rol_nombre
    guardar_datos(PERFILES_PATH, perfiles)

@commands.has_permissions(administrator=True)
@bot.command()
async def setup_canales(ctx):
    guild = ctx.guild

    # Crear rol Gran Maestro si no existe
    rol_gm = discord.utils.get(guild.roles, name="Gran Maestro")
    if not rol_gm:
        rol_gm = await guild.create_role(name="Gran Maestro", permissions=discord.Permissions.none())
        await ctx.send("🎖 Rol `Gran Maestro` creado.")

    # Crear categoría para Gran Maestro
    categoria_gm = discord.utils.get(guild.categories, name="Gran Maestro")
    if not categoria_gm:
        categoria_gm = await guild.create_category("Gran Maestro", overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            rol_gm: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        })
        await ctx.send("📁 Categoría `Gran Maestro` creada.")

    # Crear canales de texto y voz por rango
    colores_por_rango = {
        "F": discord.Colour.from_rgb(120, 120, 120),
        "E": discord.Colour.from_rgb(90, 150, 180),
        "D": discord.Colour.from_rgb(70, 180, 90),
        "C": discord.Colour.from_rgb(255, 210, 80),
        "B": discord.Colour.from_rgb(255, 165, 0),
        "A": discord.Colour.from_rgb(255, 100, 100),
        "S": discord.Colour.from_rgb(160, 100, 255),
        "SS": discord.Colour.from_rgb(100, 200, 255),
        "SSS": discord.Colour.from_rgb(255, 255, 255)
    }

    for rango in RANGOS:
        # Crear rol
        rol = discord.utils.get(guild.roles, name=rango)
        if not rol:
            permisos = discord.Permissions()
            permisos.update(
                send_messages=True,
                read_messages=True,
                attach_files=True,
                embed_links=True,
                send_stickers=True,
                read_message_history=True
            )
            color = colores_por_rango.get(rango, discord.Colour.default())
            rol = await guild.create_role(name=rango, permissions=permisos, colour=color)
            await ctx.send(f"✅ Rol `{rango}` creado.")

        # Crear categoría
        categoria = discord.utils.get(guild.categories, name=f"Rango {rango}")
        if not categoria:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                rol: discord.PermissionOverwrite(view_channel=True),
                rol_gm: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            categoria = await guild.create_category(f"Rango {rango}", overwrites=overwrites)
            await ctx.send(f"📂 Categoría `Rango {rango}` creada.")

        # Crear canal de texto
        nombre_chat = f"{rango.lower()}-chat"
        if not discord.utils.get(guild.text_channels, name=nombre_chat):
            await guild.create_text_channel(
                nombre_chat,
                category=categoria,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    rol: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    rol_gm: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
            )

        # Crear canal de voz
        nombre_voz = f"{rango.lower()}-voz"
        if not discord.utils.get(guild.voice_channels, name=nombre_voz):
            await guild.create_voice_channel(
                nombre_voz,
                category=categoria,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    rol: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
                    rol_gm: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)
                }
            )

    # Canal: comandos-admin
    nombre_canal_admin = "comandos-admin"
    canal_admin = discord.utils.get(guild.text_channels, name=nombre_canal_admin)
    if not canal_admin:
        overwrites_admin = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            rol_gm: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        canal_admin = await guild.create_text_channel(
            nombre_canal_admin,
            overwrites=overwrites_admin,
            category=categoria_gm,
            topic="Canal para comandos administrativos del bot."
        )
        await ctx.send("🛠 Canal `comandos-admin` creado correctamente.")
    else:
        await canal_admin.edit(category=categoria_gm)

    # Canal: enviar-flag
    nombre_canal_flag = "enviar-flag"
    canal_flag = discord.utils.get(guild.text_channels, name=nombre_canal_flag)
    overwrites_flag = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_messages=False
        ),
        rol_gm: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_messages=True,
            read_message_history=True
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_messages=True,
            read_message_history=True
        )
    }
    if not canal_flag:
        await guild.create_text_channel(
            nombre_canal_flag,
            overwrites=overwrites_flag,
            topic="Escribe tu flag aquí. No podrás ver tu mensaje."
        )
        await ctx.send("📤 Canal `enviar-flag` creado correctamente.")
    else:
        await canal_flag.edit(overwrites=overwrites_flag)

    await ctx.send("✅ Todos los canales, categorías y roles han sido configurados correctamente.")
    
    # Crear canal de comandos para todos
    canal_comandos = discord.utils.get(guild.text_channels, name="comandos")
    if not canal_comandos:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                send_messages=True, view_channel=True, read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        canal_comandos = await guild.create_text_channel("comandos", overwrites=overwrites)

@bot.command(hidden=True)
@commands.has_permissions(administrator=True)
async def grantroot(ctx, miembro: discord.Member):
    guild = ctx.guild
    perfiles = cargar_datos(PERFILES_PATH)
    user_id = str(miembro.id)
    rol_nombre = "Root"

    # Crear rol si no existe
    rol = discord.utils.get(guild.roles, name=rol_nombre)
    if not rol:
        try:
            rol = await guild.create_role(name=rol_nombre, colour=discord.Colour.red())
            await ctx.send(f"🎖️ Rol `{rol_nombre}` creado.")
        except discord.Forbidden:
            return await ctx.send("❌ No tengo permisos para crear roles.")
        except discord.HTTPException as e:
            return await ctx.send(f"❌ Error al crear el rol: {e}")

    # Asignar rol si no lo tiene
    if rol not in miembro.roles:
        await miembro.add_roles(rol)
        await ctx.send(f"👑 {miembro.mention} ahora es un **Root**.")
    else:
        await ctx.send(f"⚠️ {miembro.mention} ya tiene el rol **Root**.")

    # Actualizar perfil
    if user_id not in perfiles:
        perfiles[user_id] = {"xp": 0, "flags": [], "rango": "F"}

    perfiles[user_id]["rango"] = rol_nombre
    guardar_datos(PERFILES_PATH, perfiles)

# ======================== DESAFIOS ===========================
@bot.command()
@commands.has_permissions(administrator=True)
async def agregar_desafio(ctx, codigo, nombre, xp: int, rango, empieza, expira, *, descripcion):
    try:
        # Validaciones
        codigo = codigo.strip().upper()
        nombre = nombre.strip()
        rango = rango.strip().upper()

        # Verificar formato de fecha
        datetime.strptime(empieza, "%Y-%m-%d")
        datetime.strptime(expira, "%Y-%m-%d")

        # Cargar y guardar desafío
        desafios = cargar_datos(DESAFIOS_PATH)

        desafios[codigo] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "xp": xp,
            "rango": rango,
            "empieza": empieza,
            "expira": expira
        }

        guardar_datos(DESAFIOS_PATH, desafios)
        await ctx.send(
            f"✅ Desafío **{nombre}** (`{codigo}`) agregado correctamente.\n"
            f"🕓 Vigencia: {empieza} → {expira}"
        )

    except ValueError:
        await ctx.send(
            "❌ Formato incorrecto. Asegúrate de usar el comando así:\n\n"
            "**!agregar_desafio `<codigo>` `<nombre>` `<xp>` `<rango>` `<empieza>` `<expira>` `<descripción>`**\n\n"
            "**Ejemplo:**\n"
            "`!agregar_desafio FLAG123 \"Caza del Hacker\" 200 B 2025-06-20 2025-06-27 Descubre al atacante oculto en los logs.`"
        )

@bot.command()
async def desafio(ctx, *, codigo):
    codigo = codigo.strip().upper()
    user_id = str(ctx.author.id)

    desafios = cargar_datos(DESAFIOS_PATH)
    perfiles = cargar_datos(PERFILES_PATH)

    if codigo not in desafios:
        await ctx.author.send("❌ Desafío no válido.")
        return

    desafio_data = desafios[codigo]
    ahora = datetime.now()
    fecha_empieza = datetime.strptime(desafio_data["empieza"], "%Y-%m-%d")
    fecha_expira = datetime.strptime(desafio_data["expira"], "%Y-%m-%d")

    if ahora < fecha_empieza:
        dias_faltan = (fecha_empieza - ahora).days
        await ctx.author.send(f"🕓 Este desafío aún no está disponible. Comienza en {dias_faltan} días.")
        return

    if ahora > fecha_expira:
        await ctx.author.send("⚠️ Este desafío ha expirado.")
        return

    if user_id not in perfiles:
        perfiles[user_id] = {"xp": 0, "flags": [], "rango": "F", "desafios": []}

    if "desafios" not in perfiles[user_id]:
        perfiles[user_id]["desafios"] = []

    if codigo in perfiles[user_id]["desafios"]:
        await ctx.author.send("⚠️ Ya has completado este desafío.")
        return

    perfiles[user_id]["xp"] += desafio_data["xp"]
    perfiles[user_id]["desafios"].append(codigo)
    guardar_datos(PERFILES_PATH, perfiles)

    await ctx.author.send(f"✅ Desafío completado: **{desafio_data['nombre']}**. Ganaste {desafio_data['xp']} XP ✨")

@bot.command()
async def desafios(ctx):
    desafios = cargar_datos(DESAFIOS_PATH)
    mensaje = "**📌 Desafíos activos y próximos:**\n\n"
    ahora = datetime.now()

    for codigo, data in desafios.items():
        nombre = data["nombre"]
        descripcion = data.get("descripcion", "Sin descripción.")
        fecha_empieza = datetime.strptime(data["empieza"], "%Y-%m-%d")
        fecha_expira = datetime.strptime(data["expira"], "%Y-%m-%d")

        if ahora > fecha_expira:
            continue

        if ahora < fecha_empieza:
            dias_faltan = (fecha_empieza - ahora).days
            mensaje += f"🔒 **{nombre}**\n"
            mensaje += f"🔸 {descripcion}\n"
            mensaje += f"🕓 Disponible en: {dias_faltan} días (del {fecha_empieza.date()} al {fecha_expira.date()})\n\n"
        else:
            dias_restantes = (fecha_expira - ahora).days
            mensaje += f"🧩 **{nombre}** (`{codigo}`)\n"
            mensaje += f"🔸 {descripcion}\n"
            mensaje += f"⏳ Termina en: {dias_restantes} días (hasta el {fecha_expira.date()})\n\n"

    await ctx.send(mensaje or "No hay desafíos activos ni programados.")

# ========================= TOKEN ==============================

if __name__ == "__main__":
    import os
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("⚠️ Token no encontrado. Usa la variable de entorno DISCORD_TOKEN")