<p align="center">
  <img src="https://www.joyland.ai/assets/logo-large-dark-tl_aFfQx.svg" alt="Anime Kai Logo" width="200"/>
</p>


<div align="center">
  <h1>🤖 JoylandAI Discord Bot API</h1>
  <p>A sophisticated, fully-featured unofficial Discord integration for Joyland AI.</p>

  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
  [![Discord](https://img.shields.io/badge/Discord.py-2.4.0-purple.svg)](https://discordpy.readthedocs.io/)
  [![Joyland](https://img.shields.io/badge/Joyland-API-FF6B6B.svg)](https://joyland.ai)
</div>

<br>

Welcome to the **JoylandAI Discord Bot**, an immersive and intuitive way to bring Joyland's engaging characters directly into your Discord servers! This bot securely connects to Joyland AI, allowing seamless searching, immersive webhook-powered side-by-side chatting, and robust session persistence.



## ✨ Features

- 🎭 **Immersive Webhook Chat**: Characters reply dynamically through Discord Webhooks using their real names and avatars. It directly mimics the Joyland conversational UI right inside your channel.
- 🔐 **Persistent, Stealthy Sessions**: Every user enjoys a completely isolated session with locally saved credentials (`sessions.json`). Features dynamically randomized fingerprints and User-Agent cycling.
- 🎨 **Beautiful UI**: Paginated search interfaces using beautiful, responsive Discord Embeds powered by native UI Views and Buttons.
- ⚡ **Asynchronous & Fast**: Powered by `httpx` and `asyncio` for zero-blocking, high-speed API communication with Joyland.
- 🛠️ **Deep Diagnostic Debugging**: Detailed API response insights directly embedded inside Discord for seamless troubleshooting.

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- A Discord Developer Application (Bot Token)

### 1. Clone & Install Dependencies
Clone the repository and install the standard dependencies:
```bash
pip install discord httpx
```

### 2. Configure Your Bot Token
Open `bot.py` and replace the placeholder `YOUR_DISCORD_BOT_TOKEN` at the very bottom of the file with your active Discord Bot Token.

Alternatively, you could extend the logic to load from an environment variable:
```python
token = os.environ.get("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN")
```

### 3. Required Discord Permissions
In the Discord Developer Portal, ensure your bot has the following privileges enabled:
- **Message Content Intent** (Required)

When inviting the bot to your server, allow these permissions:
- `Send Messages`
- `Manage Webhooks` (Crucial for the immersive character roleplay features)
- `Use Application Commands` (Slash commands)
- `Embed Links`

### 4. Blast Off!
Launch the bot from your terminal:
```bash
python bot.py
```

## 💻 Usage

### `/login <email> <password>`
Authenticate directly with your Joyland AI account. Your session token is safely cached locally, meaning you only need to run this command once!

### `/search <keyword>`
Look up any character available on the platform. The bot will return an interactive, paginated list. Select the character you want to converse with by clicking their assigned number `[1-5]`.

### `/delete`
Once you have spawned a character in a specific channel, use this command to clear the webhook and terminate the conversation binding, allowing the channel to return to normal operation.

## ⚙️ Architecture

- `client.py` - Core Async API Wrapper for Joyland. Handles authentication hooks, browser fingerprinting, streamed web-socket chunk reconstruction, and chat histories.
- `bot.py` - The Discord presentation layer. Manages active UI interactions, caching/saving user sessions, permission checks, and intelligent API feedback.

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome! Feel free to check the [issues page](../../issues) if you want to contribute. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Issues & Feedback

Encountered a bug, have a suggestion, or want to add a new feature? 
Please open an issue on the GitHub repository providing as much context as possible (e.g., error logs, Discord permissions, or feature specifications).

---

## 📜 Disclaimer & Acknowledgments

This is an **unofficial** third-party integration created for educational and API research purposes. Special thanks to [walterwhite-69](https://github.com/walterwhite-69/JoylandAI-Discord-API) for the inspiration and foundational API exploration!

Please abide by Discord's ToS and Joyland's EULA when utilizing this integration.
