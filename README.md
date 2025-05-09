# News Aggregator Telegram Bot

Telegram бот для агрегации новостей из VK и Twitter. Бот периодически проверяет новые посты и отправляет их в указанные чаты.

## Возможности

- Поддержка источников VK и Twitter
- Автоматическая проверка новых постов каждые 5 минут
- Фильтрация рекламных постов
- Поддержка медиа-контента (фото, видео)
- Логирование всех действий
- Сохранение списка источников

## Требования

- Python 3.7+
- Telegram Bot Token
- VK API Token
- Twitter API Credentials

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/python-parser.git
cd python-parser
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` с необходимыми токенами:
```
TELEGRAM_BOT_TOKEN=ваш_токен_телеграм_бота
VK_ACCESS_TOKEN=ваш_токен_вк
TWITTER_API_KEY=ваш_api_key
TWITTER_API_SECRET=ваш_api_secret
TWITTER_ACCESS_TOKEN=ваш_access_token
TWITTER_ACCESS_TOKEN_SECRET=ваш_access_token_secret
TWITTER_BEARER_TOKEN=ваш_bearer_token
```

## Использование

1. Запустите бота:
```bash
python main.py
```

2. В Telegram доступны следующие команды:
- `/start` - Начать работу с ботом
- `/add_vk_source <group_id>` - Добавить источник VK
- `/add_twitter_source <username>` - Добавить источник Twitter
- `/list_sources` - Показать список источников
- `/remove_source <source_id>` - Удалить источник
- `/help` - Показать справку

## Получение токенов

### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота

### VK API Token
1. Перейдите на https://vk.com/dev/access_token
2. Создайте Standalone-приложение
3. Получите токен доступа

### Twitter API Tokens
1. Перейдите на https://developer.twitter.com/
2. Создайте проект и приложение
3. В настройках приложения:
   - Включите OAuth 1.0a
   - Установите тип приложения "Web App, Automated App or Bot"
   - Установите разрешения "Read and Write"
4. Получите необходимые токены

## Лицензия

MIT
