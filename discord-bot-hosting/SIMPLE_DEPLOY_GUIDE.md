# دليل النشر السهل - Render (مجاني)

## ما تحتاجه:
- حساب GitHub (مجاني)
- حساب Render (مجاني)

---

## الخطوة 1: إنشاء حساب GitHub

1. اذهب إلى: **https://github.com**
2. اضغط **Sign up**
3. أدخل بريدك الإلكتروني وكلمة المرور
4. أكمل التسجيل

---

## الخطوة 2: رفع الملفات

1. سجل الدخول على GitHub
2. اضغط علامة **+** في الأعلى يمين
3. اختر **New repository**
4. اكتب: `discord-bot-hosting`
5. اختر **Public**
6. اضغط **Create repository**
7. اضغط **uploading an existing file**
8. افتح مجلد `discord-bot-hosting` على جهازك
9. اسحب كل الملفات للمتصفح
10. اضغط **Commit changes**

---

## الخطوة 3: إنشاء حساب Render

1. اذهب إلى: **https://render.com**
2. اضغط **Get Started for Free**
3. اضغط **Sign up with GitHub**
4. اختر **Authorize render**

---

## الخطوة 4: نشر التطبيق

1. في Render، اضغط **New +**
2. اختر **Web Service**
3. اضغط **Connect a repository**
4. اختر `discord-bot-hosting`
5. اضغط **Connect**

---

## الخطوة 5: الإعدادات

اكتب هذه الإعدادات:

| الحقل | القيمة |
|--------|--------|
| Name | discord-bot-hosting |
| Region | Oregon |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Plan | Free |

اضغط **Create Web Service**

---

## الخطوة 6: الانتظار

1. انتظر 2-3 دقائق حتى ينتهي البناء
2. اضغط على الرابط الظاهر

---

## الخطوة 7: الاستخدام

1. افتح الرابط
2. سجل حساب جديد
3. ابدأ الاستخدام!

---

## روابط مساعدة

- **GitHub**: https://github.com
- **Render**: https://render.com
- **الدعم**: https://render.com/docs
