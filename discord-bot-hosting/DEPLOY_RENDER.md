# نشر على Render - دليل خطوة بخطوة

## الخطوة 1: إنشاء حساب على GitHub

1. اذهب إلى: https://github.com
2. أنشئ حساباً جديداً (مجاناً)
3. سجل الدخول

## الخطوة 2: رفع الملفات إلى GitHub

### الطريقة الأولى: استخدام GitHub Website

1. اضغط على علامة **+** في الأعلى يمين واختر **New repository**
2. اكتب اسم المستودع: `discord-bot-hosting`
3. اختر **Public**
4. اضغط **Create repository**
5. اضغط **uploading an existing file**
6. اسحب جميع ملفات المشروع من مجلد `discord-bot-hosting`
7. اضغط **Commit changes**

### الطريقة الثانية: استخدام Git (إذا كان مثبتاً)

```bash
cd /root/discord-bot-hosting
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/discord-bot-hosting.git
git push -u origin main
```

## الخطوة 3: إنشاء حساب على Render

1. اذهب إلى: https://render.com
2. اضغط **Get Started for Free**
3. سجل الدخول بحساب GitHub
4. اختر **Sign up with GitHub**

## الخطوة 4: نشر التطبيق

1. في Render Dashboard، اضغط **New +**
2. اختر **Web Service**
3. اضغط **Connect a repository**
4. اختر مستودع `discord-bot-hosting` من GitHub
5. اضغط **Connect**

## الخطوة 5: إعدادات النشر

في صفحة الإعدادات:

- **Name**: discord-bot-hosting
- **Region**: Oregon (US West)
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: Free

اضغط **Advanced** وأضف متغيرات البيئة:

```
SECRET_KEY = (اضغط Generate ل GetValue)
PYTHON_VERSION = 3.11.0
```

اضغط **Create Web Service**

## الخطوة 6: الانتظار والتحقق

1. Render سيبدأ في بناء التطبيق (takes 2-3 minutes)
2. انتظر حتى ترى **Live** بجانب الخدمة
3. اضغط على الرابط الخاص بك (يبدو مثل: https://discord-bot-hosting.onrender.com)

## الخطوة 7: استخدام الموقع

1. افتح الرابط في المتصفح
2. سجل حساب جديد
3. ابدأ في إضافة بوتات ديسكورد!

---

## ملاحظات مهمة

### البوتات لن تعمل على Render
Render لا يسمح بتشغيل عمليات طويلة الأمد مثل بوتات ديسكورد مباشرة. إذا كنت تريد تشغيل بوتات فعلية، تحتاج VPS.

### الاستخدام الموصى به
- **للتجربة والاختبار**: Render مجاني وممتاز
- **للإنتاج الفعلي**: استخدم VPS (Oracle Cloud Free Tier)

### تحديث التطبيق
عندما تقوم بتحديث الكود في GitHub، سيقوم Render تلقائياً بتحديث التطبيق.

---

## استكشاف الأخطاء

### المشكلة: التطبيق لا يبني
```bash
# تأكد من أن requirements.txt يحتوي على جميع المتطلبات
# تأكد من أن Python version صحيح
```

### المشكلة: الخطأ 502
```bash
# تحقق من أن Start Command صحيح
# تحقق من السجلات في Render Dashboard
```

### المشكلة: لا يمكن رفع ملفات كبيرة
Render المجاني لديه حد 100MB لحجم الطلب.
