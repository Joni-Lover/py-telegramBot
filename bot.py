from telegram.ext import *
import logging, json
import config
import apiai

__author__ = 'Joni-Lover'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARNING)

logger = logging.getLogger(__name__)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def hello(bot, update):
    logger.info(*update.message.parse_entities())

    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


def echo(bot, update):
    mention_usernames = list(update.message.parse_entities().values())
    if '@' + bot.username in mention_usernames:
        request = apiai.ApiAI(config.dialogflow_client_api_token).text_request()  # Токен API к Dialogflow
        request.lang = 'ru' # На каком языке будет послан запрос
        request.session_id = 'JoniLoverAIBot' # ID Сессии диалога (нужно, чтобы потом учить бота)
        request.query = update.message.text # Посылаем запрос к ИИ с сообщением от юзера
        response_json = json.loads(request.getresponse().read().decode('utf-8'))
        response = response_json['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
        # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
        if response:
            # update.message.reply_text(response)
            bot.send_message(chat_id=update.message.chat_id,
                             text='@{} {}'.format(update.message.from_user.username, response))
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='@{} я Вас не совсем понял!'.format(update.message.from_user.username))


def like_message(bot, update):
    try:
        if update.message.reply_to_message:
            bot.send_sticker(update.message.chat.id, 'CAADAgADygAD8MPADl-iKLoH8iHPAg',
                                update.message.reply_to_message.message_id)
    except Exception as e:
        logger.error(e)
        logger.error(update.message)


def happy_ny_messages(bot, update):
    try:
        bot.send_sticker(update.message.chat.id, 'CAADAgADkiEAAp7OCwABDZOqMVEg34oC')
    except Exception as e:
        logger.error(e)
        logger.error(update.message)


if __name__ == '__main__':

    updater = Updater(config.token)

    dp = updater.dispatcher
    handlers = {
        CommandHandler('hello', hello),
        CommandHandler('like', like_message),
        MessageHandler(Filters.text, echo),
        RegexHandler('^.*(ny|happy new year|с новым годом|новый год|нг|НГ).*$', happy_ny_messages),
        CommandHandler(["ny", "happy new year", "с новым годом", "новый год", 'нг', 'НГ'], happy_ny_messages)
    }
    for handler in handlers:
        dp.add_handler(handler)

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling(clean=True, poll_interval=5)
    updater.idle()
