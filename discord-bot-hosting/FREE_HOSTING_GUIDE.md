# دليل الاستضافة المجانية - Oracle Cloud Free Tier

## لماذا Oracle Cloud؟

- **مجاني دائماً**: لا توجد تكلفة شهرية
- **خادم دائم**: يعمل 24/7 بدون انقطاع
- **موارد كافية**: 4 أنوية ARM + 24GB RAM
- ** SSL مجاني**: مع Let's Encrypt

---

## الخطوة 1: إنشاء حساب Oracle Cloud

1. اذهب إلى: https://cloud.oracle.com/free
2. أنشئ حساباً جديداً (يحتاج بريد إلكتروني ورقم هاتف)
3. أكمل التحقق من الهوية
4. اختر **Oracle Cloud Free Tier**

---

## الخطوة 2: إنشاء خادم (Instance)

1. سجل الدخول إلى Oracle Cloud Console
2. اذهب إلى **Compute** → **Instances**
3. اضغط **Create Instance**
4. اختر الإعدادات التالية:

### إعدادات الخادم:
- **Name**: discord-bot-hosting
- **Image**: Ubuntu 22.04 (أو آخر إصدار)
- **Shape**: VM.Standard.A1.Flex (ARM - مجاني)
- **OCPU**: 4 (الأقصى المجاني)
- **RAM**: 24 GB (الأقصى المجاني)
- **Boot Volume**: 200 GB

### مفتاح SSH:
1. اختر **SSH Keys**
2. أنشئ مفتاح SSH جديد أو رفع مفتاح موجود
3. حفظ المفتاح الخاص (id_rsa) على جهازك

---

## الخطوة 3: إعداد جدار النار

في Oracle Cloud Console:
1. اذهب إلى **Networking** → **Virtual Cloud Networks**
2. اختر الشبكة الخاصة بك
3. اذهب إلى **Security Lists**
4. أضف قواعد للسماح بالوصول:

### قواعد جدار النار:
```
Port 22 (SSH): 0.0.0.0/0
Port 80 (HTTP): 0.0.0.0/0
Port 443 (HTTPS): 0.0.0.0/0
```

---

## الخطوة 4: الاتصال بالخادم

```bash
# من جهازك المحلي
ssh -i /path/to/id_rsa ubuntu@YOUR_PUBLIC_IP

# يمكنك العثور على IP في Oracle Cloud Console
```

---

## الخطوة 5: نشر التطبيق

بعد الاتصال بالخادم:

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install -y python3 python3-pip python3-venv nginx git

# تثبيت Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# نسخ الملفات (إذا كنت تستخدم SCP من جهازك)
# scp -r /root/discord-bot-hosting ubuntu@YOUR_IP:/home/ubuntu/

# أو استنساخ من GitHub
# git clone <your-repo-url>
cd discord-bot-hosting

# تشغيل سكربت الإعداد
sudo ./setup_vps.sh
```

---

## الخطوة 6: الوصول إلى الموقع

1. افتح المتصفح
2. انتقل إلى: `http://YOUR_PUBLIC_IP`
3. سجل حساب جديد
4. ابدأ في إضافة بوتات ديسكورد!

---

## ملاحظات مهمة

### عنوان IP العام
- يمكنك العثور عليه في Oracle Cloud Console
- يبدو مثل: `129.154.xx.xx`

### مفتاح SSH
- احفظه في مكان آمن
- لا تشاركه مع أحد
- استخدمه للاتصال بالخادم

### النسخ الاحتياطي
- Oracle Cloud يوفر نسخ احتياطي مجاني
- يمكنك also إعداد نسخ احتياطي يدوي

---

## استكشاف الأخطاء

### لا يمكن الاتصال بالخادم
```bash
# تأكد من صحة IP
ping YOUR_PUBLIC_IP

# تأكد من أن المنافذ مفتوحة
ssh -v ubuntu@YOUR_PUBLIC_IP
```

### التطبيق لا يعمل
```bash
# على الخادم
sudo systemctl status discord-bot-hosting
sudo journalctl -u discord-bot-hosting -f
```

### خطأ 502 Bad Gateway
```bash
# تأكد من أن التطبيق يعمل
sudo systemctl restart discord-bot-hosting

# تحقق من Nginx
sudo nginx -t
sudo systemctl restart nginx
```

---

## روابط مفيدة

- Oracle Cloud Free Tier: https://cloud.oracle.com/free
- Ubuntu Server Guide: https://ubuntu.com/server/docs
- Nginx Documentation: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/
