import discord, json, os
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
    print('{}: {}'.format(client.user.name, client.user.id))
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
        await ctx.message.delete(delay=2)
        await bot_msg.delete(delay=2)
    else:
        await ctx.send()

    with open("channels.json", "w") as w:
        json.dump(channels, w, indent=4, sort_keys=True)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"No tienes permiso para ejecutar este comando, hace falta el permiso de Administrador para poder ejecutar este comando. :confused:")

def check_channel(ctx):
    with open("channels.json") as r:
        channels = json.loads(r.read())
    return ctx.channel.id == channels[str(ctx.guild.id)]

@client.command()
@commands.check(check_channel)
async def private(ctx, *, name):
    with open("channels.json") as r:
        channels = json.loads(r.read())

    channel = await client.fetch_channel(channels[str(ctx.guild.id)])
    await ctx.message.delete(delay=2)
    new = await ctx.guild.create_voice_channel(name=name, category=channel.category)
    try:
        await new.set_permissions(ctx.author, read_messages=True, connect=True)
        await new.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)
        created_msg = await ctx.send("Canal creado")
        await created_msg.delete(delay=2)
    except discord.Forbidden:
        perms_msg = await ctx.send("Me faltan permisos")
        perms_msg.delete(delay=2)

@client.command(hidden=True)
@commands.check(commands.is_owner())
async def logout(ctx):
    msg = await ctx.send('Desconectando...')
    await msg.delete(delay=2)
    await client.logout()

keep_alive()
client.run(os.environ.get("token"))
