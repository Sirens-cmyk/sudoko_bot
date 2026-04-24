import logging
import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# تنظیمات لاگ برای عیب‌یابی
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دریافت توکن از متغیرهای محیطی رانفلر (BOT_TOKEN)
TOKEN = os.getenv("BOT_TOKEN")

def generate_sudoku():
    """ایجاد یک جدول سودوکو ساده (تعدادی از خانه‌ها پر شده)"""
    board = [[0 for _ in range(9)] for _ in range(9)]
    # پر کردن ۱۰ خانه به صورت تصادفی برای شروع بازی
    filled = 0
    while filled < 10:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] == 0:
            board[r][c] = random.randint(1, 9)
            filled += 1
    return board

def get_board_keyboard(board):
    """ساخت کیبورد شیشه‌ای برای نمایش جدول سودوکو"""
    keyboard = []
    for r in range(9):
        row = []
        for c in range(9):
            val = board[r][c] if board[r][c] != 0 else " "
            # هر دکمه مختصات خودش رو به تابع هندلر می‌فرسته
            row.append(InlineKeyboardButton(str(val), callback_data=f"click_{r}_{c}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def start(update: Update, context: CallbackContext):
    """شروع بازی با دستور /start"""
    board = generate_sudoku()
    context.user_data['board'] = board
    update.message.reply_text(
        "🎮 به بازی سودوکو در بله خوش اومدی!\n\n"
        "روی هر خونه کلیک کنی، عددش تغییر می‌کنه. سعی کن جدول رو حل کنی!",
        reply_markup=get_board_keyboard(board)
    )

def handle_click(update: Update, context: CallbackContext):
    """مدیریت کلیک روی دکمه‌های جدول"""
    query = update.callback_query
    data = query.data.split('_')
    r, c = int(data[1]), int(data[2])
    
    board = context.user_data.get('board')
    if not board:
        query.answer("خطا: بازی یافت نشد. دوباره /start بزنید.")
        return

    # با هر کلیک، عدد خانه یکی زیاد می‌شود (۱ تا ۹ و بعد خالی)
    current_val = board[r][c]
    board[r][c] = (current_val + 1) if current_val < 9 else 0
    
    # آپدیت کردن کیبورد بدون ارسال پیام جدید
    query.edit_message_reply_markup(reply_markup=get_board_keyboard(board))
    query.answer()

def main():
    if not TOKEN:
        print("خطا: توکن بات یافت نشد! حتما BOT_TOKEN را در رانفلر تنظیم کنید.")
        return

    # تنظیم Updater با آدرس سرور بله
    updater = Updater(TOKEN, use_context=True, base_url='https://tapi.bale.ai/bot')
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_click))

    print("بات سودوکو در حال اجراست...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
