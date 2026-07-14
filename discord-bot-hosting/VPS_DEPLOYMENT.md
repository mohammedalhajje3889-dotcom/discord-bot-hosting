# نشر استضافة بوتات ديسكورد على VPS

## المتطلبات

- VPS مع Ubuntu/Debian
- Python 3.8+
- Node.js (لبوتات JavaScript)
- Nginx (للإيقافᾄλ背后的反向代理)
- SSL (اختياري لكن مُوصى به)

## خطوات النشر

### 1. تحديث النظام وتثبيت المتطلبات

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python
sudo apt install -y python3 python3-pip python3-venv

# تثبيت Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# تثبيت Nginx
sudo apt install -y nginx

# تثبيت Git
sudo apt install -y git
```

### 2. نشر التطبيق

```bash
# إنشاء مجلد التطبيق
sudo mkdir -p /var/www/discord-bot-hosting
sudo chown $USER:$USER /var/www/discord-bot-hosting

# نسخ الملفات
cp -r /root/discord-bot-hosting/* /var/www/discord-bot-hosting/

# الدخول إلى المجلد
cd /var/www/discord-bot-hosting

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# إنشاء المجلدات المطلوبة
mkdir -p uploads bots logs
```

### 3. إعداد خدمة systemd

```bash
# نسخ ملف الخدمة
sudo cp discord-bot-hosting.service /etc/systemd/system/

# تحرير ملف الخدمة
sudo nano /etc/systemd/system/discord-bot-hosting.service
```

محتوى ملف الخدمة:
```ini
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

[Install]
WantedBy=multi-user.target
```

```bash
# تشغيل الخدمة
sudo systemctl daemon-reload
sudo systemctl enable discord-bot-hosting
sudo systemctl start discord-bot-hosting

# التحقق من حالة الخدمة
sudo systemctl status discord-bot-hosting
```

### 4. إعداد Nginx

```bash
# إنشاء ملف إعدادات Nginx
sudo nano /etc/nginx/sites-available/discord-bot-hosting
```

محتوى ملف الإعدادات:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/discord-bot-hosting/static;
        expires 30d;
    }
}
```

```bash
# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/discord-bot-hosting /etc/nginx/sites-enabled/

# حذف الموقع الافتراضي
sudo rm /etc/nginx/sites-enabled/default

# اختبار الإعدادات
sudo nginx -t

# إعادة تشغيل Nginx
sudo systemctl restart nginx
```

### 5. إعداد SSL (اختياري)

```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com

# إعداد التجديد التلقائي
sudo crontab -e
# أضف: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. إعداد جدار النار

```bash
# فتح المنافذ المطلوبة
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22

# تفعيل جدار النار
sudo ufw enable
```

### 7. إعداد النسخ الاحتياطي

```bash
# إنشاء سكربت النسخ الاحتياطي
sudo nano /usr/local/bin/backup-discord-bot-hosting.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/discord-bot-hosting"
DATE=$(date +%Y-%m-%d)

mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
cp /var/www/discord-bot-hosting/database.db $BACKUP_DIR/database_$DATE.db

# نسخ احتياطي للبوتات
tar -czf $BACKUP_DIR/bots_$DATE.tar.gz /var/www/discord-bot-hosting/uploads /var/www/discord-bot-hosting/bots

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

```bash
# جعل السكربت قابل للتنفيذ
sudo chmod +x /usr/local/bin/backup-discord-bot-hosting.sh

# إضافة إلى crontab
sudo crontab -e
# أضف: 0 2 * * * /usr/local/bin/backup-discord-bot-hosting.sh
```

## إدارة التطبيق

### أوامر مفيدة

```bash
# عرض حالة الخدمة
sudo systemctl status discord-bot-hosting

# إعادة تشغيل الخدمة
sudo systemctl restart discord-bot-hosting

# إيقاف الخدمة
sudo systemctl stop discord-bot-hosting

# عرض السجلات
sudo journalctl -u discord-bot-hosting -f

# عرض سجلات Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## ملاحظات مهمة

1. **الأمان**: غيّر SECRET_KEY في config.py
2. **النسخ الاحتياطي**: قم بعمل نسخ احتياطي دوري لقاعدة البيانات والبوتات
3. **المراقبة**: راقب استخدام الموارد والسجلات
4. **التحديثات**: قم بتحديث النظام والمتطلبات بانتظام

## استكشاف الأخطاء

### المشكلة: التطبيق لا يعمل
```bash
# تحقق من حالة الخدمة
sudo systemctl status discord-bot-hosting

# عرض السجلات
sudo journalctl -u discord-bot-hosting -n 50
```

### المشكلة: Nginx لا يعمل
```bash
# تحقق من حالة Nginx
sudo systemctl status nginx

# اختبار الإعدادات
sudo nginx -t

# عرض سجلات الأخطاء
sudo tail -f /var/log/nginx/error.log
```

### المشكلة: البوتات لا تعمل
```bash
# تحقق من صلاحيات المجلدات
ls -la /var/www/discord-bot-hosting/uploads
ls -la /var/www/discord-bot-hosting/bots
ls -la /var/www/discord-bot-hosting/logs

# تغيير الصلاحيات إذا لزم الأمر
sudo chown -R www-data:www-data /var/www/discord-bot-hosting
```
