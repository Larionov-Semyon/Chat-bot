import os.path

import logging
from typing import Dict
from telegram import ForceReply
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from key import telegram_key_api

# БД (убрать позже, изменить)
import sqlite3
from getReview import StartDatabase, uploadReview
from searchReviews import adaptiveSearch
StartDatabase(os.path.exists('reviews.sqlite'))
base = sqlite3.connect('reviews.sqlite')

# Включить ведение журнала
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTION, NAME, REGION, CITY, THEME, COMMENT, SAVE, START = range(8)
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


reply_keyboard = [
    ['Оставить отзыв'],
    ['Найти организацию'],
    ['Подробнее...'],
]
markup_1 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard_1 = [
    ['Отправить'],
    ['Сбросить'],
]
markup_review = ReplyKeyboardMarkup(reply_keyboard_1, one_time_keyboard=True)

reply_keyboard_2 = [
    ['Регион', 'Город'],
    ['Тема', 'Название'],
    ['Сброс'],
]
markup_search = ReplyKeyboardMarkup(reply_keyboard_2, one_time_keyboard=True)

# Shortcut for ConversationHandler.END
END = ConversationHandler.END


def start(update: Update, context: CallbackContext) -> None:
    """НАЧАЛО. Выбираем - ищем НКО или делаем отзыв"""
    context.user_data.clear()
    user = update.effective_user
    update.message.reply_markdown_v2(f'Здравствуйте, {user.mention_markdown_v2()}\! ' + ' Вас приветсвует помощник НКО\.',)
    update.message.reply_text("Что Вы хотите сделать?",reply_markup=markup_1,)


def help(update: Update, _: CallbackContext) -> None:
    """Помощь"""
    update.message.reply_text('Помощь!')


def remember(update, context, category):
    """"Запоминаем введенные пользователем данные"""
    user_data = context.user_data
    text = update.message.text
    user_data[category] = text
    print('Записали {} в кат. {}'.format(text, category))


def review(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Введите название организации')
    return NAME


def name(update, context):
    update.message.reply_text('Укажите регион или пропустите этот пункт нажав /skip')
    remember(update, context, 'Name')
    return REGION


def region(update, context):
    update.message.reply_text('Укажите город или пропустите этот пункт нажав /skip')
    remember(update, context, 'Region')
    return CITY


def skip_region(update, context):
    context.user_data['Region'] = None
    return CITY


def city(update, context):
    update.message.reply_text('Укажите тематику организации или пропустите этот пункт нажав /skip')
    remember(update, context, 'City')
    return THEME


def skip_city(update, context):
    context.user_data['City'] = None
    print(111)
    return THEME


def theme(update, context):
    update.message.reply_text('Напишите ваш отзыв или оставьте комментарий')
    remember(update, context, 'Theme')
    return COMMENT


def skip_theme(update, context):
    context.user_data['THEME'] = None
    return COMMENT


# функция отображения (можно исправить)
def facts_to_str(user_data: Dict[str, str]):
    """"Отображаем введенные данные"""
    facts = list()
    for key, value in user_data.items():
        facts.append(f'{key} - {value}')
    return "\n".join(facts).join(['\n', '\n'])


def comment(update: Update, context: CallbackContext) -> int:
    remember(update, context, 'Comment')
    update.message.reply_text(
        f"Хотите отправить ваш отзыв?"
        f"Ваш отзыв:"
        f"{facts_to_str(context.user_data)}", reply_markup=markup_review,
    )
    return SAVE


def save(update: Update, context: CallbackContext):
    update.message.reply_text(f'Ваш отзыв сохранен.'
                              f' Нажмите  /start')
    print("Запись отзыва для организации в базу данных - " + ' '.join(list((context.user_data).values())))
    uploadReview(context.user_data['Name'],
                 context.user_data['Region'],
                 context.user_data['City'],
                 context.user_data['Theme'],
                 context.user_data['Comment'])

    context.user_data.clear()
    return END


def stop(update: Update, context: CallbackContext):
    update.message.reply_text('Отмена')
    user_data = context.user_data
    user_data.clear()

    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Начнем сначала, {user.mention_markdown_v2()}\.',
        '''reply_markup=ForceReply(selective=True),'''
    )
    update.message.reply_text("Чтобы Вы хотите сделать?",reply_markup=markup_1,)
    return END

def search_review(update: Update, context: CallbackContext) -> int:
    reply_text = "Давайте искать... Выберете, с чего хотите начать свой поиск"
    update.message.reply_text(reply_text, reply_markup=markup_search)

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text.upper()
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = (
            f"Ведите {text}" + '\n'
            f"Ранее вы ввели: {context.user_data[text]}"
        )
    else:
        reply_text = f"Мы ждем, что вы введете {text}"
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    remember(update, context, context.user_data['choice'])
    del context.user_data['choice']

    string = adaptiveSearch(context.user_data.get("НАЗВАНИЕ", ''),
                   context.user_data.get("РЕГИОН", ''),
                   context.user_data.get("ГОРОД", ''),
                   context.user_data.get("ТЕМА", ''),)
    update.message.reply_text(
        f"Ниже приведен отсортированный список всех НКО по указанным параметрам:"
        f"{facts_to_str(context.user_data)}"
        f"" + string,
        reply_markup=markup_search,
    )
    print(context.user_data.get('НАЗВАНИЕ', ''))
    return CHOOSING


# def show_data(update: Update, context: CallbackContext) -> None:
#     update.message.reply_text(
#         f"Show data: {facts_to_str(context.user_data)}"
#     )


def done(update: Update, context: CallbackContext):
    if 'choice' in context.user_data:
        del context.user_data['choice']

    string = adaptiveSearch(context.user_data.get("НАЗВАНИЕ", ''),
                   context.user_data.get("РЕГИОН", ''),
                   context.user_data.get("ГОРОД", ''),
                   context.user_data.get("ТЕМА", ''),)

    update.message.reply_text(
        "Поиск в БД по: " f"{facts_to_str(context.user_data)}" f"" + string,
        reply_markup=ReplyKeyboardRemove(),
    )
    return END


def main():
    # Create the Updater and pass it your bot token.
    updater = Updater(telegram_key_api)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    help_handler_1 = MessageHandler(Filters.regex('Подробнее...'), help)
    # help_handler = MessageHandler(Filters.regex('Подробнее...'), help)

    review_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Оставить отзыв$'), review)],
        states={
            NAME: [MessageHandler(Filters.text, name)],
            REGION: [MessageHandler(Filters.text, region), CommandHandler('skip', skip_region)],
            CITY: [MessageHandler(Filters.text, city), CommandHandler('skip', skip_city)],
            THEME: [MessageHandler(Filters.text, theme), CommandHandler('skip', skip_theme)],
            COMMENT: [MessageHandler(Filters.text, comment)],
            SAVE: [MessageHandler(Filters.regex('^Отправить$'), save),
                   MessageHandler(Filters.regex('^Сбросить$'), stop)],
        },
        fallbacks=[CommandHandler('stop', stop), MessageHandler(Filters.regex('^Подробнее...$'), help)],
    )

    search_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Найти организацию$'), search_review)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Регион|Город|Тема|Название)$'), regular_choice)],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Поиск$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Поиск$')), received_information,
                )
            ],
        },
        fallbacks=[CommandHandler('stop', stop), MessageHandler(Filters.regex('^Сброс$'), stop), MessageHandler(Filters.regex('^Подробнее...$'), help)],
    )
    dispatcher.add_handler(help_handler_1)
    dispatcher.add_handler(review_conv_handler)
    dispatcher.add_handler(search_conv_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
