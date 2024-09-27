import asyncio
import discord
from discord.ext import commands
import pendulum
import helper
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)
server_info = helper.read_server_info()
token = helper.read_token()


async def send_message_to_channel(channel, message):
    channel_id = server_info[channel]
    logging.info(f"Sending {message} to channel {channel_id}")
    channel = client.get_channel(channel_id)

    await channel.send(message)

@client.event
async def on_member_join(member):
    logging.info(f"New member has joined: {member.name}")

    rules_url = server_info['rules_url']

    message = f"Welcome to the server, {member.mention}!\n"
    message += f"Please read familarize yourself with the [rules]({rules_url})"
    
    logging.info(f"sending the welcome message: {message} ")

    await send_message_to_channel("welcome_channel",message)

async def vs_day_reminder():
    logging.info("vs_day_reminder has been triggered.")
    vs_day_reminders = helper.read_vs_day_toml()
    current_time = pendulum.now()
    logging.info(f"vs_day_reminder was triggered on {current_time.to_datetime_string}")

    for vs_day_key, vs_day_info in vs_day_reminders.items():
        day_of_week_match_check = (
            helper.days_of_week[current_time.day_of_week] == vs_day_info["day"]
        )

        if day_of_week_match_check:
            message = (
                f"# It is now day {vs_day_key[-1]} aka {vs_day_info['name']}.\n"
            )
            message += "## Perform the following tasks to earn points:\n"
            message += f"""{helper.combine_vs_messages(vs_day_info["tasks"])}"""
            message += "## Some tips for this day:\n"
            message += f"""{helper.combine_vs_messages(vs_day_info["tips"])}"""
            message += "## Some reminders for upcoming days:\n"
            message += f"""{helper.combine_vs_messages(vs_day_info["reminders"])}"""
            message += "### For questions and a complete guide please visit [vs-tournament-tips-info](https://discord.com/channels/1263660916994478120/1264795050941091941)"
            break
    try:
        logging.info(f"sending {message}")
        await send_message_to_channel("annoncement_channel_id", message)
    except Exception as error:
        logging.error(f"Failed to send {message} because: {error}")
    await asyncio.sleep(61)

async def marshal_reminder():
    message = "# Alliance Exercise (Marshal) will begin soon.\n"
    message += "## Stop your rallies and prepare to only join/start Marshal rallies only.\n"
    message += "1. Only join rallies with a 2.5% or a 5% bonus if your squad power is greater than 5 million.\n"
    message += "2. Start rallies with your B/C squad and join rallies with your other squads.\n"
    message += "3. When we reach level 5 you may join any rally and you may stop. You should continue if you believe you can achieve the next tier of rewards. However, we do ask that you continue to send rallies so offline members may join.\n"

    await send_message_to_channel("annoncement_channel_id", message)

@client.event
async def on_ready():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(vs_day_reminder, 'cron', hour=22, minute=0)
    scheduler.add_job(marshal_reminder, CronTrigger(day_of_week='sun,tue,thu', hour=22, minute=10))
    scheduler.start()

client.run(token)
