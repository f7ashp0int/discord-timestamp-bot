# TimeStamper Bot ⏰

A Discord bot that converts time mentions to Discord's universal timestamps and provides time management utilities.

## Features ✨
- Auto-convert time mentions to localized timestamps
- User timezone configuration
- Countdown timers with notifications
- Manual timestamp generation
- Natural language processing for time detection

## Setup Guide 🛠️

### 1. Invite the Bot
[Invite Link](https://discord.com/api/oauth2/authorize?client_id=1334788863608225895&permissions=274877983808&scope=bot%20applications.commands)

Required Permissions:
- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands

### 2. Commands 📜

#### User Commands
`/setzone [timezone]` - Set your timezone (e.g. IST, CET)  
`/timer [duration] [message]` - Create countdown (e.g. "10m Meeting starts")  
`/timestamp [date] [time] [timezone]` - Generate custom timestamp  

#### Admin Commands
`/convert [time] [from_tz] [to_tz]` - Convert between timezones  
`/schedule [message] [time]` - Schedule server announcements  

### 3. Natural Language Usage 💬
Tag the bot (@TimeStamper) with:
- "Set a 15m timer for pizza!"
- "Convert 3PM EST to UTC"
- "What's 2023-12-25 20:00 CET in PST?"

Responds to time mentions in messages:  
"Meeting tomorrow at 14:30 IST" → converts automatically

