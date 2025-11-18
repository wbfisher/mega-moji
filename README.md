# Mega Moji - Discord Emoji Downloader

A Discord bot with a web interface that downloads all emojis from a Discord server and packages them into a zip file.

## Features

- 🎨 Download all emojis from any Discord server the bot is in
- 🌐 Simple web interface to select the server
- 📦 Automatically packages emojis into a zip file
- 🖼️ Supports both static and animated emojis

## Setup

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - Server Members Intent
   - Message Content Intent (if needed)
6. Copy the bot token

### 2. Invite Bot to Server

Use this URL (replace `YOUR_CLIENT_ID` with your bot's Client ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=0&scope=bot
```

Make sure the bot has access to the servers you want to download emojis from.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and add your bot token:

```bash
cp .env.example .env
```

Edit `.env`:
```
DISCORD_BOT_TOKEN=your_actual_bot_token_here
```

### 5. Run the Application

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

## Usage

1. Start the application
2. Open `http://localhost:5000` in your browser
3. Select a Discord server from the dropdown
4. Click "Download Emojis"
5. Wait for the download to complete
6. Download the generated zip file

## Project Structure

```
mega-moji/
├── app.py                 # Main Flask application
├── bot.py                 # Discord bot client
├── emoji_downloader.py    # Emoji downloading logic
├── templates/             # HTML templates
│   └── index.html
├── static/                # Static files (CSS, JS)
│   └── style.css
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment configuration
├── runtime.txt           # Python version specification
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Railway Deployment

### Prerequisites

1. A [Railway](https://railway.app/) account
2. A GitHub account (or use Railway CLI)
3. Your Discord bot token ready

### Deploying to Railway

#### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a new Railway project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   - In your Railway project, go to the "Variables" tab
   - Add the following environment variable:
     - `DISCORD_BOT_TOKEN`: Your Discord bot token

4. **Deploy**
   - Railway will automatically detect the Python project
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

5. **Get your URL**
   - Railway will assign a public URL (e.g., `https://mega-moji.up.railway.app`)
   - You can also set a custom domain in the project settings

#### Option 2: Deploy using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway project**
   ```bash
   railway init
   ```

4. **Set environment variables**
   ```bash
   railway variables set DISCORD_BOT_TOKEN=your_bot_token_here
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### Railway-Specific Notes

- Railway automatically provides a `PORT` environment variable - the app uses this automatically
- The `Procfile` tells Railway how to start your application
- `runtime.txt` specifies the Python version (Railway will use this)
- Your bot will be publicly accessible at the Railway URL
- Railway will automatically redeploy when you push to your connected GitHub branch

### Monitoring

- View logs in the Railway dashboard under your service
- Check the "Metrics" tab for resource usage
- Railway provides automatic HTTPS and custom domains

## Notes

- The bot must be a member of the server you want to download emojis from
- Emoji files are saved with their original names and formats
- Animated emojis are saved as `.gif` files
- Static emojis are saved as `.png` files
- When deployed, the web interface will be accessible via your Railway URL

