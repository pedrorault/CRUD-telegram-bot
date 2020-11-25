from telegram import InlineKeyboardButton,InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram.ext.commandhandler import CommandHandler
import os
from dotenv import load_dotenv

if not os.getenv('PWBDTELEGRAM'):
    load_dotenv()

#STATES
AUTH, FIRST, SECOND, THIRD = range(4)

#callback_data
#Direto nas coisas

def _kbbutton(name,cb):
    return InlineKeyboardButton(name,callback_data=cb)

def start(update: Update, context: CallbackContext) -> None: 
    msg = "Favor entrar com a senha para fazer alterações no bd"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    return AUTH

def pwdWrong(update: Update, context: CallbackContext) -> None:
    msg = "Digistate a senha errada para o password, tente novamente"
    context.bot.send_message(chat_id=update.effective_chat.id,text=msg)
    return AUTH

def tablesInline(update: Update, context: CallbackContext) -> None:
    inlineOp = [ 
        [_kbbutton("Música",'musica'),_kbbutton("Playlist",'playlist'),_kbbutton("Grupo Musical",'grupomusical') ]
    ]
    kbLayout = InlineKeyboardMarkup(inlineOp)
    msg = "Escolha uma das tabelas para fazer alterações no banco de dados."
    try:
        qr = update.callback_query
        qr.answer()

        qr.edit_message_text(text=msg)
        qr.edit_message_reply_markup(kbLayout)
    except AttributeError:
         context.bot.send_message(chat_id=update.effective_chat.id, 
                    text=msg, 
                    reply_markup=kbLayout,
                    parse_mode="HTML") 
    return FIRST

def crudInline(update: Update, context: CallbackContext) -> None:    
    query = update.callback_query
    query.answer()

    if "_" in query.data:
        table = query.data.split("_")[0]
    else:
        table = query.data

    msg = f'Escolha uma das opções para fazer alterações na <b>Tabela {table}</b> do banco de dados.'

    inlineOp = [ 
        [_kbbutton("Create",f'{table}_create'),_kbbutton("Read",f'{table}_read') ],
        [_kbbutton("Update",f'{table}_update'),_kbbutton("Delete",f'{table}_delete')],
        [_kbbutton("Voltar",'voltar')]
    ]
    kbLayout = InlineKeyboardMarkup(inlineOp)

    query.edit_message_text(text=msg, parse_mode="HTML")
    query.edit_message_reply_markup(kbLayout)
    return SECOND

def modifyData(update: Update, context: CallbackContext) -> None:    
    query = update.callback_query
    query.answer()
    table, operation = query.data.split("_")
    query.edit_message_text(text=f'Aqui teremos instruções de como fazer a operação <b>{operation}</b> na tabela <b>{table}</b>',parse_mode="HTML")

    inlineOp = [[_kbbutton("Voltar",f'{table}_voltar')]]
    kbLayout = InlineKeyboardMarkup(inlineOp)
    query.edit_message_reply_markup(reply_markup=kbLayout)

    return THIRD


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start',start)],
    states={
        AUTH: [
            MessageHandler((Filters.regex(f'^{os.getenv("PWBDTELEGRAM")}$')),tablesInline),
            MessageHandler((~ Filters.text | ~ Filters.regex(f'^{os.getenv("PWBDTELEGRAM")}$')),pwdWrong),

        ],
        FIRST: [
            CallbackQueryHandler(crudInline, pattern=f'^musica$'),
            CallbackQueryHandler(crudInline, pattern=f'^playlist$'),
            CallbackQueryHandler(crudInline, pattern=f'^grupomusical$'),
        ],
        SECOND: [
            CallbackQueryHandler(modifyData, pattern=f'^(.*)_(create|read|update|delete)$'),         
            CallbackQueryHandler(tablesInline, pattern=f'^voltar$'),

        ],
        THIRD: [
            CallbackQueryHandler(crudInline, pattern=f'^(.*)_voltar$'),
        ]
    },
    
    fallbacks=[CommandHandler('start',start)]
)

