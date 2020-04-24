import discord, json, os, asyncio
from discord.ext import commands
from keep_alive import keep_alive

prefix = "."

client = commands.Bot(command_prefix=prefix)
client.remove_command('help')

def check(msg):
    return msg.channel_mentions

@client.event
async def on_ready():
    print('Connected as:')
    print(f"{client.user.name}: {client.user.id}")
    print(f'Prefix: {prefix}')
    print('--------------')

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! ||({round(client.latency*1000)}ms)||")

@client.command(alias="Help")
async def help(ctx):
    embed = discord.Embed(title="Comandos disponibles", description="By Mr. Appu")
    embed.add_field(name="***help**", value="Muestra este mensaje", inline=False)
    embed.add_field(name="***setup #canal**", value="Establece el canal para solicitar el canal de voz privado", inline=False)
    embed.add_field(name="***private <nombre del canal>**", value="Crea un canal privado solo para ti **(No hace falta poner los <>)**", inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/695245417587277915/0db0457b04f888b54c77daf4ac7138ff.webp?size=256")
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, canal: discord.TextChannel = None):
    if canal:
        with open("channels.json") as r:
            channels = json.loads(r.read())
            channels[str(ctx.guild.id)] = canal.id

        bot_msg = await ctx.send(f"Canal establecido a {canal.name}")
    else:
        await ctx.send()

    with open("channels.json", "w") as w:
        json.dump(channels, w, indent=4, sort_keys=True)

    await ctx.message.delete(delay=2)
    await bot_msg.delete(delay=2)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"No tienes permiso para ejecutar este comando, hace falta el permiso de Administrador para poder ejecutar este comando. :confused:")

@client.command()
async def private(ctx, *, name):
    with open("channels.json") as r:
        channels = json.loads(r.read())

    channel = await client.fetch_channel(channels[str(ctx.guild.id)])
    if ctx.channel.id != channels[str(ctx.guild.id)]:
        await ctx.send(f"Por favor, manda el mensaje en el canal correspondiente! {channel.mention}")
        return

    new = await ctx.guild.create_voice_channel(name=name, reason=f"Solicitado por {ctx.author.name}#{ctx.author.discriminator}")

    if channel.category is not None:
        await new.edit(category=channel.category)

    try:
        await new.set_permissions(ctx.author, read_messages=True, connect=True)
        await new.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)
        created_msg = await ctx.send("Canal creado")
        await created_msg.delete(delay=2)
        await ctx.message.delete(delay=2)
    except discord.Forbidden:
        perms_msg = await ctx.send("Me faltan permisos")
        await new.delete(reason="Permiso de modificar roles y modificar canales necesario para establecer los permisos del canal")
        perms_msg.delete(delay=2)

@private.error
async def private_error(ctx, error):
    print((ctx.guild.name, error))
    await ctx.send("Hace falta usar el comando `.setup` entes de este!\n(Para más información escribe `.help`)")

@client.command(hidden=True)
@commands.check(commands.is_owner())
async def botinfo(ctx):
    info = await client.application_info()
    embed = discord.Embed(title=f"Información sobre {client.user.name}", description="By Mr. Appu", color=0x2c2f33, author=ctx.author)
    embed.set_thumbnail(url=client.user.avatar_url)
    embed.add_field(name="Latencia:", value=round(client.latency*1000))
    embed.add_field(name="Número de servidores:", value=len(client.guilds))
    embed.add_field(name="Caché lista?", value=client.is_ready())
    embed.add_field(name="Id del propietario:", value=info.owner.id)
    embed.add_field(name="Equipo:", value=info.team.name)
    embed.add_field(name="Bot público?", value=info.bot_public)
    embed.add_field(name="ID:", value=info.id)
    # embed.add_field(name="", value=)
    # embed.add_field(name="", value=)
    # embed.add_field(name="", value=)
    # embed.add_field(name="", value=)
    # embed.add_field(name="", value=)

    await ctx.send(embed=embed)

@client.command(hidden=True)
@commands.check(commands.is_owner())
async def logout(ctx):
    msg = await ctx.send('Desconectando...')
    await msg.delete(delay=2)
    await client.logout()

keep_alive()
client.run(os.environ.get("token"))
