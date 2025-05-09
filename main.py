import asyncio
import schedule
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TELEGRAM_BOT_TOKEN, logger, check_config
from storage import Storage
from parsers import VKParser, TwitterParser

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Initialize storage and parsers
storage = Storage()
vk_parser = VKParser()
twitter_parser = TwitterParser()

def get_show_posts_keyboard(source_type: str, source_id: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for showing posts"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "📝 Показать последние посты",
        callback_data=f"show_posts:{source_type}:{source_id}"
    ))
    return keyboard

@dp.callback_query_handler(lambda c: c.data.startswith('show_posts:'))
async def process_show_posts(callback_query: types.CallbackQuery):
    """Handle show posts button click"""
    try:
        # Parse callback data
        _, source_type, source_id = callback_query.data.split(':')

        # Get posts based on source type
        if source_type == 'vk':
            posts = vk_parser.get_posts(source_id)
            source = next((s for s in storage.get_sources('vk') if s['id'] == source_id), None)
            if not source:
                await callback_query.answer("Источник не найден")
                return

            # Send posts
            await callback_query.message.answer(f"📢 Последние посты из группы VK '{source['name']}':")
            for post in posts:
                message = f"{post['text']}\n\n🔗 {post['link']}"
                await callback_query.message.answer(message)

        elif source_type == 'twitter':
            tweets = twitter_parser.get_tweets(source_id)
            source = next((s for s in storage.get_sources('twitter') if s['id'] == source_id), None)
            if not source:
                await callback_query.answer("Источник не найден")
                return

            # Send tweets
            await callback_query.message.answer(f"🐦 Последние твиты от {source['name']}:")
            for tweet in tweets:
                message = f"{tweet['text']}\n\n🔗 {tweet['link']}"
                await callback_query.message.answer(message)

        await callback_query.answer()

    except Exception as e:
        logger.error(f"Error showing posts: {e}")
        await callback_query.answer("Произошла ошибка при получении постов")

# Command handlers
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Add chat to receive messages
    storage.add_chat(message.chat.id)
    await message.answer(
        "👋 Привет! Я бот для агрегации новостей из VK и Twitter.\n\n"
        "Доступные команды:\n"
        "/help - Показать справку\n"
        "/add_vk_source <group_id> - Добавить группу VK\n"
        "/add_twitter_source <username> - Добавить аккаунт Twitter\n"
        "/list_sources - Показать все источники\n"
        "/remove_source <source_id> - Удалить источник\n"
        "/stop - Отписаться от уведомлений"
    )

@dp.message_handler(commands=['stop'])
async def cmd_stop(message: types.Message):
    storage.remove_chat(message.chat.id)
    await message.answer("Вы отписались от уведомлений. Чтобы снова получать новости, отправьте /start")

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer(
        "📚 Справка по командам:\n\n"
        "/add_vk_source <group_id> - Добавить группу VK как источник новостей\n"
        "/add_twitter_source <username> - Добавить аккаунт Twitter как источник новостей\n"
        "/list_sources - Показать список всех добавленных источников\n"
        "/remove_source <source_id> - Удалить источник по его ID\n"
        "/stop - Отписаться от уведомлений\n\n"
        "Примеры:\n"
        "/add_vk_source 123456\n"
        "/add_twitter_source elonmusk"
    )

@dp.message_handler(commands=['add_vk_source'])
async def cmd_add_vk_source(message: types.Message):
    try:
        group_id = message.text.split()[1]
        group_info = vk_parser.get_group_info(group_id)

        if not group_info:
            await message.answer("❌ Не удалось найти группу VK. Проверьте ID группы.")
            return

        if storage.add_source('vk', group_id, group_info['name']):
            await message.answer(
                f"✅ Группа VK '{group_info['name']}' успешно добавлена!",
                reply_markup=get_show_posts_keyboard('vk', group_id)
            )
        else:
            await message.answer("❌ Эта группа уже добавлена.")
    except IndexError:
        await message.answer("❌ Укажите ID группы VK. Пример: /add_vk_source 123456")
    except Exception as e:
        logger.error(f"Error adding VK source: {e}")
        await message.answer("❌ Произошла ошибка при добавлении группы VK.")

@dp.message_handler(commands=['add_twitter_source'])
async def cmd_add_twitter_source(message: types.Message):
    try:
        username = message.text.split()[1]
        user_info = twitter_parser.get_user_info(username)

        if not user_info:
            await message.answer("❌ Не удалось найти пользователя Twitter. Проверьте имя пользователя.")
            return

        if storage.add_source('twitter', username, user_info.name):
            await message.answer(
                f"✅ Аккаунт Twitter '{user_info.name}' успешно добавлен!",
                reply_markup=get_show_posts_keyboard('twitter', username)
            )
        else:
            await message.answer("❌ Этот аккаунт уже добавлен.")
    except IndexError:
        await message.answer("❌ Укажите имя пользователя Twitter. Пример: /add_twitter_source elonmusk")
    except Exception as e:
        logger.error(f"Error adding Twitter source: {e}")
        await message.answer("❌ Произошла ошибка при добавлении аккаунта Twitter.")

@dp.message_handler(commands=['list_sources'])
async def cmd_list_sources(message: types.Message):
    sources = storage.get_sources()
    if not sources['vk'] and not sources['twitter']:
        await message.answer("📝 Список источников пуст.")
        return

    response = "📝 Список источников:\n\n"

    if sources['vk']:
        response += "VK группы:\n"
        for source in sources['vk']:
            response += f"- {source['name']} (ID: {source['id']})\n"
            # Add show posts button for each source
            keyboard = get_show_posts_keyboard('vk', source['id'])
            await message.answer(response, reply_markup=keyboard)
            response = ""

    if sources['twitter']:
        response += "\nTwitter аккаунты:\n"
        for source in sources['twitter']:
            response += f"- {source['name']} (@{source['id']})\n"
            # Add show posts button for each source
            keyboard = get_show_posts_keyboard('twitter', source['id'])
            await message.answer(response, reply_markup=keyboard)
            response = ""

@dp.message_handler(commands=['remove_source'])
async def cmd_remove_source(message: types.Message):
    try:
        source_id = message.text.split()[1]
        removed = False

        # Try to remove from VK sources
        if storage.remove_source('vk', source_id):
            removed = True

        # Try to remove from Twitter sources
        if storage.remove_source('twitter', source_id):
            removed = True

        if removed:
            await message.answer("✅ Источник успешно удален!")
        else:
            await message.answer("❌ Источник не найден.")
    except IndexError:
        await message.answer("❌ Укажите ID источника. Пример: /remove_source 123456")

async def check_new_posts():
    """Check for new posts from all sources"""
    try:
        # Get all chat IDs that should receive messages
        chat_ids = storage.get_chats()
        if not chat_ids:
            logger.info("No chats registered to receive messages")
            return

        # Check VK sources
        for source in storage.get_sources('vk'):
            posts = vk_parser.get_new_posts(source['id'], source['last_post_id'])
            for post in reversed(posts):
                message = (
                    f"📢 Новый пост из группы VK '{source['name']}':\n\n"
                    f"{post['text']}\n\n"
                    f"🔗 {post['link']}"
                )
                # Send message to all registered chats
                for chat_id in chat_ids:
                    try:
                        await bot.send_message(chat_id=chat_id, text=message)
                    except Exception as e:
                        logger.error(f"Error sending message to chat {chat_id}: {e}")
                storage.update_last_post_id('vk', source['id'], post['id'])

        # Check Twitter sources
        for source in storage.get_sources('twitter'):
            tweets = twitter_parser.get_tweets(source['id'], source['last_post_id'])
            for tweet in reversed(tweets):
                message = (
                    f"🐦 Новый твит от {source['name']}:\n\n"
                    f"{tweet['text']}\n\n"
                    f"🔗 {tweet['link']}"
                )
                # Send message to all registered chats
                for chat_id in chat_ids:
                    try:
                        await bot.send_message(chat_id=chat_id, text=message)
                    except Exception as e:
                        logger.error(f"Error sending message to chat {chat_id}: {e}")
                storage.update_last_post_id('twitter', source['id'], tweet['id'])

    except Exception as e:
        logger.error(f"Error checking new posts: {e}")

async def scheduler():
    """Run the scheduler"""
    while True:
        await check_new_posts()
        await asyncio.sleep(600)  # 10 minutes

async def main():
    # Check configuration
    if not check_config():
        logger.error("Missing required environment variables. Please check your .env file.")
        return

    # Start the scheduler
    asyncio.create_task(scheduler())

    # Start the bot
    logger.info("Starting bot...")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
