import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = "8404830989:AAFr5avY_2WeR5ivnCLommSDa9ooJrqgTMM"

# قواميس لحفظ البيانات مؤقتاً
search_results = {}
video_info = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(  
        """=اهلا بك في بوت ابا الحارث لتحميل فيديوهات=\n\n"""
        "📜 الأوامر المتاحة:\n"
        "▫️ بحث - البحث عما تربد  في يوتيوب\n"
        "▫️ صوت - تحميل الصوت فقط\n"
        "▫️ أرسل رابط للتحميل مباشرة\n\n"
        "أمثلة:\n"
        " بحث هنا اكتب ما تبحث \n"
        "صوت هنا رابط الفيديو \n\n"
        "المواقع المدعومة:\n"
        "🔴 يوتيوب | 📸 إنستجرام | 📘 فيسبوك\n"
        "🎵 تيك توك | 🐦 تويتر"
        """\n__|by dev|@code1203g|___""")
                                     

def format_number(num):
    """تنسيق الأرقام"""
    if not num:
        return "غير معلوم"
    try:
        num = int(num)
        if num >= 1000000:
            return f"{num/1000000:.1f} مليون"
        elif num >= 1000:
            return f"{num/1000:.1f} ألف"
        return str(num)
    except:
        return "غير معلوم"


def format_duration(seconds):
    """تحويل الثواني إلى صيغة مقروءة"""
    if not seconds:
        return "غير معلوم"
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours} ساعة و{minutes} دقيقة"
        return f"{minutes} دقيقة و{secs} ثانية"
    except:
        return "غير معلوم"


async def search_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إذا كان الأمر "بحث" بدون نص
    if update.message.text.strip() == "بحث":
        await update.message.reply_text(
            "❌ تفضل بكتابة ما تريد البحث عنه\n\n" "مثال:\n" "بحث ما تريده"
        )
        return

    # استخراج نص البحث (إزالة كلمة "بحث" من البداية)
    query = update.message.text.replace("بحث", "", 1).strip()

    if not query:
        await update.message.reply_text(
            "❌ تفضل بكتابة ما تريد البحث عنه\n\n" "مثال:\n" "بحث ما تريده "
        )
        return

    msg = await update.message.reply_text(f"🔍 جارٍ البحث عن: {query}")

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch7:{query}"
            results = ydl.extract_info(search_query, download=False)

        if not results or "entries" not in results or not results["entries"]:
            await msg.edit_text("❌ لم نعثر على نتائج")
            return

        user_id = update.effective_user.id
        search_results[user_id] = results["entries"]

        keyboard = []
        for i, video in enumerate(results["entries"][:7], 1):
            title = video.get("title", "بلا عنوان")
            short_title = title[:35] + "..." if len(title) > 35 else title

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{i}. {short_title}", callback_data=f"info_{i-1}"
                    )
                ]
            )

        keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await msg.edit_text(
            f"🔍 نتائج البحث عن: {query}\n\n" "اختر الفيديو الذي تريده:",
            reply_markup=reply_markup,
        )

    except Exception as e:
        await msg.edit_text(f"❌ خطأ في البحث: {str(e)}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "cancel":
        await query.edit_message_text("❌ تم الإلغاء")
        if user_id in search_results:
            del search_results[user_id]
        if user_id in video_info:
            del video_info[user_id]
        return

    if query.data == "back":
        if user_id not in search_results:
            await query.edit_message_text("❌ انتهت صلاحية البحث")
            return

        keyboard = []
        for i, video in enumerate(search_results[user_id][:7], 1):
            title = video.get("title", "بلا عنوان")
            short_title = title[:35] + "..." if len(title) > 35 else title
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{i}. {short_title}", callback_data=f"info_{i-1}"
                    )
                ]
            )

        keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🔍 محصول بحثك:\n\n" "اختر الفيديو:", reply_markup=reply_markup
        )
        return

    if query.data.startswith("info_"):
        index = int(query.data.split("_")[1])

        if user_id not in search_results:
            await query.edit_message_text("❌ انتهت صلاحية البحث")
            return

        video = search_results[user_id][index]
        video_info[user_id] = video

        title = video.get("title", "بلا عنوان")
        duration = format_duration(video.get("duration"))
        views = format_number(video.get("view_count"))
        channel = video.get("uploader", "غير معلوم")

        info_text = (
            f"🎬 {title}\n\n"
            f"👤 القناة: {channel}\n"
            f"👁 المشاهدات: {views}\n"
            f"⏱ المدة: {duration}\n\n"
            "اختر نوع التحميل:"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "📹 فيديو جودة عالية", callback_data=f"dl_best_{index}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📹 فيديو جودة متوسطة", callback_data=f"dl_medium_{index}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📹 فيديو جودة منخفضة", callback_data=f"dl_low_{index}"
                )
            ],
            [InlineKeyboardButton("🎵 صوت فقط", callback_data=f"dl_audio_{index}")],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="back"),
                InlineKeyboardButton("❌ إلغاء", callback_data="cancel"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(info_text, reply_markup=reply_markup)
        return

    if query.data.startswith("dl_"):
        parts = query.data.split("_")
        quality = parts[1]
        index = int(parts[2])

        if user_id not in search_results:
            await query.edit_message_text("❌ انتهت صلاحية البحث")
            return

        video = search_results[user_id][index]
        video_url = f"https://www.youtube.com/watch?v={video['id']}"

        await download_with_quality(query, context, video_url, quality, video["title"])


async def download_with_quality(query, context, url, quality, title):
    """تحميل الفيديو بجودة محددة"""
    await query.edit_message_text("اصبر قليلا ...")

    try:
        if quality == "best":
            format_str = "best[filesize<50M]/best"
            quality_name = "جودة عالية"
        elif quality == "medium":
            format_str = "best[height<=480][filesize<30M]/best[height<=480]"
            quality_name = "جودة متوسطة"
        elif quality == "low":
            format_str = "worst[filesize<20M]/worst"
            quality_name = "جودة منخفضة"
        elif quality == "audio":
            format_str = "bestaudio/best"
            quality_name = "صوت فقط"

        ydl_opts = {
            "outtmpl": "%(title)s.%(ext)s",
            "format": format_str,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 300,
            "retries": 20,
            "fragment_retries": 20,
            "nocheckcertificate": True,
          'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
    'cookiefile': '/cookies.txt',  # ✅ أضف هذا السطر
}  
        if quality == "audio":
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        await query.edit_message_text(f"اصبر قليلا..سيتم تحميل {quality_name}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

            if quality == "audio" and not file_name.endswith(".mp3"):
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"

        await query.edit_message_text("📤 جارٍ الإرسال")

        if quality == "audio":
            with open(file_name, "rb") as audio:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio,
                    caption=f"🎵 {title}\n\n✅تم حمد لله تحميل ",
                    read_timeout=300,
                    write_timeout=300,
                )
        else:
            with open(file_name, "rb") as video:
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=video,
                    caption=f"🎬 {title}\n📊 {quality_name}\n\n✅ تم على بركة الله تحميل ",
                    read_timeout=300,
                    write_timeout=300,
                )

        os.remove(file_name)
        await query.edit_message_text(f"✅ تم الإرسال بنجاح\n📊 {quality_name}")

    except Exception as e:
        await query.edit_message_text(f"❌ خطأ: {str(e)}")

# ✅ تحقق من خطأ إنستجرام
        if 'instagram' in url.lower() and ('rate-limit' in error_msg or 'login required' in error_msg):
            await msg.edit_text(
                "❌ إنستجرام يمنع التحميل حالياً\n\n"
                "الحلول:\n"
                "1️⃣ حاول مرة أخرى بعد قليل\n"
                "2️⃣ استخدم رابط من موقع آخر\n"
                "3️⃣ حمّل الفيديو من المتصفح\n\n"
                "📸 إنستجرام يحد من التحميل المتكرر"
            )
        else:
            await msg.edit_text(f"❌ خطأ: {error_msg}")
async def download_audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # استخراج الوصلة (إزالة كلمة "صوت" من البداية)
    text = update.message.text.replace("صوت", "", 1).strip()

    if not text or not text.startswith("http"):
        await update.message.reply_text(
            "تفضل بإرفاق رابط \n\n" "مثال:\n" "صوت  هنا رابط التحميل "
        )
        return

    url = text
    msg = await update.message.reply_text("🎵 جارٍ تحميل الصوت")

    try:
        ydl_opts = {
            "outtmpl": "%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "socket_timeout": 300,
            "retries": 20,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
     'cookiefile': '/cookies.txt',  # ✅ أضف هذا الس       
}
        

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
            file_name = file_name.rsplit(".", 1)[0] + ".mp3"

        await msg.edit_text("📤 جارٍ الإرسال")

        with open(file_name, "rb") as audio:
            await update.message.reply_audio(
                audio=audio,
                caption="🎵 تم التحميل بنجاح",
                read_timeout=300,
                write_timeout=300,
            )

        os.remove(file_name)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # إذا بدأت الرسالة بـ "بحث"
    if text.startswith("بحث"):
        await search_youtube(update, context)
        return

    # إذا بدأت الرسالة بـ "صوت"
    if text.startswith("صوت"):
        await download_audio_command(update, context)
        return

    # إذا كانت الرسالة وصلة
    if text.startswith("http"):
        await download_video(update, context)
        return

    # رسالة افتراضية
    await update.message.reply_text(
        "❌ لم أفهم طلبك\n\n"
        "الأوامر المتاحة:\n"
        "▫️ بحث [نص] - للبحث في يوتيوب\n"
        "▫️ صوت [رابط] - لتحميل الصوت فقط\n"
        "▫️ أرسل رابط - لتحميل الفيديو"
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text(" تريث قليلا...")

    try:
        ydl_opts = {
            "outtmpl": "%(title)s.%(ext)s",
            "format": "best[filesize<50M]/best",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 300,
            "retries": 20,
            "fragment_retries": 20,
            "nocheckcertificate": True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate' ,
    'cookiefile': '/home/container/cookies.txt',  # ✅ أضف هذا الس         
}
        

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await msg.edit_text("📤 جارٍ الإرسال")

        with open(file_name, "rb") as video:
            await update.message.reply_video(
                video=video,
                read_timeout=300,
                write_timeout=300,
            )

        os.remove(file_name)
        await msg.delete()
        await update.message.reply_text("✅ حمد لله تم تحميل بنجاح")

    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # معالج الأوامر
    app.add_handler(CommandHandler("start", start))

    # معالج الأزرار
    app.add_handler(CallbackQueryHandler(button_callback))

    # معالج جميع الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل الآن")
    print("=" * 50)
    print("📜 الأوامر:")
    print("   🔍 بحث - للبحث في يوتيوب")
    print("   🎵 صوت - لتحميل الصوت")
    print("   📹 وصلة - لتحميل الفيديو")
    print("=" * 50)
    app.run_polling()
