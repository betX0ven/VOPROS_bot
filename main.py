from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, \
    CallbackQueryHandler
import logging
import re
from ban_users import ban_user, unban_user, check_ban
from ai_sort import text_clear, start_ai
from user_database import find_chat_id_by_username, save_user, init_db

# ID администратора
ADMIN_ID =  5281677719 #1362818165 #1774089592

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция обработки ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Произошла ошибка: {context.error}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "dislike":
        text = query["message"]["reply_to_message"]["text"]
        user_id = query["message"]["reply_to_message"]["from_user"]["id"]
        username = query["message"]["reply_to_message"]["from_user"]["username"]
        await query.edit_message_text(text="Вопрос перенаправлен администратору.")
        if str(username) == "None":
            save_user(str(user_id), user_id)
            username = user_id
        if not find_chat_id_by_username(username):
            save_user(username, user_id)
        await context.bot.send_message(chat_id=ADMIN_ID,
                                       text=f"Новый вопрос от пользователя @{username}:\n{text}\n\nОтветьте на это сообщение, чтобы отправить ответ пользователю.")


# Функция обработки вопросов от пользователей
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    with open('bad_words.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    ban_words = content.split()
    message = update.message.text.lower()

    if any(word in message for word in ban_words):
        # Отправляем сообщение "БАН"
        ban_user(user_id)
        check_word = False
        await update.message.reply_text("Ваш вопрос имеет нежелательное содержание. Вы будите заблокированы")
    else:
        # Можете добавить другой обработчик для чистых сообщений
        check_word = True

    if check_ban(user_id) != "ban" and check_word:# and user_id != ADMIN_ID:
        message = update.message.text
        messageС = text_clear(message)
        response = start_ai(messageС)
        message_id = update.message.message_id


        if str(username) == "None":
            save_user(str(user_id), user_id)
            username = user_id
        if not find_chat_id_by_username(username):
            save_user(username, user_id)

        print(username)

        if response:
            keyboard = [
                [InlineKeyboardButton("Не понравился ответ", callback_data="dislike")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(response, reply_markup=reply_markup, reply_to_message_id = message_id)
        #Уведомляем администратора и отправляем ID пользователя
        else:

            await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новый вопрос от пользователя @{username} :\n{message}\n\nОтветьте на это сообщение, чтобы отправить ответ пользователю."
         )

            await update.message.reply_text(f"Вопрос отправлен на рассмотрение")
    



# Функция обработки ответов от администратора
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка, что это ответ на вопрос
    if update.message.reply_to_message and update.message.reply_to_message.text:
        original_message = update.message.reply_to_message.text
        # Используем регулярное выражен ие для извлечения ID из строки, например, "ID: 1362818165"
        match = re.search(r"ID:\s*(\d+)", original_message)
        match1 = re.search(r"@\w+", original_message)


        if match1:
            user_name = match1.group(0).replace("@", "")
            user_id = find_chat_id_by_username(user_name)

            print(user_id)
            # Отправляем ответ пользователю
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Ответ от администратора:\n{update.message.text}"
            )

            # Подтверждаем администратору, что ответ отправлен
            await update.message.reply_text(f"Ответ отправлен пользователю @{user_name}")
        else:
            # Если не удается извлечь ID
            await update.message.reply_text("Не удалось извлечь ID пользователя из сообщения.")
    else:
        # Если это не ответ на сообщение, то уведомляем администратора
        await update.message.reply_text("Пожалуйста, ответьте на сообщение пользователя.")


# Функция старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте! Вы обратились к виртуальному ассистенту министра образования. Вы можете оставить своё обращение здесь.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(user_id)
    # Проверка, что это ответ на вопрос
    if update.message.reply_to_message and update.message.reply_to_message.text and user_id == ADMIN_ID:
        original_message = update.message.reply_to_message.text
        # Используем регулярное выражение для извлечения ID из строки, например, "ID: 1362818165"
        match1 = re.search(r"@\w+", original_message)
        if match1:
            user_name = match1.group(0).replace("@", "")
            if str(user_name) == "None":
                save_user(str(user_id), user_id)
                user_name = user_id
            user_id = find_chat_id_by_username(user_name)

            ban_user(user_id)
            print(f"пользователь{user_id}был забанен")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка, что это0 ответ на вопрос
    user_id = update.message.from_user.id
    if update.message.reply_to_message and update.message.reply_to_message.text and user_id == ADMIN_ID:
        original_message = update.message.reply_to_message.text
        # Используем регулярное выражение для извлечения ID из строки, например, "ID: 1362818165"
        match1 = re.search(r"@\w+", original_message)
        if match1:
            user_name = match1.group(0).replace("@", "")
            if str(user_name) == "None":
                save_user(str(user_id), user_id)
                user_name = user_id
            user_id = find_chat_id_by_username(user_name)
            unban_user(user_id)
            print(f"пользователь{user_id}был разбанен")


def main():
    # Создание приложения с вашим токеном
    application = Application.builder().token(
        "8077500567:AAEBoEpe4Vkn5n3nkalCWRQrEJOzVyMsIOU").build()  # Замените YOUR_BOT_TOKEN на ваш токен

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY,
                                           handle_user_message))  # Сообщения пользователей
    application.add_handler(MessageHandler(filters.REPLY, handle_admin_reply))  # Ответы администратора


    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)


    # Запуск бота
    application.run_polling(timeout=10)  # Увеличиваем таймаут до 10 секунд


if __name__ == "__main__":
    init_db()
    main()


