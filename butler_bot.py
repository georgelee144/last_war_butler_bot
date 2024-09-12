import asyncio
import discord
from discord.ext import commands
import pendulum
import helper

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


# @client.event
# async def on_member_join(member):
#     print("triggerd")

#     alliance_name = server_info["alliance_name"]

#     message = f"Hello {member.mention}!\nWelcome to {alliance_name}.\nVisit for the rules: {server_info['rules_url']}"
#     await send_message_to_channel("welcome_channel_id", message)


async def vs_day_reminder():
    vs_day_reminders = helper.read_vs_day_toml()

    while True:
        current_time = pendulum.now()
        if current_time.hour == 22 and current_time.minute == 0:
            # if True:

            for vs_day_key, vs_day_info in vs_day_reminders.items():
                day_of_week_match_check = (
                    helper.days_of_week[current_time.day_of_week] == vs_day_info["day"]
                )

                if day_of_week_match_check:
                    message = (
                        f"# It is now day {vs_day_key[-1]} aka {vs_day_info['name']}.\n"
                    )
                    message += "Perform the following tasks to earn points:\n"
                    message += f"""{helper.combine_vs_tasks(vs_day_info["tasks"])}"""
                    break
            await send_message_to_channel("annoncement_channel_id", message)
            await asyncio.sleep(90)


@client.event
async def on_ready():
    client.loop.create_task(vs_day_reminder())


client.run(token)
