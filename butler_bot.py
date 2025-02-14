import asyncio
import discord
from discord.ext import commands
import pendulum
import helper
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import google_gemini_llm
import os

logging.basicConfig(
    filename="butler_bot.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
server_info = helper.read_server_info()
token = os.getenv("LAST_WAR_DISCORD_TOKEN")

@commands.has_permissions(mention_everyone=True)
async def send_message_to_channel(channel, message):
    channel_id = server_info[channel]
    logging.info(f"Sending {message} to channel {channel_id}")
    channel = bot.get_channel(channel_id)
    try:
        await channel.send(message,allowed_mentions=discord.AllowedMentions(everyone=True))
    except Exception as error:
        logging.error(
            f"Failed to send {message} to channel {channel_id} becauase: {error}"
        )
        pass


@bot.event
async def on_member_join(member):
    logging.info(f"New member has joined: {member.name}")

    rules_url = server_info["rules_url"]

    message = f"Welcome to the server, {member.mention}!\n"
    message += f"Please read familarize yourself with the [rules]({rules_url})"

    logging.info(f"sending the welcome message: {message} ")

    await send_message_to_channel("welcome_channel_id", message)


@bot.slash_command(name="llm", description="Process a message with LLM")
@discord.option("message", type=str)
@discord.option(
    "temperature",
    description="Determines randomness of output 0.0 (less random) to 2.0 (more random)",
    type=discord.SlashCommandOptionType.number,
    default=0.0,
    min_value=0.0,
    max_value=2.0,
)
async def llm(ctx:discord.commands.context.ApplicationContext, message: str, temperature: float):
    logging.info(f"{ctx.author} called llm with this prompt: {message}")
    
    response = google_gemini_llm.talk_to_gemini(
            message_to_llm=message, temperature=temperature
    )

    if response is tuple:
        logging.error(f"Failed to get a response from llm because {response[1]}")    
        await ctx.respond(f"Failed to get a response because {response[1]}")
    else:
        await ctx.respond(response)


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
            message = f"# It is now day {vs_day_key[-1]} aka {vs_day_info['name']}.\n"
            message += "## Perform the following tasks to earn points:\n"
            message += f"""{helper.combine_vs_messages(vs_day_info["tasks"])}"""
            message += "## Arms Race synergy:\n"
            message += f"""{helper.combine_vs_messages(vs_day_info["arms_race"])}"""
            break
    try:
        logging.info(f"sending {message}")
        await send_message_to_channel("annoncement_channel_id", message)
    except Exception as error:
        logging.error(f"Failed to send {message} because: {error}")
    await asyncio.sleep(61)


async def marshal_reminder():
    message = "# Alliance Exercise (Marshal) will begin soon.\n"
    message += (
        "## Stop your rallies and prepare to only join/start Marshal rallies only.\n"
    )
    message += "1. Only join rallies with a 2.5% or a 5% bonus if your squad power is greater than 5 million.\n"
    message += "2. Start rallies with your B/C squad and join rallies with your other squads.\n"
    message += "3. When we reach level 5 you may join any rally and you may stop. You should continue if you believe you can achieve the next tier of rewards. However, we do ask that you continue to send rallies so offline members may join.\n"

    await send_message_to_channel("annoncement_channel_id", message)

@bot.slash_command(name="send_marshal_call", description="Sends stock message that marshal will begin to Announcement Channel")
async def send_marshal_call(ctx:discord.commands.context.ApplicationContext):
    caller = ctx.author
    logging.info(f"{caller} called send_marshal_call()")

    if any(role.name.lower() == "r4" or role.name.lower() == "r5" for role in caller.roles):
        await marshal_reminder()
    else:
        await ctx.respond("Sorry you do not have the authority (R4/R5 roles are missing) to do that.")
        logging.warning(f"{caller} failed to call send_marshal_call()")

@bot.slash_command(name="translate", description="Translates most recent message into English")
async def translate(ctx:discord.commands.context.ApplicationContext):
    caller = ctx.author
    logging.info(f"{caller} called translate()")

    last_message = await ctx.channel.history(limit=1).flatten()
    if last_message:
        last_message = "Translate into english: "+last_message[0].content
    else:
        await ctx.respond("Sorry but there doesn't seem like there is anything to translate.")
    
    await llm(ctx=ctx,message =last_message,temperature=1)

@bot.slash_command(name="traducir", description="Traduce el mensaje más reciente al español.")
async def traducir(ctx:discord.commands.context.ApplicationContext):
    caller = ctx.author
    logging.info(f"{caller} called traducir()")

    last_message = await ctx.channel.history(limit=1).flatten()
    if last_message:
        last_message = "Translate into spanish: "+last_message[0].content
    else:
        await ctx.respond("Lo siento, pero no parece que haya nada que traducir.")
    
    await llm(ctx=ctx,message =last_message,temperature=1)

async def capitol_mud_fight_reminder():
    message = "# Capitol will open be open in about 1 hour.\n"
    message += "## Capitol Buffs will NOT be available for 8 hours from 10am EST, 9am CST, 8am MT, or 7am PST"
    message += "## Pull back squads from the mud if you do not want to get hit.\n"
    message += "1. Only resource tiles in the mud, the brown area around the capitol, is open for battle.\n"
    message += "2. Fight until you receive 100,000 points to get 10,000 honor points.\n"
    message += "3. Fight intellgently, attack tiles with weaker squads and avoid getting hit by heavy hitters.\n"
    message += "4. You may save troops on weeks we have a level 6 land by occuppying the capitol at our scheduled time.\n"

    await send_message_to_channel("annoncement_channel_id", message)


async def capitol_mud_fight_active():
    message = "# Mud fight has begun!\n"
    message += (
        "## Mud fight will end in 8 hours at 6pm EST, 5pm CST, 4pm MT, or 3pm PST"
    )

    await send_message_to_channel("annoncement_channel_id", message)


async def capitol_mud_fight_end():
    message = "# Mud fight is ending in 5 minutes!\n"
    message += "## Reminder: buy a shield from the Alliance or VIP store and activate it before reset, if you do not plan to fight."

    await send_message_to_channel("annoncement_channel_id", message)

async def buy_and_activate_shield_warning():
    message = "@everyone \n"
    message += "# buy a shield from the Alliance or VIP store and activate it, KILL DAY STARTS IN 20 MINUTES!\n"
    message += "## Warp up any fights and do not fight nor scout it will trigger war fever for 15 minutes."

    await send_message_to_channel("annoncement_channel_id", message)

async def desert_storm_reminder():
    message = "@everyone For those that registered please prepare for Desert Storm it will start soon,"
    await send_message_to_channel("annoncement_channel_id",message)

async def desert_storm_registration_reminder():
    message = "Sign up for Desert Storm by reset, today is the last day to register.\nPlease only sign up if you intend to particpate. DS is on Fridays 8pm EST/5pm PST"
    await send_message_to_channel("annoncement_channel_id",message)

async def store_reminder():
    message = "Store will be restock by reset time. Buy your items before then."
    await send_message_to_channel("annoncement_channel_id",message)

@bot.event
async def on_ready():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(vs_day_reminder, "cron", hour=21, minute=0)


    scheduler.add_job(
        desert_storm_registration_reminder, CronTrigger(day_of_week="wed", hour=18, minute=0)
    )
    scheduler.add_job(
        desert_storm_reminder, CronTrigger(day_of_week="fri", hour=19, minute=55)
    )
    scheduler.add_job(
        buy_and_activate_shield_warning, CronTrigger(day_of_week="fri", hour=20, minute=40)
    )
    scheduler.add_job(
        store_reminder, CronTrigger(day_of_week="sun", hour=20, minute=40)
    )
    scheduler.start()


bot.run(token)
