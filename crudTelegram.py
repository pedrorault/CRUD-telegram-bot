import os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup, Update
from telegram.ext import  CallbackContext, ConversationHandler
from dotenv import load_dotenv
import logging


if not os.getenv('PWBDTELEGRAM'):
    load_dotenv()

# TODO: Em cada operação, colocar um botão Anterior, Seguinte, Cancelar
# Insira o {NOME} da {Música} e envie para salvar. Re-envie para sobreescrever.
# Seguinte -> Insira o {X} da {Y} e envie para salvar. Re-envie para sobreescrever.
# A cada etapa, salva essas coisas em um dicionário, que é:
#   Enviado pro crud: Quando clicar em [Enviar]
#   Deletado: Quando clicar em [Cancelar] (e volta pra tela de comandos disponiveis pra tabela)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#STATES
VALUE1 = 4

def _kbbutton(name,cb):
    return InlineKeyboardButton(name,callback_data=cb)

def _colunasFromTable(tablename):
    colunas = None
    if tablename == 'musica':
        colunas = ['nome','ano','duracaosegundos','plays','genero','nome da banda']
    elif tablename == 'playlist':
        colunas = ['nome','descricao','horainicio']
    elif tablename == 'grupomusical':
        colunas = ['nome','biografia','origem']
    return colunas

def _opcoesInlineArguments(arg,colunas,table):
    if arg == 0:
        return [ 
            [_kbbutton("Próximo",f'{table}_proximo'),_kbbutton("Cancelar",f'{table}_cancel') ],  
        ]
    elif arg == len(colunas)-1:
        return [ 
            [_kbbutton("Enviar",f'{table}_{colunas[arg]}_enviar'),
            _kbbutton("Anterior",f'{table}_{colunas[arg]}_anterior'),
            _kbbutton("Cancelar",f'{table}_cancel') ],  
        ]
    else:
        return [ 
            [_kbbutton("Anterior",f'{table}_{colunas[arg]}_anterior'),
            _kbbutton("Próximo",f'{table}_{colunas[arg]}_proximo'),
            _kbbutton("Cancelar",f'{table}_cancel') ],  
        ]

def createData(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data.count("_") == 2:
        table, arg, action = query.data.split("_")
    else:
        table, action = query.data.split("_")

    data = context.chat_data
    argSql = None
    colunas = _colunasFromTable(tablename=table)

    if "arg" not in data.keys():
        argSql = colunas[0]
        data["arg"] = 0
        data["table"] = table
        data["query"] = {}
    else:
        if action == "proximo":
            data["arg"] += 1
            argSql = colunas[data["arg"]]            
        elif action == "anterior":
            data["arg"] -= 1
            argSql = colunas[data["arg"]]        
        elif action == "enviar":
            return ConversationHandler.END # TODO: algo
    data["query"][argSql] = ""

    msg = f'Insira a coluna <b>{argSql}</b> da tabela <b>{table}</b>.\nEnvie a mensagem para salvar.\nRe-envie para sobreescrever.\nClique em Enviar para cadastrar os dados.'
    inlineOp = _opcoesInlineArguments(data["arg"], colunas, table)

    kbLayout = InlineKeyboardMarkup(inlineOp)
    query.edit_message_text(text=msg, parse_mode="HTML")
    query.edit_message_reply_markup(reply_markup=kbLayout)
    return VALUE1

def receiveData(update: Update, context: CallbackContext) -> None:
    #TODO: talvez mudar essa merda pra poder ter return values diferentes
    data = context.chat_data
    table = data["table"]
    arg = data["arg"]
    column = _colunasFromTable(table)[arg]
    context.chat_data["query"][column] = update.message.text
    return VALUE1

def sendData(update: Update, context: CallbackContext) -> None:
    print(context.chat_data)
    query = update.callback_query
    query.answer()
    msg = "Enviando dados!"
    query.edit_message_text(text=msg)
    return ConversationHandler.END
