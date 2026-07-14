#!/bin/bash

# Discord Bot Hosting - Monitor Script
# This script checks the status of the application and its components

echo "=========================================="
echo "  Discord Bot Hosting - Status Monitor"
echo "=========================================="
echo ""

# Check systemd service
echo "1. Checking systemd service..."
if systemctl is-active --quiet discord-bot-hosting; then
    echo "   ✓ Service is running"
else
    echo "   ✗ Service is not running"
    echo "   Starting service..."
    sudo systemctl start discord-bot-hosting
fi

# Check Nginx
echo ""
echo "2. Checking Nginx..."
if systemctl is-active --quiet nginx; then
    echo "   ✓ Nginx is running"
else
    echo "   ✗ Nginx is not running"
    echo "   Starting Nginx..."
    sudo systemctl start nginx
fi

# Check application port
echo ""
echo "3. Checking application port..."
if netstat -tlnp | grep -q ":5000"; then
    echo "   ✓ Application is listening on port 5000"
else
    echo "   ✗ Application is not listening on port 5000"
fi

# Check database
echo ""
echo "4. Checking database..."
if [ -f "/var/www/discord-bot-hosting/database.db" ]; then
    echo "   ✓ Database file exists"
else
    echo "   ✗ Database file not found"
fi

# Check disk space
echo ""
echo "5. Checking disk space..."
df -h / | tail -1 | awk '{print "   Disk usage: "$5" ("$3" used of "$2" total)"}'

# Check memory
echo ""
echo "6. Checking memory..."
free -h | grep Mem | awk '{print "   Memory usage: "$3" used of "$2" total"}'

# Check running bots
echo ""
echo "7. Checking running bots..."
ps aux | grep -E "node|python" | grep -v grep | wc -l | xargs -I {} echo "   {} processes running"

echo ""
echo "=========================================="
echo "  Monitor Complete"
echo "=========================================="
echo ""

# Show recent logs
echo "Recent logs (last 10 lines):"
echo "------------------------------------------"
sudo journalctl -u discord-bot-hosting -n 10 --no-pager
