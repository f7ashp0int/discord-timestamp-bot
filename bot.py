import os
import re
import datetime
import dateparser
import asyncio
import sqlite3
import pytz
from dateutil import tz
import discord
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

# Database setup
conn = sqlite3.connect('timezones.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, timezone TEXT)''')
conn.commit()
conn.close()

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

TIMEZONE_MAP = {
    'IST': 'Asia/Kolkata',
    'CET': 'Europe/Paris',
    'UTC': 'UTC',
    'PST': 'America/Los_Angeles',
    'EST': 'America/New_York'
}

TIME_PATTERN = re.compile(
    r'(?i)\b('
    r'(?:today|tomorrow|yesterday|\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|'
    r'\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?|'
    r'\d+\s+days?\s+(?:from\s+now|ago)'
    r')\b)\s*'
    r'(?:at\s*)?(\d{1,2}(?::\d{2}){0,2}\s*[ap]?\.?m?\.?)\s*'  # Time part
    r'(\b[A-Z]{2,4}\b)\s*'  # Timezone part
    r'(?:tomorrow|today|yesterday|\d+\s+days?\s+(?:from\s+now|ago))?',  # Relative date after timezone
    re.IGNORECASE
)

def get_user_timezone(user_id):
    conn = sqlite3.connect('timezones.db')
    c = conn.cursor()
    c.execute('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'UTC'

async def convert_times(message_content, created_at, author_id):
    results = []
    now = created_at.replace(tzinfo=tz.UTC)
    
    for match in TIME_PATTERN.finditer(message_content):
        date_part, time_part, tz_part = match.groups()
        if not all([date_part, time_part]):
            continue

        tz_name = TIMEZONE_MAP.get((tz_part or '').upper(), tz_part or 'UTC')
        time_str = f"{date_part} {time_part}".strip()
        
        try:
            # Parse as naive datetime in target timezone
            parsed = dateparser.parse(
                time_str,
                settings={
                    'RELATIVE_BASE': now,
                    'TIMEZONE': tz_name,
                    'RETURN_AS_TIMEZONE_AWARE': False
                }
            )
            
            if parsed:
                # Localize and convert to UTC
                tz_obj = pytz.timezone(tz_name)
                localized = tz_obj.localize(parsed)
                utc_time = localized.astimezone(pytz.utc)
                
                results.append({
                    "original": f"{time_str} {tz_part}" if tz_part else time_str,
                    "timestamp": int(utc_time.timestamp())
                })
                
        except Exception as e:
            print(f"Error parsing {time_str}: {e}")

    return results

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for time formats"
    ))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        converted = await convert_times(message.content, message.created_at, message.author.id)
        if not converted:
            return

        response = "**Converted Times:**\n" + "\n".join(
            f"`{entry['original']}` → <t:{entry['timestamp']}:F>"
            for entry in converted
        )
        await message.reply(response, mention_author=False)

    except Exception as e:
        print(f"Error processing message: {e}")
# Add to bot commands
@bot.slash_command(description="Create a timestamp")
async def timestamp(ctx, 
                   date: str, 
                   time: str, 
                   timezone: str = "UTC"):
    try:
        parsed = dateparser.parse(f"{date} {time}", settings={'TIMEZONE': timezone})
        utc_time = parsed.astimezone(pytz.utc)
        await ctx.respond(f"`{date} {time} {timezone}` → <t:{int(utc_time.timestamp())}:F>")
    except:
        await ctx.respond("Invalid format! Use: `/timestamp 2023-12-31 23:59 CET`")

# Add message handler for mentions
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        if "timer" in message.content.lower():
            # Parse natural language timer
            duration = re.search(r'(\d+)\s*(m|min|minutes)', message.content)
            if duration:
                mins = int(duration.group(1))
                # Timer logic here
                
        elif not any(word in message.content.lower() for word in ['convert', 'time', 'at']):
            await message.reply("Don't @ me 😠\nUse proper time format: `3PM IST tomorrow`")
            return
            
    await bot.process_commands(message)

@bot.slash_command(description="Set your timezone")
async def settimezone(ctx, timezone: str):
    timezone = TIMEZONE_MAP.get(timezone.upper(), timezone)
    try:
        pytz.timezone(timezone)
        conn = sqlite3.connect('timezones.db')
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', (ctx.author.id, timezone))
        conn.commit()
        conn.close()
        await ctx.respond(f"Timezone set to {timezone}!", ephemeral=True)
    except pytz.UnknownTimeZoneError:
        await ctx.respond("Invalid timezone! Use formats like 'IST' or 'Asia/Kolkata'", ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
