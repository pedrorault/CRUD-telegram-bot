import os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup, Update
from telegram import replymarkup
from telegram.ext import  CallbackContext, ConversationHandler
from dotenv import load_dotenv
import logging
import crudDB
import re

if not os.getenv('PWBDTELEGRAM'):
    load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#STATES
VALUE1 = 4
SUBMIT= 5
DELETE = 6
msgUpdate = "nome que está buscando para modificar"


def _kbbutton(name,cb):
    return InlineKeyboardButton(name,callback_data=cb)

def _colunasFromTable(tablename, operation=None):
    colunas = None
    if tablename == 'musica':
        colunas = ['nome','ano','duracaosegundos','plays','genero','nome da banda']
    elif tablename == 'playlist':
        colunas = ['nome','descricao','horainicio']
    elif tablename == 'grupomusical':
        colunas = ['nome','biografia','origem']
    if operation == "update":
        colunas.append(msgUpdate)
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
    operation = None

    if action == "update":
        operation = action
    elif "operation" in data.keys() and data["operation"] == "update":
        operation = data["operation"]

    colunas = _colunasFromTable(tablename=table, operation=operation)

    if "arg" not in data.keys():
        argSql = colunas[0]
        data["arg"] = 0
        data["table"] = table
        data["query"] = {}
        data["operation"] = action
    else:
        print(colunas, data["arg"])
        if action == "proximo":
            data["arg"] += 1
            argSql = colunas[data["arg"]]            
        elif action == "anterior":
            data["arg"] -= 1
            argSql = colunas[data["arg"]]     
    data["query"][argSql] = ""

    msg = f'Insira a coluna <b>{argSql}</b> da tabela <b>{table}</b>.\nEnvie a mensagem para salvar.\nRe-envie para sobreescrever.\nClique em Enviar para cadastrar os dados.'
    inlineOp = _opcoesInlineArguments(data["arg"], colunas, table)

    kbLayout = InlineKeyboardMarkup(inlineOp)
    query.edit_message_text(text=msg, parse_mode="HTML")
    query.edit_message_reply_markup(reply_markup=kbLayout)
    return VALUE1

def receiveCreateData(update: Update, context: CallbackContext) -> None:
    #TODO: talvez mudar essa merda pra poder ter return values diferentes
    data = context.chat_data
    table = data["table"]
    arg = data["arg"]
    op = data["operation"]
    column = _colunasFromTable(table,op)[arg]
    context.chat_data["query"][column] = update.message.text
    return VALUE1

def sendData(update: Update, context: CallbackContext) -> None:
    print(context.chat_data)
    query = update.callback_query
    query.answer()
    chatData = context.chat_data
    queryData = chatData["query"]
    op = chatData["operation"]
    table = chatData["table"]

    msg = "Entrada inserida:\n"
    for key,value in chatData["query"].items():
        msg += f'<b>{key}:</b> {value}\n'
    
    result = conexaoDB(op,table,queryData)    
    query.edit_message_text(text=msg,parse_mode="HTML")

    inlineOp= [ [_kbbutton("Voltar",f'{chatData["table"]}_voltar')] ]
    if result.startswith("Erro"):
        print("Deu erro viu minha flor")
        #chatData["arg"] = 0
        # table_algo, igual da primeira
        pass #add button pra voltar pro começo da inserção
    kb = InlineKeyboardMarkup(inlineOp)
    context.bot.send_message(chat_id=update.effective_chat.id,text=result,reply_markup=kb)

    return SUBMIT

def isAnyEmpty(dicionarioData):
    for x in dicionarioData.values():
        if not x or x.strip() == '':
            return True
    return False

def emptyToNone(data):
    if data.strip() == '':
        return None
    else:
        return data

def deleteData(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    table, operation = query.data.split("_")

    if table != "musica":
        msg = f'Digite o nome da tabela {table} que deseja deletar'
        inlineOp = [ [_kbbutton("Enviar",f'{table}_enviar'), _kbbutton("Cancelar",'cancel') ]]
        kb = InlineKeyboardMarkup(inlineOp)
        query.edit_message_text(text=msg,reply_markup=kb)
    return DELETE

def receiveDeleteData(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.chat_data["query"] = {}
    context.chat_data["query"]["nome"] = update.message.text
    return DELETE
    #TODO: tratar esse caso na função crud e ver o handler

def conexaoDB(operation, tablename, data):
    result = None    
    conn = crudDB.Conexao()
    cur = conn.cur
    if tablename == 'grupomusical':
        try:
            nome = emptyToNone(data["nome"]) 
            bio = emptyToNone(data["biografia"]) 
            origem = emptyToNone(data["origem"]) 

            if operation == 'create':
                if isAnyEmpty(data):
                    conn.close()
                    return "Erro: Os dados não foram inseridos completamente!"
                result = crudDB.GrupoMusical(cur).createGrupoMusical(
                    nome,bio,origem )
            elif operation == 'update':
                where = data[msgUpdate]
                if where.strip() == '':
                    conn.close()
                    return "Erro: Não foi submetida o nome da entrada que deseja alterar" 
                result = crudDB.GrupoMusical(cur).updateGrupoMusical(where,nome,bio,origem)
                pass
            elif operation == 'delete':
                pass
            elif operation == 'read':
                pass
        except:
            return "Erro: Os dados não foram inseridos corretamente!"
    elif tablename == 'musica':
        nome = emptyToNone(data["nome"])
        ano = emptyToNone(data["ano"])
        duracao = emptyToNone(data["duracaosegundos"])
        plays = emptyToNone(data["plays"])
        genero = emptyToNone(data["genero"])
        nomeBanda = emptyToNone(data["nome da banda"])

        if operation == 'create':
            if isAnyEmpty(data):
                conn.close()
                return "Erro: Os dados não foram inseridos completamente!"
            try:
                ano = int(ano)
                duracao = int(duracao)
                plays = int(plays)
            except Exception:
                return "Erro: Os dados numérios não foram inseridos adequadamente"
            result = crudDB.Musica(cur).createMusica(
                nome,ano,duracao,plays,genero,nomeBanda
            )
        elif operation == 'update':
            where = data[msgUpdate]     
            if where.strip() == '' or not nomeBanda:
                conn.close()
                return "Erro: Não foi submetida o nome da música ou o nome da banda que deseja alterar" 
            try:
                ano = int(ano) if ano else ano
                duracao = int(duracao) if duracao else duracao
                plays = int(plays) if plays else plays
            except Exception:
                return "Erro: Os dados numéricos não foram inseridos adequadamente"
            result = crudDB.Musica(cur).updateMusica(where,nome,ano,duracao,plays,genero,nomeBanda)
        elif operation == 'delete':
            pass
        elif operation == 'read':
            pass            

        
    elif tablename == 'playlist':
        try:
            nome = emptyToNone(data["nome"])
            descricao = emptyToNone(data["descricao"])
            horainicio = emptyToNone(data["horainicio"])

            if operation == 'create':
                if isAnyEmpty(data):
                    conn.close()
                    return "Erro: Os dados não foram inseridos completamente!" 
                if (horainicio and re.match(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$",horainicio)) or not horainicio:              
                    result = crudDB.Playlist(cur).createPlaylist(
                        nome,descricao,horainicio )
            elif operation == 'update':
                where = data[msgUpdate]
                if where.strip() == '':
                    conn.close()
                    return "Erro: Não foi submetida o nome da entrada que deseja alterar" 
                print("Hora inicio ", horainicio)
                if (horainicio and re.match(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$",horainicio)) or not horainicio:                
                    result = crudDB.Playlist(cur).updatePlaylist(where,nome,descricao,horainicio) 
                else:
                    conn.close()
                    return "Erro: A hora deve ter formato como 00:00 ou 23:59"           
                
            elif operation == 'delete':
                pass
            elif operation == 'read':
                pass
        except Exception:
            result = "Erro: Os dados não foram inseridos corretamente!"

    conn.close()
    return result