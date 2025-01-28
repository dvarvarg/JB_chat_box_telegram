from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

# тут будем писать наш код:)

async def start(update,context):
    dialog.mode='main'
    text=load_message('main')
    await send_photo(update,context,'main')
    await send_text(update,context, text)

    # ассинхр ф-ция
    await show_main_menu(update,context,{
        'start':'главное меню бота',
        'profile': 'генерация Tinder-профиля 😎',
        'opener': 'сообщение для знакомства 🥰',
        'message': 'переписка от вашего имени 😈',
        'date': 'переписка со звездами 🔥',
        'gpt': 'задать вопрос чату GPT 🧠'
    })


async def gpt(update,context):
    dialog.mode='gpt'
    text=load_message('gpt')
    await send_photo(update,context,'gpt')
    await send_text(update,context, text)


async def gpt_dialog(update,context):
    text=update.message.text #человек в чат написал сообщение
    prompt=load_prompt('gpt')
    # мы пересылаем это чату GPT, ждем ответ с помощью await
    answer=await chatgpt.send_question(prompt,text)
    # ответ берем и присылаем человеку как ответ чата gpt
    await send_text(update,context, answer)


# переводим диалог в режим дейтинга
async def date(update,context):
    dialog.mode='date'
    # читаем заготовленный текст и отображаем картинку и список кнопок
    # при клике на кнопку вкл обработчик date_button
    text=load_message('date')
    await send_photo(update,context,'date')
    await send_text_buttons(update,context, text, {
        'date_grande':'Ариана Гранде',
        'date_robbie': 'Марго Робби',
        'date_zendaya': 'Зендея',
        'date_gosling': 'Райан Гослинг',
        'date_hardy': 'Том Харди',
    })


async def date_dialog(update, context):
    text=update.message.text
    my_message=await send_text(update,context,'Девушка/парень набирает текст...')
    answer =await chatgpt.add_message(text)
    await my_message.edit_text(answer)
    # await send_text(update,context, answer)


async def date_button(update,context):
    query=update.callback_query.data
    await update.callback_query.answer()

    # передаем подготовленную картинку с таким же именем и текст
    await send_photo(update,context,query)
    await send_text(update,context,'Отличный выбор! Пригласите девушку (парня) на свидание за 5 сообщений. ')

    #загружаем prompt и передаем его чату gpt
    prompt=load_prompt(query)
    chatgpt.set_prompt(prompt)


async def message(update,context):
    dialog.mode='message'
    text = load_message('message')
    await send_photo(update, context, 'message')
    await send_text_buttons(update, context, text, {
        'message_next':'Следующее сообщение ',
        'message_date':'Пригласить на свидание '

    })
    dialog.list.clear()


async def message_dialog(update,context):
    query=update.callback_query.data
    await update.callback_query.answer()

    prompt=load_prompt(query)
    user_chat_history='\n\n'.join(dialog.list)
    my_message=await send_text(update,context,'ChatGPT думает над вариантами ответа ...')
    answer=await chatgpt.send_question(prompt,user_chat_history)
    await my_message.edit_text(answer)


async def message_button(update,context):
    text=update.message.text
    dialog.list.append(text)


async def hello(update,context):
    if dialog.mode=='gpt':
        await gpt_dialog(update,context)
    if dialog.mode == 'date':
        await date_dialog(update, context)
    if dialog.mode == 'message':
        await message_dialog(update, context)
    else:
        await send_text(update,context, '*Привет*')
        await send_text(update,context, '_Как дела?_')
        await send_text(update,context, 'Вы написали '+update.message.text)

        await send_photo(update,context,'avatar_main')
        await send_text_buttons(update,context,'Запустить процесс?',{
            'start':'Запустить',
            'stop':'Остановить'
        })


async def hello_button(update,context):
    query=update.callback_query.data
    if query=='start':
        await send_text(update, context, 'Процесс запущен')
    else:
        await send_text(update, context, 'Процесс остановлен')


dialog=Dialog()
dialog.mode=None
dialog.list=[]

chatgpt=ChatGptService(token='gpt:IMAtcJ134WVIxVeFe7I2JFkblB3TH88zgyZ5JYpVQKKxZnKk')

app = ApplicationBuilder().token("7830540338:AAEB2Ed9CKCKgrr1tDA4wXsMiERXrCHg1o8").build()
# обработчики команд
app.add_handler(CommandHandler('start',start))
app.add_handler(CommandHandler('gpt',gpt))
app.add_handler(CommandHandler('date',date))
app.add_handler(CommandHandler('message',message))

# обработчик текстов, что человек пишет в чат
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,hello))

# обработчики кнопок
app.add_handler(CallbackQueryHandler(date_button, pattern='^date_.*'))
app.add_handler(CallbackQueryHandler(message_button, pattern='^message_.*'))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
