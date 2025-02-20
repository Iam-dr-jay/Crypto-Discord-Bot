# Import necessary libraries
import discord
from discord.ext import commands, tasks
import requests
import asyncio
import os

# Load environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
BINANCE_API_URL = os.getenv("BINANCE_API_URL", "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")

# Set bot command prefix and intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Function to fetch BTC price from Binance API
async def get_btc_price():
    try:
        response = requests.get(BINANCE_API_URL)
        data = response.json()
        price = data["price"]
        return f"Current BTC Price: ${price}"
    except Exception as e:
        return f"Error fetching price: {e}"

# Function to check BTC transactions (Placeholder - Replace with API call)
async def check_btc_transactions():
    # Simulated response (Replace with real API logic)
    return "SimulatedTxHash", 0.01  # Example transaction amount

# Background task to fetch BTC price updates
@tasks.loop(minutes=5)
async def btc_price_update():
    price = await get_btc_price()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "market-feed" in channel.name:  # Send to market-feed channel
                await channel.send(price)

# Background task to check BTC payments
@tasks.loop(minutes=10)
async def check_payments():
    tx_hash, amount = await check_btc_transactions()
    if tx_hash:
        for guild in bot.guilds:
            vip_role = discord.utils.get(guild.roles, name="VIP Member")
            if vip_role:
                for member in guild.members:
                    if not vip_role in member.roles:
                        await member.add_roles(vip_role)
                        await member.send(f"Payment of {amount} BTC received! You have been granted VIP access.")

# Event: Bot Ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    btc_price_update.start()
    check_payments.start()

# Command: Get BTC Price
@bot.command()
async def btc(ctx):
    price = await get_btc_price()
    await ctx.send(price)

# Run bot
bot.run(DISCORD_BOT_TOKEN)