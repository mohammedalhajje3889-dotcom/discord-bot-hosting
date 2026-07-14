#!/bin/bash

# Oracle Cloud Free Tier - Quick Setup Script
# Run this on your Oracle Cloud Ubuntu instance

set -e

echo "=========================================="
echo "  Oracle Cloud Free Tier Setup"
echo "  Discord Bot Hosting"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo ./oracle_cloud_setup.sh"
    exit 1
fi

# Update system
echo "Updating system..."
apt update && apt upgrade -y

# Install required packages
echo "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx git curl ufw

# Install Node.js
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)
echo "Your Public IP: $PUBLIC_IP"

# Create application directory
echo "Creating application directory..."
mkdir -p /var/www/discord-bot-hosting
cd /var/www/discord-bot-hosting

# Ask for repository URL
echo ""
read -p "Enter your GitHub repository URL (or press Enter to skip): " REPO_URL

if [ -n "$REPO_URL" ]; then
    echo "Cloning repository..."
    git clone $REPO_URL .
else
    echo "Please upload your files manually using SCP or SFTP"
    echo "Example: scp -r /path/to/discord-bot-hosting/* ubuntu@$PUBLIC_IP:/var/www/discord-bot-hosting/"
    echo ""
    echo "Press Enter after uploading files to continue..."
    read
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create required directories
echo "Creating directories..."
mkdir -p uploads bots logs

# Set permissions
echo "Setting permissions..."
chown -R www-data:www-data /var/www/discord-bot-hosting
chmod -R 755 /var/www/discord-bot-hosting

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/discord-bot-hosting.service << 'EOF'
[Unit]
Description=Discord Bot Hosting Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/discord-bot-hosting
Environment="PATH=/var/www/discord-bot-hosting/venv/bin"
ExecStart=/var/www/discord-bot-hosting/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "Enabling service..."
systemctl daemon-reload
systemctl enable discord-bot-hosting
systemctl start discord-bot-hosting

# Configure Nginx
echo "Configuring Nginx..."
cat > /etc/nginx/sites-available/discord-bot-hosting << EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/discord-bot-hosting/static;
        expires 30d;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/discord-bot-hosting /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx

# Configure firewall
echo "Configuring firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Access your application at:"
echo "  http://$PUBLIC_IP"
echo ""
echo "Next steps:"
echo "1. Open your browser and go to http://$PUBLIC_IP"
echo "2. Create a new account"
echo "3. Start adding your Discord bots!"
echo ""
echo "To manage the service:"
echo "  sudo systemctl status discord-bot-hosting"
echo "  sudo systemctl restart discord-bot-hosting"
echo "  sudo journalctl -u discord-bot-hosting -f"
echo ""
