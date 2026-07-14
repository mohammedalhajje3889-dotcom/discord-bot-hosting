#!/bin/bash
cd /root/discord-bot-hosting

# Kill any existing instances
pkill -f "python app.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1

# Start Flask app
source venv/bin/activate
python app.py > /tmp/flask.log 2>&1 &
echo "Flask started on port 5000"
sleep 2

# Start cloudflared tunnel
/tmp/cloudflared tunnel --url http://localhost:5000 > /tmp/tunnel.log 2>&1 &
echo "Cloudflare tunnel starting..."
sleep 5

# Get the URL
URL=$(grep -oP 'https://[a-z-]+\.trycloudflare\.com' /tmp/tunnel.log | head -1)
echo "Site URL: $URL"
echo "Dashboard: $URL/login"
