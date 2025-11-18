"""
Flask web application for Discord emoji downloader.
"""

import os
import asyncio
import threading
import traceback
import sys
import discord
from flask import Flask, render_template, request, jsonify, send_file
from bot import DiscordBot
from emoji_downloader import download_and_zip_emojis

app = Flask(__name__)

# Global bot instance and event loop
bot = None
bot_loop = None
bot_thread = None


def get_bot_loop():
    """Get or create the bot's event loop."""
    global bot_loop
    return bot_loop


def run_async(coro):
    """Run an async coroutine in the bot's event loop."""
    loop = get_bot_loop()
    if loop is None or not loop.is_running():
        # Fallback: run in new event loop
        return asyncio.run(coro)
    
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


def get_bot_instance():
    """Get or create the Discord bot instance."""
    global bot
    return bot


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get bot connection status for debugging."""
    try:
        bot_instance = get_bot_instance()
        token_set = bool(os.getenv('DISCORD_BOT_TOKEN'))
        
        status = {
            'bot_exists': bot_instance is not None,
            'bot_ready': bot_instance.is_ready() if bot_instance else False,
            'token_set': token_set,
            'guild_count': len(bot_instance.get_guilds()) if bot_instance and bot_instance.is_ready() else 0
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/guilds', methods=['GET'])
def get_guilds():
    """Get list of all guilds the bot is in."""
    try:
        bot_instance = get_bot_instance()
        
        if bot_instance is None:
            # Check if token is set
            if not os.getenv('DISCORD_BOT_TOKEN'):
                return jsonify({'error': 'Discord bot token not configured. Please set DISCORD_BOT_TOKEN in Railway.'}), 503
            return jsonify({'error': 'Bot is not initialized yet. Please wait a moment and refresh.'}), 503
        
        if not bot_instance.is_ready():
            return jsonify({'error': 'Bot is not ready yet. Please wait a moment and refresh.'}), 503
        
        guilds = bot_instance.get_guilds()
        guild_list = [
            {
                'id': str(guild.id),
                'name': guild.name,
                'emoji_count': len(guild.emojis)
            }
            for guild in guilds
        ]
        
        return jsonify({'guilds': guild_list})
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/download', methods=['POST'])
def download_emojis():
    """Download emojis from a guild and return zip file."""
    try:
        data = request.get_json()
        guild_id = int(data.get('guild_id'))
        
        bot_instance = get_bot_instance()
        
        if bot_instance is None or not bot_instance.is_ready():
            return jsonify({'error': 'Bot is not ready yet. Please wait a moment.'}), 503
        
        guild = bot_instance.get_guild_by_id(guild_id)
        
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        # Download and zip emojis (run async in bot's event loop)
        zip_buffer, emoji_count = run_async(download_and_zip_emojis(guild))
        
        # Create filename
        safe_guild_name = "".join(c for c in guild.name if c.isalnum() or c in "._- ")
        filename = f"{safe_guild_name}_emojis.zip"
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_bot_loop():
    """Run the Discord bot in an event loop."""
    global bot, bot_loop
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    
    try:
        # Check if token is set before creating bot
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print("ERROR: DISCORD_BOT_TOKEN not found in environment variables")
            print("Please set DISCORD_BOT_TOKEN in Railway project variables")
            sys.stderr.write("ERROR: DISCORD_BOT_TOKEN not found\n")
            return
        
        print(f"Initializing Discord bot (token length: {len(token) if token else 0})...")
        bot = DiscordBot()
        print("Bot instance created successfully")
        
        # Start the bot as a task and run the loop forever
        async def start():
            try:
                print("Attempting to connect to Discord...")
                await bot.start()
            except discord.LoginFailure:
                print("ERROR: Failed to login to Discord. Check your bot token.")
                sys.stderr.write("ERROR: Discord login failed - invalid token\n")
            except Exception as e:
                print(f"ERROR: Bot connection failed: {e}")
                print(traceback.format_exc())
                sys.stderr.write(f"ERROR: Bot error: {e}\n{traceback.format_exc()}\n")
        
        # Create task and run loop forever (bot.start() keeps running)
        task = bot_loop.create_task(start())
        print("Bot task created, starting event loop...")
        bot_loop.run_forever()
    except Exception as e:
        print(f"ERROR: Loop error: {e}")
        print(traceback.format_exc())
        sys.stderr.write(f"ERROR: Loop error: {e}\n{traceback.format_exc()}\n")
    finally:
        if not bot_loop.is_closed():
            bot_loop.close()


def start_bot_background():
    """Start the Discord bot in a background thread."""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
        bot_thread.start()
        
        # Wait a moment for bot to initialize
        import time
        time.sleep(3)


@app.before_request
def initialize_bot():
    """Initialize the bot before handling requests."""
    global bot
    if bot is None:
        start_bot_background()


if __name__ == '__main__':
    # Start bot in background
    start_bot_background()
    
    # Run Flask app
    # Railway provides PORT environment variable, fallback to 5000 for local dev
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

