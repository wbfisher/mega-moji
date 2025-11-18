"""
Discord bot client for accessing guild information.
"""

import os
import discord
from discord import Intents
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DiscordBot:
    """Discord bot client wrapper."""
    
    def __init__(self):
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        if not self.token:
            raise ValueError("DISCORD_BOT_TOKEN not found in environment variables")
        
        # Set up intents to access guild information
        intents = Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        
        self.client = discord.Client(intents=intents)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up Discord client event handlers."""
        
        @self.client.event
        async def on_ready():
            print(f'✅ {self.client.user} has logged in to Discord!')
            print(f'✅ Bot is in {len(self.client.guilds)} server(s)')
            for guild in self.client.guilds:
                print(f'   - {guild.name} (ID: {guild.id}, Emojis: {len(guild.emojis)})')
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            import traceback
            print(f'❌ An error occurred in {event}')
            traceback.print_exc()
        
        @self.client.event
        async def on_disconnect():
            print('⚠️  Bot disconnected from Discord')
    
    async def start(self):
        """Start the Discord bot."""
        await self.client.start(self.token)
    
    async def close(self):
        """Close the Discord bot connection."""
        await self.client.close()
    
    def get_guilds(self):
        """Get all guilds the bot is in."""
        return self.client.guilds
    
    def get_guild_by_id(self, guild_id: int):
        """Get a guild by its ID."""
        return self.client.get_guild(guild_id)
    
    def is_ready(self):
        """Check if the bot is ready."""
        return self.client.is_ready()

