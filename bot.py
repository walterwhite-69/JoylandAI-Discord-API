import discord
from discord import app_commands
from client import JoylandClient
import os
import json
import asyncio

class JoylandBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.user_sessions = {}
        self.active_channels = {}
        self.sessions_file = "sessions.json"

    def save_sessions(self):
        data = {}
        for user_id, session in self.user_sessions.items():
            data[str(user_id)] = {
                "token": session["client"].token,
                "fingerprint": session["client"].fingerprint,
                "user_agent": session["client"].user_agent
            }
        with open(self.sessions_file, "w") as f:
            json.dump(data, f)

    async def load_sessions(self):
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, "r") as f:
                    data = json.load(f)
                for user_id_str, session_data in data.items():
                    user_id = int(user_id_str)
                    client = JoylandClient()
                    client.token = session_data["token"]
                    client.fingerprint = session_data["fingerprint"]
                    client.user_agent = session_data["user_agent"]
                    client.client.headers["authtoken"] = client.token
                    client.client.headers["fingerprint"] = client.fingerprint
                    client.client.headers["user-agent"] = client.user_agent
                    self.user_sessions[user_id] = {"client": client, "dialogues": {}, "current_bot": None}
                print(f"Loaded {len(self.user_sessions)} sessions from {self.sessions_file}")
            except Exception as e:
                print(f"Error loading sessions: {e}")

    async def setup_hook(self):
        print("Synchronizing commands...")
        await self.tree.sync()
        print("Commands synchronized.")
        await self.load_sessions()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Bot is ready and listening for events!")
        print("------")

bot = JoylandBot()

class SearchView(discord.ui.View):
    def __init__(self, interaction, keyword, client):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.keyword = keyword
        self.client = client
        self.page = 1
        self.results = []
        self.current_slice = []

    async def update_embed(self):
        data = await self.client.search(self.keyword, page=self.page, size=5)
        if data.get("code") == "0" and not data.get("result", {}).get("records", []):
            original_token = self.client.client.headers.get("authtoken")
            if original_token:
                self.client.client.headers["authtoken"] = ""
                guest_data = await self.client.search(self.keyword, page=self.page, size=5)
                self.client.client.headers["authtoken"] = original_token
                if guest_data.get("code") == "0" and guest_data.get("result", {}).get("records", []):
                    data = guest_data

        if data.get("code") == "0":
            self.current_slice = data.get("result", {}).get("records", [])
            
            if not self.current_slice and self.page > 1:
                self.page -= 1
                return await self.update_embed()
            
            embeds = []
            
            if not self.current_slice:
                 main_embed = discord.Embed(title=f"Search: {self.keyword} (Page {self.page})", color=discord.Color.blue())
                 main_embed.description = "No characters found."
                 embeds.append(main_embed)
            else:
                 for i, b in enumerate(self.current_slice):
                     name = b.get("characterName") or b.get("botName") or b.get("name") or "Unknown"
                     intro = b.get("introduce") or b.get("botIntroduction") or b.get("intro") or "No intro"
                     if len(intro) > 120:
                         intro = intro[:117] + "..."
                     
                     bot_id = b.get("id") or b.get("botId") or "No ID"
                     avatar = b.get("avatar") or b.get("botAvatar") or b.get("appBackgroundUrl")
                     chats = b.get("botChats", "0")
                     
                     char_embed = discord.Embed(
                         title=f"{i+1}. {name}",
                         description=f"{intro}\n\n💬 **{chats}** chats",
                         color=discord.Color.blurple()
                     )
                     if avatar:
                         char_embed.set_thumbnail(url=avatar)
                     embeds.append(char_embed)
            
            await self.interaction.edit_original_response(embeds=embeds, attachments=[], view=self)
        else:
            await self.interaction.edit_original_response(content=f"Search error: {data.get('message')}", embeds=[], view=None)

    @discord.ui.button(label="1", style=discord.ButtonStyle.success)
    async def select_1(self, it, btn): await self.select(it, 0)
    @discord.ui.button(label="2", style=discord.ButtonStyle.success)
    async def select_2(self, it, btn): await self.select(it, 1)
    @discord.ui.button(label="3", style=discord.ButtonStyle.success)
    async def select_3(self, it, btn): await self.select(it, 2)
    @discord.ui.button(label="4", style=discord.ButtonStyle.success)
    async def select_4(self, it, btn): await self.select(it, 3)
    @discord.ui.button(label="5", style=discord.ButtonStyle.success)
    async def select_5(self, it, btn): await self.select(it, 4)

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.secondary)
    async def prev_page(self, it, btn):
        if self.page > 1:
            self.page -= 1
            await it.response.defer()
            await self.update_embed()
        else: await it.response.send_message("First page!", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, it, btn):
        self.page += 1
        await it.response.defer()
        await self.update_embed()

    async def select(self, it, index):
        if index >= len(self.current_slice):
            return await it.response.send_message("Invalid selection.", ephemeral=True)
        
        perms = it.channel.permissions_for(it.guild.me)
        if not perms.manage_webhooks:
            return await it.response.send_message("Error: I need the **Manage Webhooks** permission in this channel to create an immersive chat!", ephemeral=True)

        await it.response.defer(ephemeral=True)
        selected = self.current_slice[index]
        bot_id = selected.get("id") or selected.get("botId")
        name = selected.get("characterName") or selected.get("botName") or selected.get("name") or "Unknown"
        avatar = selected.get("avatar") or selected.get("botAvatar") or selected.get("appBackgroundUrl")
        
        entry = await self.client.enter_dialogue(bot_id)
        if entry.get("code") == "0":
            dialogue_id = entry.get("result", {}).get("dialogueId")
            
            webhook = None
            try:
                hooks = await it.channel.webhooks()
                for h in hooks:
                    if h.name == "Joyland-Chat":
                        webhook = h
                        break
                if not webhook:
                    webhook = await it.channel.create_webhook(name="Joyland-Chat")
            except discord.Forbidden:
                return await it.followup.send("Error: Missing permissions to manage webhooks.", ephemeral=True)
            
            bot.active_channels[it.channel.id] = {
                "webhook": webhook,
                "dialogue_id": dialogue_id,
                "client": self.client,
                "bot_name": name,
                "bot_avatar": avatar
            }
            
            history = await self.client.get_chat_history(dialogue_id, limit=1)
            result = history.get("result", {})
            msgs = result if isinstance(result, list) else result.get("list", [])
            greeting = "Hello!"
            if msgs: greeting = msgs[0].get("content", "Hello!")
            
            try:
                await webhook.send(content=greeting, username=name, avatar_url=avatar)
                await it.followup.send(f"Selected **{name}**. You can now chat simply by typing in this channel!", ephemeral=True)
            except discord.Forbidden:
                await it.followup.send("Error: I joined the chat but couldn't send the greeting via webhook. Check channel permissions.", ephemeral=True)
        else:
            await it.followup.send(f"Error selecting bot: {entry.get('message')}", ephemeral=True)

@bot.tree.command(name="login", description="Login to Joyland AI")
async def login(interaction: discord.Interaction, email: str, password: str):
    await interaction.response.defer(ephemeral=True)
    client = JoylandClient()
    success, resp = await client.login(email, password)
    
    if success:
        bot.user_sessions[interaction.user.id] = {"client": client, "dialogues": {}, "current_bot": None}
        bot.save_sessions()
        await interaction.followup.send(f"✅ **Login Successful!**\nLogged in as **{email}**", ephemeral=True)
    else:
        error_msg = resp.get('message', 'Unknown Error')
        await interaction.followup.send(f"❌ **Login Failed!**\n{error_msg}\n\n*Note: Please ensure you are already registered on Joyland.ai .*", ephemeral=True)
        await client.close()

@bot.tree.command(name="search", description="Search for Joyland bots")
async def search(interaction: discord.Interaction, keyword: str):
    await interaction.response.defer()
    if interaction.user.id not in bot.user_sessions:
        return await interaction.followup.send("Login first!", ephemeral=True)
    
    view = SearchView(interaction, keyword, bot.user_sessions[interaction.user.id]["client"])
    await view.update_embed()

@bot.tree.command(name="delete", description="Remove the character webhook from this channel")
async def delete(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.channel.id in bot.active_channels:
        data = bot.active_channels.pop(interaction.channel.id)
        webhook = data["webhook"]
        try:
            await webhook.delete(reason="Joyland chat deactivated")
            await interaction.followup.send("Character chat deactivated and webhook deleted.")
        except discord.Forbidden:
            await interaction.followup.send("Character chat deactivated. (Note: I couldn't delete the webhook due to missing permissions).")
        except discord.NotFound:
            await interaction.followup.send("Character chat deactivated.")
    else:
        await interaction.followup.send("No active Joyland chat in this channel.", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id in bot.active_channels:
        data = bot.active_channels[message.channel.id]
        
        perms = message.channel.permissions_for(message.guild.me)
        if not perms.send_messages: return
        
        try:
            response = await data["client"].send_message(data["dialogue_id"], message.content)
            if response:
                await data["webhook"].send(content=response, username=data["bot_name"], avatar_url=data["bot_avatar"])
            else:
                await message.reply("Character is silent or there was an error.")
        except discord.Forbidden:
            await message.reply("Error: I lack permissions to send messages or use webhooks in this channel.")
        except discord.NotFound:
            await message.reply("Error: The active webhook was deleted. Please re-select the character using `/search`.")
            bot.active_channels.pop(message.channel.id, None)

if __name__ == "__main__":
    token = "DISCORD_TOKEN"
    if token == "YOUR_DISCORD_BOT_TOKEN":
        print("!!! ERROR: Discord Token not found. !!!")
        print("Please set your token in bot.py or as an environment variable 'DISCORD_TOKEN'.")
    else:
        try:
            bot.run(token)
        except discord.LoginFailure:
            print("!!! ERROR: Invalid Discord Token provided. !!!")
