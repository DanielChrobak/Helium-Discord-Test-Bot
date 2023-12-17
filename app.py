import os
import discord
from discord import app_commands
from discord.ext import commands
import requests

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

API_URL = "https://helium-api.heliumgeek.com/v0/gateways?name="
API_KEY = os.getenv('API_KEY')  # Fetch API key from environment variable

@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="search")
@app_commands.describe(hotspot_name="Enter the name of the hotspot")
async def search(interaction: discord.Interaction, hotspot_name: str):
    formatted_name = "+".join(hotspot_name.lower().split())
    header = {"x-api-key": API_KEY}  # Use the API key fetched from environment variable
    request = requests.get(f"{API_URL}{formatted_name}", headers=header)
    data = request.json()

    if request.status_code == 200:
        if data:
            hotspot = data[0]  # Get data for the first hotspot
            embed = discord.Embed(title="Hotspot Information", color=discord.Color.green())

            embed.add_field(name="Name", value=hotspot.get("name"), inline=True)
            embed.add_field(name="Owner", value=hotspot.get("owner"), inline=True)
            embed.add_field(name="Status", value=hotspot.get("statusString"), inline=True)

            speedtest_avg = hotspot.get("recent", {}).get("speedtestAverage", {})
            embed.add_field(name="Speedtest Avg", value=f"Upload: {speedtest_avg.get('upload')}\nDownload: {speedtest_avg.get('download')}\nLatency: {speedtest_avg.get('latency')}", inline=True)

            total_rank = hotspot.get("recent", {}).get("epoch", {}).get("mobileRewards", {}).get("total", {}).get("rank")
            poc_rank = hotspot.get("recent", {}).get("epoch", {}).get("mobileRewards", {}).get("poc", {}).get("rank")
            embed.add_field(name="Total Rank", value=total_rank, inline=True)
            embed.add_field(name="PoC Rank", value=poc_rank, inline=True)

            total_rewards = hotspot.get("recent", {}).get("epoch", {}).get("mobileRewards", {}).get("total", {}).get("amount")
            poc_rewards = hotspot.get("recent", {}).get("epoch", {}).get("mobileRewards", {}).get("poc", {}).get("amount")
            embed.add_field(name="Total Rewards", value=total_rewards, inline=True)
            embed.add_field(name="PoC Rewards", value=poc_rewards, inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message("No data found for the specified hotspot.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Failed to fetch data. Status code: {request.status_code}", ephemeral=True)

# Retrieve the bot token from an environment variable
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if BOT_TOKEN is None:
    print('Please set the DISCORD_BOT_TOKEN environment variable.')
else:
    bot.run(BOT_TOKEN)
