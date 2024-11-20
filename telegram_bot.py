import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters, CallbackQueryHandler  # إضافة الاستيراد هنا

# المجلد الذي سيتم حفظ الصور فيه
save_folder = 'saved_photos'

# قائمة لتخزين أسماء الصور
saved_photos = []

# دالة لحفظ الصورة
async def save_photo(update: Update, context: CallbackContext) -> None:
    global saved_photos

    # إنشاء المجلد إذا لم يكن موجودًا
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # الحصول على الصورة
    photo = update.message.photo[-1]  # أخذ الصورة بأعلى دقة
    file = await photo.get_file()  # الحصول على كائن الملف من الصورة
    file_name = f"{save_folder}/{photo.file_id}.jpg"  # اسم الملف بناءً على ID الصورة

    try:
        # تنزيل الصورة باستخدام رابط التنزيل
        await file.download_to_drive(file_name)  # استخدام الدالة الصحيحة لتحميل الصورة

        # إضافة اسم الصورة إلى القائمة
        saved_photos.append(file_name)

        # إرسال رسالة تأكيد للمستخدم
        await update.message.reply_text(f"تم حفظ الصورة بنجاح باسم: {file_name}")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء حفظ الصورة: {str(e)}")

# دالة عرض قائمة الصور المحفوظة
async def list_saved_photos(update: Update, context: CallbackContext) -> None:
    if not saved_photos:
        await update.message.reply_text("لا توجد صور محفوظة بعد.")
        return

    keyboard = []
    # إنشاء الأزرار لكل صورة في القائمة
    for index, photo in enumerate(saved_photos):
        keyboard.append([InlineKeyboardButton(f"صورة {index + 1}", callback_data=str(index))])

    # إنشاء واجهة المستخدم مع الأزرار
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال الرسالة للمستخدم مع عرض الأزرار
    await update.message.reply_text('اختر صورة لعرضها:', reply_markup=reply_markup)

# دالة التعامل مع الأزرار (اختيار صورة)
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # الحصول على الرقم الذي ضغط عليه المستخدم
    photo_index = int(query.data)

    if photo_index < len(saved_photos):
        # إرسال الصورة للمستخدم
        await query.message.reply_photo(photo=saved_photos[photo_index])
    else:
        await query.message.reply_text("الصورة غير موجودة.")

# دالة الرد على الأمر "/start"
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('مرحبًا! أرسل لي صورة وسأقوم بحفظها. لاختيار صورة محفوظة، اكتب /list.')

def main() -> None:
    # أدخل الـ Token الذي حصلت عليه من BotFather
    TOKEN = '7877420521:AAEcNNsVEo9JHFY_XkQcXFlkvDtp914FuDM'  # استبدل بـ التوكن الجديد

    # إعداد الـ Application باستخدام Token
    application = Application.builder().token(TOKEN).build()

    # إضافة معالج للأمر "/start"
    application.add_handler(CommandHandler("start", start))

    # إضافة معالج للأمر "/list" لعرض الصور
    application.add_handler(CommandHandler("list", list_saved_photos))

    # إضافة معالج للصور
    application.add_handler(MessageHandler(filters.PHOTO, save_photo))

    # إضافة معالج للأزرار
    application.add_handler(CallbackQueryHandler(button_handler))

    # بدء البوت
    application.run_polling()

if __name__ == '__main__':
    main()