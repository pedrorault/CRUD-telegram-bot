from telegram import InlineKeyboardButton,InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram.ext.commandhandler import CommandHandler
import os
from dotenv import load_dotenv
from crudTelegram import *

if not os.getenv('PWBDTELEGRAM'):
    load_dotenv()

#STATES
AUTH, FIRST, SECOND, THIRD, CREATE = range(5)

#callback_data
#Direto nas coisas

def _kbbutton(name,cb):
    return InlineKeyboardButton(name,callback_data=cb)

def start(update: Update, context: CallbackContext) -> None: 
    msg = "Favor entrar com a senha para fazer alterações no bd"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)    
    return AUTH

def pwdWrong(update: Update, context: CallbackContext) -> None:
    msg = "Digitaste a senha errada para o password, tente novamente"
    context.bot.send_message(chat_id=update.effective_chat.id,text=msg)
    return AUTH

def tablesInline(update: Update, context: CallbackContext) -> None:
    inlineOp = [ 
            [_kbbutton("Música",'musica'),
            _kbbutton("Playlist",'playlist'),
            _kbbutton("Grupo Musical",'grupomusical')]
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

    context.chat_data.clear() #Reset o dicionario 
    table = query.data.split("_")[0] if "_" in query.data else query.data
    context.chat_data["table"] = table
    context.chat_data["arg"] = 0
    context.chat_data["query"] = {}

    msg = f'Escolha uma das opções para fazer alterações na <b>Tabela {table}</b> do banco de dados.'

    inlineOp = [ 
        [_kbbutton("Criar",f'{table}_create'),_kbbutton("Buscar",f'{table}_read') ],
        [_kbbutton("Atualizar",f'{table}_update'),_kbbutton("Deletar",f'{table}_delete')],
        [_kbbutton("Voltar",'voltar')]
    ]
    kbLayout = InlineKeyboardMarkup(inlineOp)
    query.edit_message_text(text=msg, parse_mode="HTML")
    query.edit_message_reply_markup(kbLayout)

    return SECOND

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
            CallbackQueryHandler(createData, pattern=f'^(.*)_(create|update)$'),  
            CallbackQueryHandler(tablesInline, pattern=f'^voltar$'),  
            CallbackQueryHandler(deleteData, pattern=f'^(.*)_delete$'), 
            CallbackQueryHandler(whichSelectData, pattern=f'^(.*)_read$'),   
              
        ],
        CREATE: [
            MessageHandler(Filters.regex(".+"),receiveCreateData),
            CallbackQueryHandler(crudInline, pattern=f'^(.*)_cancel$'),
            CallbackQueryHandler(createData, pattern=f'^(.*)_proximo$'),
            CallbackQueryHandler(createData, pattern=f'^(.*)_anterior$'),
            CallbackQueryHandler(sendData, pattern=f'^(.*)_enviar$'),
        ],
        THIRD: [
            CallbackQueryHandler(crudInline, pattern=f'^(.*)_voltar$'),
        ],
        SUBMIT: [
            CallbackQueryHandler(crudInline, pattern=f'^(.*)_voltar$'),
            # CallbackQueryHandler(crudInline, pattern=f'^(.*)_cancel$'), TODO: Sair, _sair
        ],
        DELETE:[
            CallbackQueryHandler(crudInline, pattern=f'^(.*)cancel$'),
            CallbackQueryHandler(sendData, pattern=f'^(.*)_enviar$'),
            CallbackQueryHandler(deleteData, pattern=f'^(.*)_proximo$'),
            CallbackQueryHandler(deleteData, pattern=f'^(.*)_anterior$'),
            MessageHandler(Filters.regex(".+"),receiveDeleteData)            
        ],
        SELECT: [
            CallbackQueryHandler(crudInline, pattern=f'^(.*)_cancel$'),
            CallbackQueryHandler(sendData, pattern=f'^(.*)_enviar$'),
            CallbackQueryHandler(selectData, pattern=f'^(.*)_prox$'),
            CallbackQueryHandler(whichSelectData, pattern=f'^(.*)_voltar$'),
            MessageHandler(Filters.regex(".+"),receiveSelectData),
            CallbackQueryHandler(sendData, pattern=f'^(.*)_completa$'),

        ]
    },
    
    fallbacks=[CommandHandler('start',start)]
)

