# استضافة بوتات ديسكورد

منصة استضافة بوتات ديسكورد على VPS خاص مع خدمة دائمة تعمل 24/7.

## المميزات

- تسجيل حسابات المستخدمين
- رفع ملفات ZIP للبوتات
- إدخال توكن البوت
- تشغيل/إيقاف/حذف البوتات
- عرض السجلات في الوقت الفعلي
- خدمة systemd للعمل الدائم
- Nginx كـ reverse proxy
- دعم SSL/TLS

## المتطلبات

- VPS مع Ubuntu/Debian
- Python 3.8+
- Node.js (لبوتات JavaScript)
- Nginx
- Git

## النشر السريع

### 1. نسخ الملفات إلى VPS

```bash
# على جهازك المحلي
scp -r /root/discord-bot-hosting user@your-vps-ip:/root/

# أو استخدام git
git clone <repository-url>
```

### 2. تشغيل سكربت الإعداد

```bash
# على VPS
cd /root/discord-bot-hosting
sudo ./setup_vps.sh
```

### 3. الوصول إلى الموقع

افتح المتصفح وانتقل إلى:
```
http://your-vps-ip
```

## الإعداد اليدوي

إذا كنت تفضل الإعداد اليدوي، راجع [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md).

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

# تشغيل مراقب الحالة
./monitor.sh
```

## هيكل المشروع

```
discord-bot-hosting/
├── app.py                    # التطبيق الرئيسي
├── config.py                 # الإعدادات
├── database.py               # إعداد قاعدة البيانات
├── models.py                 # نماذج البيانات
├── requirements.txt          # المتطلبات
├── setup_vps.sh              # سكربت الإعداد
├── deploy.sh                 # سكربت النشر
├── monitor.sh                # مراقب الحالة
├── discord-bot-hosting.service # خدمة systemd
├── routes/
│   ├── auth.py               # مسارات المصادقة
│   └── dashboard.py          # مسارات لوحة التحكم
├── bot_manager/
│   └── process_manager.py    # إدارة عمليات البوتات
├── templates/                # القوالب
├── static/                   # الملفات الثابتة
├── uploads/                  # ملفات البوتات
├── bots/                     # البوتات المستخرجة
└── logs/                     # سجلات البوتات
```

## استكشاف الأخطاء

### المشكلة: التطبيق لا يعمل

```bash
# تحقق من حالة الخدمة
sudo systemctl status discord-bot-hosting

# عرض السجلات
sudo journalctl -u discord-bot-hosting -n 50
```

### المشكلة: خطأ 502 Bad Gateway

```bash
# تحقق من أن التطبيق يعمل
sudo systemctl status discord-bot-hosting

# تحقق من أن Nginx يعمل
sudo systemctl status nginx

# تحقق من الإعدادات
sudo nginx -t
```

### المشكلة: البوتات لا تعمل

```bash
# تحقق من الصلاحيات
ls -la /var/www/discord-bot-hosting/uploads
ls -la /var/www/discord-bot-hosting/bots

# تغيير الصلاحيات
sudo chown -R www-data:www-data /var/www/discord-bot-hosting
```

## النسخ الاحتياطي

```bash
# إنشاء نسخة احتياطية يدوية
sudo /usr/local/bin/backup-discord-bot-hosting.sh

# عرض النسخ الاحتياطية
ls -la /var/backups/discord-bot-hosting/
```

## الأمان

1. **غيّر SECRET_KEY** في config.py
2. **استخدم HTTPS** مع Let's Encrypt
3. **حدّث النظام** بانتظام
4. **راجع السجلات** بشكل دوري
5. **افعل نسخ احتياطي** للبيانات

## الدعم

للمشاكل أو الاستفسارات، راجع الملفات التالية:
- [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md) - دليل النشر التفصيلي
- [deploy.sh](deploy.sh) - سكربت النشر
- [setup_vps.sh](setup_vps.sh) - سكربت الإعداد
