
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from chatterbot import ChatBot
from gtts import gTTS
import yaml
import requests


from chatterbot.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot(
    'telegram',
    storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',

        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'halo123',
            'output_text': 'Ok, here is a link: http://chatterbot.rtfd.org'
        }
    ],
    database_uri='mongodb://localhost:27017/your-mongodb-database',
    read_only=True
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def speak(text,chat_id):
    tts = gTTS(text=text,lang="id")
    filename = "voice"+str(chat_id)+".mp3"
    tts.save("/var/www/html"+filename)
    return filename

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def echo(update, context):
    """Echo the user message."""
    response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key=be4808a7b6d2d8684012bc817583647d")
    cuaca = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?appid=5bcb6eb2e0d7d2b3c2c2c2eccbd4f270&q=Jakarta")

    userText = update.message.text

    if userText.find("Saran film") != -1:
        s = ''
        data = "Aku Kemarin Nonton Filem '",response.json()['results'][0]['title'],"' Menurut Aku itu bagus"
        update.message.reply_text(s.join(data))

    elif userText.find("Top film") != -1:
        s = ''
        data = "TOP 10 Film BY TMDB \n \n",response.json()['results'][0]['title'],'.\n',response.json()['results'][1]['title'],'.\n',response.json()['results'][2]['title'],'.\n',response.json()['results'][3]['title'],'.\n',response.json()['results'][4]['title'],'.\n',response.json()['results'][5]['title'],'.\n',response.json()['results'][6]['title'],'.\n',response.json()['results'][7]['title'],'.\n',response.json()['results'][8]['title'],'.\n',response.json()['results'][9]['title'],'.\n',response.json()['results'][10]['title'],'.\n'

        update.message.reply_text(s.join(data))

    elif userText.find("Cari film") != -1:

        text = userText.split(' ', 2)
        api_filem = requests.get("https://api.themoviedb.org/3/search/movie?api_key=be4808a7b6d2d8684012bc817583647d&language=en-US&query="+text[2]+"&page=1")
        if api_filem.json()['results'][0] is None:
            update.message.reply_text('Saya tidak menemukan filem '+text[2])

        update.message.reply_text('Aku menumukan Filem ini')
        update.message.reply_text(api_filem.json()['results'][0]['title'])
        update.message.reply_photo('https://image.tmdb.org/t/p/w500'+api_filem.json()['results'][0]['poster_path'])
        update.message.reply_text(api_filem.json()['results'][0]['overview'])

    elif userText.find("Nyanyi dong") != -1:
        update.message.reply_audio('https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_700KB.mp3')

    elif userText.find("Bacain") != -1:
        chat_id = update.message.chat_id
        text = userText.split(' ', 1)

        update.message.reply_html('<a href='++'>HALO </a>')



    elif userText.find("Perediksi cuaca") != -1:
        yandex = requests.get(
            "https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20181205T160438Z.d9c1f2f3127956af.d38a8770c4ab879be96b8b480d22b85cd5be1ba5&text="+cuaca.json()['weather'][0]['main']+"&lang=en-id")
        s = ''
        data = 'Menurut data yang saya ambil dari Open Weather Cuaca saat ini adalah ',yandex.json()['text'][0]
        update.message.reply_text(s.join(data))

    elif userText.find("Translate") != -1:
        text = userText.split(' ',1)
        s = ' '
        print(text)
        yandex = requests.get(
            "https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20181205T160438Z.d9c1f2f3127956af.d38a8770c4ab879be96b8b480d22b85cd5be1ba5&text=" +
            text[1] + "&lang=id-en")
        s = ''

        update.message.reply_text(yandex.json()['text'][0])
    elif userText.find("Translate") != -1:
        text = userText.split(' ',1)
        s = ' '
        print(text)
        yandex = requests.get(
            "https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20181205T160438Z.d9c1f2f3127956af.d38a8770c4ab879be96b8b480d22b85cd5be1ba5&text=" +
            text[1] + "&lang=id-en")
        s = ''

        update.message.reply_text(yandex.json()['text'][0])

    elif userText.find("Timer") != -1:
        chat_id = update.message.chat_id
        text = userText.split(' ', 1)
        due = int(text[1])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Aku akan chat kamu '+ text[1] +' detik lagi')


    else:


        update.message.reply_text(str(chatbot.get_response(userText)))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def belajar(update, context):
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train(
        "chatterbot.corpus.indonesia.conversations",
        'chatterbot.corpus.indonesia.greetings',
        'chatterbot.corpus.indonesia.trivia',
        'chatterbot.corpus.indonesia.verra',
    )
    update.message.reply_text("Aku Sudah belajar hal baru :)")

def ajarin(update, context):


    s = ' '
    data = context.args
    data = s.join(data)
    pertanyaan = data.split(' // ',1);
    jawaban = str(pertanyaan[1])
    pertanyaan = str(pertanyaan[0])



    with open(r'/home/ubuntu/.local/lib/python3.6/site-packages/chatterbot_corpus/data/indonesia/verra.yml') as file:
        fruits_list = yaml.load(file, Loader=yaml.FullLoader)
        new_array = [pertanyaan,jawaban]
        fruits_list['conversations'].append(new_array)
        print(fruits_list)

    with open(r'/home/ubuntu/.local/lib/python3.6/site-packages/chatterbot_corpus/data/indonesia/verra.yml', 'w') as file:
        documents = yaml.dump(fruits_list, file)

    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train(
        "chatterbot.corpus.indonesia.conversations",
        'chatterbot.corpus.indonesia.greetings',
        'chatterbot.corpus.indonesia.trivia',
        'chatterbot.corpus.indonesia.verra',
    )

    update.message.reply_text(pertanyaan +" "+ jawaban)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1037911184:AAHmtCHtpcEKo5fKkI4_07KZhTCTzbsKEig", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("belajar", belajar))
    dp.add_handler(CommandHandler("ajarin", ajarin))

    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()