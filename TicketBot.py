import discord, os
from datetime import datetime
from discord import app_commands, utils
from discord.ext import commands

class ticket_launcher(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 600, commands.BucketType.member)

    @discord.ui.button(label = "Create a Ticket", style = discord.ButtonStyle.blurple, custom_id = "ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()
        if retry: return await interaction.response.send_message(f"Riprova tra {round(retry, 1)} secondi!", ephemeral = True)
        ticket = utils.get(interaction.guild.text_channels, name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}")
        if ticket is not None: await interaction.response.send_message(f"Hai già un ticket aperto {ticket.mention}!", ephemeral = True)
        else:
            if type(client.ticket_mod) is not discord.Role:
                client.ticket_mod = interaction.guild.get_role(1051562493887139960) #ruolo
            overwirtes = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                client.ticket_mod: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True, attach_files = True, embed_links = True)
            }
            try: channel = await interaction.guild.create_text_channel(name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}", overwrites = overwirtes, reason = f"Ticket for {interaction.user}")
            except: return await interaction.response.send_message("LA creazione del ticket è fallita! Assicurati di avere il permesso di 'manage_channels'!", ephemeral = True)
            await channel.send(f"{client.ticket_mod.mention}, {interaction.user.mention} created a ticket!", view = main())
            await interaction.response.send_message(f"I've opened a ticket for u at {channel.mention}!", ephemeral=True) 

class confirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Conferma", style = discord.ButtonStyle.red, custom_id = "confirm")
    async def confirm_button(self, interaction, button):
        try: await interaction.channel.delete()
        except: await interaction.response.send_message("Channel deletion failed! Make sure i have 'manage_channals' permission!", ephemeral = True)

class main(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Chiudi Ticket", style = discord.ButtonStyle.red, custom_id = "close")
    async def close(self, interaction, button):
        embed = discord.Embed(title = "Sei sicuro di voler chiudere il ticket?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.default())
        self.synced = False 
        self.added = False
        self.ticket_mod = 1051562493887139960 #ruolo

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=1051562083260579992)) #server
            self.synced = True
        if not self.added:
            self.add_view(ticket_launcher())
            self.add_view(main())
            self.added = True
        print("Loggato come {self.user}!")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(guild = discord.Object(id=1051562083260579992), name = 'ticket', description='Launches the ticketing system') #server
@app_commands.default_permissions(manage_guild = True)
@app_commands.checks.cooldown(3, 60, key = lambda i: (i.guild_id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(description = "• Select in the **MENU** below the category according to your need.",  color = discord.Colour.blue())
    embed.set_image(url="https://cdn.discordapp.com/attachments/961333221499469844/996032547135959090/open_a_ticket.png")
    embed.set_footer(text='Lil Keef © 2022', icon_url="https://cdn.discordapp.com/attachments/965727196524191765/1020007438017122305/unknown.png")
    embed.set_author(name="lil keef | Ticket", icon_url="https://cdn.discordapp.com/attachments/965727196524191765/1020007438017122305/unknown.png")
    await interaction.channel.send(embed = embed, view= ticket_launcher())
    await interaction.response.send_message("I am working! I was made with Discord.py!", ephemeral=True)

@tree.command(guild = discord.Object(id=1051562083260579992), name = 'close', description='Chiudi il ticket')#server
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def close(interaction: discord.Interaction):
    if "ticket-for-" in interaction.channel.name:
        embed = discord.Embed(title = "Sei sicuro di voler chiudere il ticket?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)
    else: await interaction.response.send_message("Questo non è un ticket!", ephemeral = True)

@tree.command(guild = discord.Object(id=1051562083260579992), name = 'add', description='Aggiungi utente al ticket') #server
@app_commands.default_permissions(manage_guild = True)
@app_commands.checks.cooldown(3, 20, key = lambda i: (i.guild_id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
@app_commands.describe(user = "The user you want to add to the ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel = True, send_messages = True, attach_files = True, embed_links = True)
        await interaction.response.send_message(f"{user.mention} è stato aggiunto al ticket da {interaction.user.mention}!")
    else: await interaction.response.send_message("Questo non è un ticket!", ephemeral = True)

@tree.command(guild = discord.Object(id=1051562083260579992), name = 'remove', description='Rimuovi utente dal ticket') #server
@app_commands.default_permissions(manage_guild = True)
@app_commands.checks.cooldown(3, 20, key = lambda i: (i.guild_id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
@app_commands.describe(user = "The user you want to remove to the ticket")
async def remove(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        if type(client.ticket_mod) is not discord.Role: client.ticket_mod = interaction.guild.get_role(1051562493887139960) #ruolo
        if client.ticket_mod not in interaction.user.roles:
            return await interaction.response.send_message("Non puoi farlo!", ephemeral = True)
        if client.ticket_mod not in user.roles:
            await interaction.channel.set_permissions(user, overwrite = None)
            await interaction.channel.send_message(f"{user.mention} è stato rimosso dal ticket da {interaction.user.mention}!", ephemeral = True)
        else: await interaction.response.send_message(f"{user.mention} è un moderatore non puoi rimuoverlo da ticket!", ephemeral = True)
    else: await interaction.response.send_message("Questo non è un ticket!", ephemeral = True)
    
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(error, ephemeral=True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        return await interaction.response.send_message(error, ephemeral=True)
        raise error


client.run('TOKEN HERE')