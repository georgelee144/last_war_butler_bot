import asyncio
import discord
from discord.ext import commands
import pendulum
import helper
from apscheduler.schedulers.asyncio import AsyncIOScheduler

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)
server_info = helper.read_server_info()
token = helper.read_token()


async def send_message_to_channel(channel, message):
    channel_id = server_info[channel]
    channel = client.get_channel(channel_id)

    await channel.send(message)

@client.event
async def on_member_join(member):
    print(f"New member joined: {member.name}")
    general_channel = client.get_channel(server_info["welcome_channel"])
    if general_channel:
        await general_channel.send(f"Welcome to the server, {member.mention}! 👋")
    else:
        print("Error: Could not find the general channel.")

async def vs_day_reminder():
    vs_day_reminders = helper.read_vs_day_toml()
    current_time = pendulum.now()

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

    await send_message_to_channel("annoncement_channel_id", message)
    await asyncio.sleep(61)

@client.event
async def on_ready():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(vs_day_reminder, 'cron', hour=1, minute=49)
    scheduler.start()

client.run(token)
