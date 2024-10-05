This is a discord bot built to remind alliance members in [Last War:Survival Game.](https://play.google.com/store/apps/details?id=com.fun.lastwar.gp&hl=en_US&pli=1)

Reminders are currently just for VS day tasks.

To get started clone the repo and create a new environment. Here we will be using an enviorment manager from base python.

```python -m venv .```

Activate the enviroment, its will be a bit different depending on your operating system and which enviorment manager you use.

Install poetry. https://python-poetry.org/

```pip install poetry```

install the necessary packages to run the bot using

```poetry install```

You will also need to make 2 files ```server_info.toml``` and ```.secret```

server_info.toml is:

```rules_url = "discord_website_to_rules_message"
annoncement_channel_id = SOME_INT
welcome_channel_id = SOME_INT
allliance_initals = "SOME_3_LENGTH_INITIALS"
alliance_name = "SOME_NAME"
last_war_server = SOME_INT
```

you will also need to download googleCLI, get an api key and it set `GEMINI_API_KEY` environment variable.
https://cloud.google.com/sdk/docs/install
after installing you will need to set up a project and get an api key to set environment variable.


.secret is just a string containing the discord bot token that allows the bot to run.
https://discordgsm.com/guide/how-to-get-a-discord-bot-token

Steps on how to add discord bot.
https://discordpy.readthedocs.io/en/stable/discord.html
