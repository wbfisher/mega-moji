"""
Module for downloading Discord emojis and packaging them into zip files.
"""

import io
import zipfile
import asyncio
from typing import List, Tuple
import aiohttp
import discord
from discord import Emoji


async def download_emoji(session: aiohttp.ClientSession, emoji: Emoji) -> Tuple[str, bytes]:
    """
    Download an emoji and return its filename and content.
    
    Args:
        session: aiohttp session for making HTTP requests
        emoji: Discord emoji object
        
    Returns:
        Tuple of (filename, emoji_bytes)
    """
    # Determine file extension based on whether emoji is animated
    extension = "gif" if emoji.animated else "png"
    filename = f"{emoji.name}.{extension}"
    
    # Download the emoji
    async with session.get(str(emoji.url)) as response:
        emoji_bytes = await response.read()
    
    return filename, emoji_bytes


async def download_all_emojis(guild: discord.Guild) -> List[Tuple[str, bytes]]:
    """
    Download all emojis from a Discord guild.
    
    Args:
        guild: Discord guild (server) to download emojis from
        
    Returns:
        List of tuples containing (filename, emoji_bytes)
    """
    emojis = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for emoji in guild.emojis:
            tasks.append(download_emoji(session, emoji))
        
        emojis = await asyncio.gather(*tasks)
    
    return emojis


def create_zip_file(emojis: List[Tuple[str, bytes]], guild_name: str) -> io.BytesIO:
    """
    Create a zip file containing all downloaded emojis.
    
    Args:
        emojis: List of tuples containing (filename, emoji_bytes)
        guild_name: Name of the guild (used for zip filename)
        
    Returns:
        BytesIO object containing the zip file
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, emoji_bytes in emojis:
            # Sanitize filename to avoid issues with special characters
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            zip_file.writestr(safe_filename, emoji_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer


async def download_and_zip_emojis(guild: discord.Guild) -> Tuple[io.BytesIO, int]:
    """
    Download all emojis from a guild and create a zip file.
    
    Args:
        guild: Discord guild (server) to download emojis from
        
    Returns:
        Tuple of (zip_file_buffer, emoji_count)
    """
    if not guild.emojis:
        # Return empty zip if no emojis
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            pass
        zip_buffer.seek(0)
        return zip_buffer, 0
    
    emojis = await download_all_emojis(guild)
    zip_buffer = create_zip_file(emojis, guild.name)
    
    return zip_buffer, len(emojis)

