import os
import json
import random
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s [%(levelname)s]: %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Проверка токена
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error('Токен бота не указан в переменной окружения BOT_TOKEN!')
    exit(1)

# Инициализация бота
application = Application.builder().token(BOT_TOKEN).build()

# Ссылки на посты в канале
tips = {
    'js': [
        "https://t.me/zametkyIT/159",
        "https://t.me/zametkyIT/125",
        "https://t.me/zametkyIT/220",
        "https://t.me/zametkyIT/225",
        "https://t.me/zametkyIT/150",
        "https://t.me/zametkyIT/114"
    ],
    'python': [
        "https://t.me/zametkyIT/159",
        "https://t.me/zametkyIT/125",
        "https://t.me/zametkyIT/220",
    ],
    'web': [
        "https://t.me/zametkyIT/159",
        "https://t.me/zametkyIT/148",
        "https://t.me/zametkyIT/225",
        "https://t.me/zametkyIT/220",
        "https://t.me/zametkyIT/163",
        "https://t.me/zametkyIT/150"
    ],
    'hacking': [
        "https://t.me/zametkyIT/181",
        "https://t.me/zametkyIT/226",
        "https://t.me/zametkyIT/220",
        "https://t.me/zametkyIT/202",
        "https://t.me/zametkyIT/201",
        "https://t.me/zametkyIT/128",
        "https://t.me/zametkyIT/232"
    ]
}

# Вопросы для игры "Угадай язык"
code_snippets = [
    {
        'snippet': "```\nfor (let i = 0; i < 5; i++) {\n    console.log(i);\n}\n```",
        'options': [
            {'text': "JavaScript", 'id': "js"},
            {'text': "Python", 'id': "py"},
            {'text': "C++", 'id': "cpp"}
        ],
        'correct': "js",
        'explanation': "Это цикл `for` в JavaScript с использованием `let` и `console.log`."
    },
    {
        'snippet': "```\nfor i in range(5):\n    print(i)\n```",
        'options': [
            {'text': "JavaScript", 'id': "js"},
            {'text': "Python", 'id': "py"},
            {'text': "Ruby", 'id': "rb"}
        ],
        'correct': "py",
        'explanation': "Это цикл `for` в Python с `range()` и `print()`."
    },
    {
        'snippet': "```\n#include <iostream>\nint main() {\n    std::cout << \"Hello\";\n    return 0;\n}\n```",
        'options': [
            {'text': "C++", 'id': "cpp"},
            {'text': "Java", 'id': "java"},
            {'text': "C#", 'id': "cs"}
        ],
        'correct': "cpp",
        'explanation': "Это код на C++ с использованием `iostream` и `std::cout`."
    },
    {
        'snippet': "```\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}\n```",
        'options': [
            {'text': "Python", 'id': "py"},
            {'text': "Java", 'id': "java"},
            {'text': "JavaScript", 'id': "js"}
        ],
        'correct': "java",
        'explanation': "Это код на Java с классом и методом `main`."
    }
]

# Сниппеты для игры "Собери код"
assemble_snippets = [
    {
        'parts': [
            "for i in range(3):",
            "    print(i)",
            "print(\"Done\")"
        ],
        'correct_order': [0, 1, 2],
        'explanation': "Это цикл в Python, где сначала задаётся цикл `for`, затем его тело с `print(i)`, и в конце `print(\"Done\")`."
    },
    {
        'parts': [
            "function sayHello() {",
            "    console.log(\"Hello!\");",
            "}",
            "sayHello();"
        ],
        'correct_order': [0, 1, 2, 3],
        'explanation': "Это функция в JavaScript: сначала объявление функции, затем её тело, закрытие функции и вызов `sayHello()`."
    }
]

# Глобальные состояния
user_state = {}
user_favorites = {}
user_favorites_state = {}
user_game_state = {}
user_assemble_state = {}
user_theme = {}

favorites_file = 'favorites.json'
themes_file = 'themes.json'

# Загрузка данных из файлов
if os.path.exists(favorites_file):
    with open(favorites_file, 'r', encoding='utf-8') as f:
        user_favorites = json.load(f)

if os.path.exists(themes_file):
    with open(themes_file, 'r', encoding='utf-8') as f:
        user_theme.update(json.load(f))

# Функции для работы с файлами
def save_favorites():
    with open(favorites_file, 'w', encoding='utf-8') as f:
        json.dump(user_favorites, f, ensure_ascii=False, indent=2)

def save_themes():
    with open(themes_file, 'w', encoding='utf-8') as f:
        json.dump(user_theme, f, ensure_ascii=False, indent=2)

# Работа с темами
def get_user_theme(user_id):
    return user_theme.get(str(user_id), 'light')

def set_user_theme(user_id, theme):
    user_theme[str(user_id)] = 'dark' if theme == 'dark' else 'light'
    save_themes()

# Команда /start с отправкой фото
async def start(update, context):
    logger.info(f'Команда /start получена от пользователя {update.message.from_user.id}')
    user_id = update.message.from_user.id
    theme = get_user_theme(user_id)
    theme_emoji = '🌙' if theme == 'dark' else '☀️'
    logger.info(f'Текущая тема пользователя {user_id}: {theme}')

    # Путь к фото
    photo_path = 'baby.jpeg'  # Убедитесь, что файл называется так и лежит в директории
    
    # Отправка фото
    if os.path.exists(photo_path):
        try:
            with open(photo_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=f'{theme_emoji} Привет! Добро пожаловать в бот канала @ZametkyIT! Выбери действие:'
                )
            logger.info(f'Фото отправлено пользователю {user_id}')
        except Exception as e:
            logger.error(f'Ошибка при отправке фото: {e}')
            await update.message.reply_text(f'{theme_emoji} Привет! Фото не загрузилось, но выбери действие:')
    else:
        logger.warning(f'Фото {photo_path} не найдено')
        await update.message.reply_text(f'{theme_emoji} Привет! Фото канала не найдено. Выбери действие:')

    # Отправка меню
    keyboard = [
        [InlineKeyboardButton("JavaScript", callback_data='js')],
        [InlineKeyboardButton("Python", callback_data='python')],
        [InlineKeyboardButton("Hacking", callback_data='hacking')],
        [InlineKeyboardButton("Web", callback_data='web')],
        [InlineKeyboardButton("📌 Избранное", callback_data='show_favorites'),
         InlineKeyboardButton("🎲 Рандом", callback_data='random_tip')],
        [InlineKeyboardButton("🎮 Угадай язык", callback_data='start_game'),
         InlineKeyboardButton("🧩 Собери код", callback_data='start_assemble')],
        [InlineKeyboardButton("🎨 Тема", callback_data='theme')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f'{theme_emoji} Выбери действие:', reply_markup=reply_markup)
    logger.info(f'Меню отправлено пользователю {user_id}')

# Команда /theme
async def theme_command(update, context):
    user_id = update.message.from_user.id
    current_theme = get_user_theme(user_id)
    theme_emoji = '🌙' if current_theme == 'dark' else '☀️'
    
    keyboard = [
        [InlineKeyboardButton("☀️ Светлая", callback_data='set_theme_light'),
         InlineKeyboardButton("🌙 Тёмная", callback_data='set_theme_dark')],
        [InlineKeyboardButton("🏠", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'{theme_emoji} 🎨 Текущая тема: {"🌙 Тёмная" if current_theme == "dark" else "☀️ Светлая"}\nВыбери тему:',
        reply_markup=reply_markup
    )

# Обработка callback-запросов
async def handle_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    theme = get_user_theme(user_id)
    theme_emoji = '🌙' if theme == 'dark' else '☀️'

    try:
        # Возврат к меню
        if data == 'back_to_menu':
            photo_path = 'photo.jpg'  # Убедитесь, что файл называется так
            if os.path.exists(photo_path):
                try:
                    with open(photo_path, 'rb') as photo:
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption=f'{theme_emoji} Привет! Добро пожаловать в бот канала @ZametkyIT! Выбери действие:'
                        )
                except Exception as e:
                    logger.error(f'Ошибка при отправке фото: {e}')
            else:
                await query.message.reply_text(f'{theme_emoji} Привет! Фото канала не найдено.')

            keyboard = [
                [InlineKeyboardButton("JavaScript", callback_data='js')],
                [InlineKeyboardButton("Python", callback_data='python')],
                [InlineKeyboardButton("Hacking", callback_data='hacking')],
                [InlineKeyboardButton("Web", callback_data='web')],
                [InlineKeyboardButton("📌 Избранное", callback_data='show_favorites'),
                 InlineKeyboardButton("🎲 Рандом", callback_data='random_tip')],
                [InlineKeyboardButton("🎮 Угадай язык", callback_data='start_game'),
                 InlineKeyboardButton("🧩 Собери код", callback_data='start_assemble')],
                [InlineKeyboardButton("🎨 Тема", callback_data='theme')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(f'{theme_emoji} Выбери действие:', reply_markup=reply_markup)
            await query.answer()

        # Выбор категории лайфхаков
        elif data in ['js', 'python', 'hacking', 'web']:
            category = data
            all_tips = tips[category]
            if not all_tips:
                await query.message.reply_text('Пока нет лайфхаков в этой категории!')
                await query.answer()
                return

            user_state[user_id] = {'category': category, 'index': 0, 'used_tips': []}
            tip = all_tips[0]
            user_state[user_id]['used_tips'].append(tip)
            
            prev_emoji = '🌑' if theme == 'dark' else '⬅️'
            next_emoji = '🌑' if theme == 'dark' else '➡️'
            keyboard = [
                [InlineKeyboardButton(prev_emoji, callback_data='prev'),
                 InlineKeyboardButton(next_emoji, callback_data='next')],
                [InlineKeyboardButton('❤️', callback_data=f'favorite_{tip}'),
                 InlineKeyboardButton('📌', callback_data='show_favorites')],
                [InlineKeyboardButton('🏠', callback_data='back_to_menu')]
            ]
            await query.message.reply_text(tip, reply_markup=InlineKeyboardMarkup(keyboard))
            await query.answer()

        # Навигация по лайфхакам
        elif data in ['next', 'prev']:
            if user_id not in user_state:
                await query.message.reply_text('Сначала выбери категорию!')
                await query.answer()
                return

            state = user_state[user_id]
            all_tips = tips[state['category']]
            available_tips = [t for t in all_tips if t not in state['used_tips']]
            new_index = state['index'] + (1 if data == 'next' else -1)

            if data == 'next' and available_tips:
                next_tip = available_tips[0]
                state['used_tips'].append(next_tip)
                new_index = all_tips.index(next_tip)
            elif new_index < 0:
                new_index = 0
            elif new_index >= len(all_tips):
                new_index = len(all_tips) - 1

            state['index'] = new_index
            current_tip = all_tips[new_index]
            
            prev_emoji = '🌑' if theme == 'dark' else '⬅️'
            next_emoji = '🌑' if theme == 'dark' else '➡️'
            keyboard = [
                [InlineKeyboardButton(prev_emoji, callback_data='prev'),
                 InlineKeyboardButton(next_emoji, callback_data='next')],
                [InlineKeyboardButton('❤️', callback_data=f'favorite_{current_tip}'),
                 InlineKeyboardButton('📌', callback_data='show_favorites')],
                [InlineKeyboardButton('🏠', callback_data='back_to_menu')]
            ]
            await query.message.edit_text(current_tip, reply_markup=InlineKeyboardMarkup(keyboard))
            await query.answer()

        # Добавление в избранное
        elif data.startswith('favorite_'):
            tip = data.replace('favorite_', '')
            if user_id not in user_favorites:
                user_favorites[user_id] = []
            if tip not in user_favorites[user_id]:
                user_favorites[user_id].append(tip)
                save_favorites()
                await query.answer('Добавлено в избранное! ❤️')
            else:
                await query.answer('Уже в избранном!')

        # Показать избранное
        elif data == 'show_favorites':
            favorites = user_favorites.get(user_id, [])
            if not favorites:
                await query.message.reply_text('У тебя пока нет избранных лайфхаков!')
            else:
                page_size = 5
                user_favorites_state[user_id] = user_favorites_state.get(user_id, {'page': 0})
                page = user_favorites_state[user_id]['page']
                start = page * page_size
                end = start + page_size
                paginated_favorites = favorites[start:end]
                total_pages = (len(favorites) + page_size - 1) // page_size

                prev_emoji = '🌑 Пред.' if theme == 'dark' else '⬅️ Пред.'
                next_emoji = '🌑 След.' if theme == 'dark' else '➡️ След.'
                keyboard = [
                    [InlineKeyboardButton(prev_emoji, callback_data='fav_prev_page'),
                     InlineKeyboardButton(next_emoji, callback_data='fav_next_page')],
                    [InlineKeyboardButton('🏠', callback_data='back_to_menu')]
                ]
                await query.message.reply_text(
                    f'{theme_emoji} Избранное (страница {page + 1} из {total_pages}):\n' + '\n'.join(paginated_favorites),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            await query.answer()

        # Навигация по страницам избранного
        elif data in ['fav_next_page', 'fav_prev_page']:
            favorites = user_favorites.get(user_id, [])
            if not favorites:
                await query.message.reply_text('У тебя пока нет избранных лайфхаков!')
                await query.answer()
                return

            page_size = 5
            user_favorites_state[user_id] = user_favorites_state.get(user_id, {'page': 0})
            page = user_favorites_state[user_id]['page']
            total_pages = (len(favorites) + page_size - 1) // page_size
            page += 1 if data == 'fav_next_page' else -1

            if page < 0 or page >= total_pages:
                await query.answer()
                return

            user_favorites_state[user_id]['page'] = page
            start = page * page_size
            end = start + page_size
            paginated_favorites = favorites[start:end]

            prev_emoji = '🌑 Пред.' if theme == 'dark' else '⬅️ Пред.'
            next_emoji = '🌑 След.' if theme == 'dark' else '➡️ След.'
            keyboard = [
                [InlineKeyboardButton(prev_emoji, callback_data='fav_prev_page'),
                 InlineKeyboardButton(next_emoji, callback_data='fav_next_page')],
                [InlineKeyboardButton('🏠', callback_data='back_to_menu')]
            ]
            await query.message.edit_text(
                f'{theme_emoji} Избранное (страница {page + 1} из {total_pages}):\n' + '\n'.join(paginated_favorites),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await query.answer()

        # Случайный лайфхак
        elif data == 'random_tip':
            all_tips = [tip for sublist in tips.values() for tip in sublist]
            random_tip = random.choice(all_tips)
            keyboard = [
                [InlineKeyboardButton('❤️', callback_data=f'favorite_{random_tip}')],
                [InlineKeyboardButton('🏠', callback_data='back_to_menu')]
            ]
            await query.message.reply_text(f'{theme_emoji} {random_tip}', reply_markup=InlineKeyboardMarkup(keyboard))
            await query.answer()

        # Установка темы
        elif data in ['set_theme_light', 'set_theme_dark']:
            new_theme = 'dark' if data == 'set_theme_dark' else 'light'
            set_user_theme(user_id, new_theme)
            new_theme_emoji = '🌙' if new_theme == 'dark' else '☀️'
            keyboard = [
                [InlineKeyboardButton("☀️ Светлая", callback_data='set_theme_light'),
                 InlineKeyboardButton("🌙 Тёмная", callback_data='set_theme_dark')],
                [InlineKeyboardButton("🏠", callback_data='back_to_menu')]
            ]
            await query.message.edit_text(
                f'{new_theme_emoji} 🎨 Тема успешно изменена на: {"🌙 Тёмная" if new_theme == "dark" else "☀️ Светлая"}\nНастройки применятся к следующим сообщениям!',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await query.answer('Тема изменена!')

    except Exception as e:
        logger.error(f'Ошибка для пользователя {user_id}: {e}')
        await query.message.reply_text('Что-то пошло не так, попробуй снова!')
        await query.answer()

# Регистрация обработчиков
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('theme', theme_command))
application.add_handler(CallbackQueryHandler(handle_callback))

# Запуск бота
if __name__ == '__main__':
    logger.info('Бот запущен!')
    application.run_webhook(
        listen='0.0.0.0',
        port=8443,
        url_path=BOT_TOKEN,
       webhook_url=f'https://99f0-138-124-123-12.ngrok-free.app/{BOT_TOKEN}'
    )

    

