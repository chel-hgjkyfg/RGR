import logging
import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Применение nest_asyncio для работы с существующим циклом событий
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище заказов
orders = {}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Добро пожаловать в маркетплейс кроссовок! Введите запрос, например: "Поиск: Adidas".'
    )

# Обработчик поиска моделей
async def search_shoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.replace("Поиск:", "").strip().lower()
    shoes = {
        "nike": ["Nike Air Max", "Nike Revolution"],
        "adidas": ["Adidas Ultraboost", "Adidas NMD R1"]
    }

    # Поиск по моделям
    all_shoes = {model.lower(): model for brand in shoes.values() for model in brand}
    matches = [name for key, name in all_shoes.items() if query in key]

    if matches:
        await update.message.reply_text(f'Найдены модели: {", ".join(matches)}.')
    else:
        await update.message.reply_text('Модели не найдены. Попробуйте другой запрос.')

# Обработчик оформления заказа
async def order_shoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    order_text = "Ваш заказ оформлен."
    orders[user_id] = {
        "model": "Nike Air Max",  # Здесь можно добавить выбор модели
        "status": "Оформлен",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    await update.message.reply_text(order_text)

# Обработчик проверки статуса заказа
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    order = orders.get(user_id)
    if order:
        await update.message.reply_text(
            f'Статус: {order["status"]}. Модель: {order["model"]}. Дата: {order["timestamp"]}.'
        )
    else:
        await update.message.reply_text("У вас нет активных заказов.")

# Обработчик отмены заказа
async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in orders:
        del orders[user_id]
        await update.message.reply_text("Ваш заказ был отменен.")
    else:
        await update.message.reply_text("У вас нет заказов для отмены.")

# Главная функция для запуска бота
async def main() -> None:
    # Укажите токен вашего бота
    TOKEN = "7649188289:AAH6ih2yrauyEblVognT2jfOPbdL8_esrgo"

    # Создание приложения
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_shoes))
    app.add_handler(CommandHandler("order", order_shoes))
    app.add_handler(CommandHandler("status", check_status))
    app.add_handler(CommandHandler("cancel", cancel_order))

    # Запуск бота
    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    await app.run_polling()

# Запуск программы
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"Ошибка выполнения: {e}")
