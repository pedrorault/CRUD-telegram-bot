import os
from telegram import InlineKeyboardButton,InlineKeyboardMarkup, Update
from telegram.ext import  CallbackContext
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
            [_kbbutton("Enviar",f'{table}_enviar'),
            _kbbutton("Anterior",f'{table}_anterior'),
            _kbbutton("Cancelar",f'{table}_cancel') ],  
        ]
    else:
        return [ 
            [_kbbutton("Anterior",f'{table}_anterior'),
            _kbbutton("Próximo",f'{table}_proximo'),
            _kbbutton("Cancelar",f'{table}_cancel') ],  
        ]

def createData(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = context.chat_data
    table = data["table"]

    _,action = query.data.split("_")
    data["operation"] = action if action in ['create','update'] else data["operation"]
    colunas = _colunasFromTable(tablename=table, operation=data["operation"])

    addToArg = +1 if action == "proximo" else -1 if action == "anterior" else 0 
    data["arg"] += addToArg

    colunaAtual = colunas[data["arg"]]  
    if colunaAtual not in data["query"].keys():  
        data["query"][colunaAtual] = ""

    msg = f'Insira a coluna <b>{colunaAtual}</b> da tabela <b>{table}</b>.'
    msg2 = "\nEnvie a mensagem para salvar.\nRe-envie para sobreescrever.\nClique em Enviar para cadastrar os dados."
    msg = msg+msg2 if data["arg"] == 0 else msg

    inlineOp = _opcoesInlineArguments(data["arg"], colunas, table)

    kbLayout = InlineKeyboardMarkup(inlineOp)
    query.edit_message_text(text=msg, parse_mode="HTML")
    query.edit_message_reply_markup(reply_markup=kbLayout)
    return VALUE1

def receiveCreateData(update: Update, context: CallbackContext) -> None:
    data = context.chat_data
    table = data["table"]
    arg = data["arg"]
    op = data["operation"]
    column = _colunasFromTable(table,op)[arg]
    context.chat_data["query"][column] = update.message.text
    return VALUE1

def sendData(update: Update, context: CallbackContext) -> None:
    # print(context.chat_data)
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
    # if result.startswith("Erro"):
        # print("Deu erro viu minha flor")
        #chatData["arg"] = 0
        # table_algo, igual da primeira
         #add button pra voltar pro começo da inserção
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

    data = context.chat_data
    table = data["table"]
    data["operation"] = operation if operation in ['delete'] else data["operation"]

    addToArg = +1 if operation == "proximo" else -1 if operation == "anterior" else 0 
    data["arg"] += addToArg


    if table != "musica":
        msg = f'Digite o <b>nome</b> da tabela <b>{table}</b> que deseja deletar'
        inlineOp = [ [_kbbutton("Enviar",f'{table}_enviar'), _kbbutton("Cancelar",'cancel') ]]
        kb = InlineKeyboardMarkup(inlineOp)
        query.edit_message_text(text=msg,parse_mode="HTML")
        query.edit_message_reply_markup(reply_markup=kb)
    else:
        if data["arg"] == 0:
            msg = f'Digite e envie o <b>nome</b> da música que deseja deletar'
            inlineOp = [ [_kbbutton("Próximo",f'{table}_proximo'), 
                    _kbbutton("Cancelar",'cancel') ]]
            kb = InlineKeyboardMarkup(inlineOp)
            query.edit_message_text(text=msg,parse_mode="HTML")  
            query.edit_message_reply_markup(reply_markup=kb)

        elif data["arg"] == 1:
            msg = f'Digite e envie o <b>nome</b> da <b>banda</b> que deseja deletar a música'
            inlineOp = [ [_kbbutton("Enviar",f'{table}_enviar'), 
                    _kbbutton("Anterior",f'{table}_anterior'),
                    _kbbutton("Cancelar",'cancel') ]]
            kb = InlineKeyboardMarkup(inlineOp)
            query.edit_message_text(text=msg,parse_mode="HTML")
            query.edit_message_reply_markup(reply_markup=kb)

    return DELETE


def receiveDeleteData(update: Update, context: CallbackContext) -> None:
    data = context.chat_data
    if "query" not in data.keys():
        data["query"] = {}
    if data["table"] != "musica":
        data["query"]["nome"] = update.message.text
    else:
        if data["arg"] == 0:
            data["query"]["nome"] = update.message.text
        elif data["arg"] == 1:
            data["query"]["banda"] = update.message.text
    return DELETE

def conexaoDB(operation, tablename, data):
    result = None    
    conn = crudDB.Conexao()
    cur = conn.cur

    if tablename == 'grupomusical':
        try:
            nome = emptyToNone(data["nome"])
            if operation == 'create':
                bio = emptyToNone(data["biografia"]) 
                origem = emptyToNone(data["origem"]) 
                if isAnyEmpty(data):
                    conn.close()
                    return "Erro: Os dados não foram inseridos completamente!"
                result = crudDB.GrupoMusical(cur).createGrupoMusical(
                    nome,bio,origem )
            elif operation == 'update':
                where = data[msgUpdate]
                bio = emptyToNone(data["biografia"]) 
                origem = emptyToNone(data["origem"]) 
                if where.strip() == '':
                    conn.close()
                    return "Erro: Não foi submetida o nome da entrada que deseja alterar" 
                result = crudDB.GrupoMusical(cur).updateGrupoMusical(where,nome,bio,origem)
                pass
            elif operation == 'delete':
                if isAnyEmpty(data):
                    conn.close()
                    return "Erro: Não foi inserido o nome do grupo que será deletado!"
                result = crudDB.GrupoMusical(cur).deleteGrupoMusical(nome) 
            elif operation == 'read':
                pass
        except :
            return "Erro: Os dados não foram inseridos corretamente!"
    elif tablename == 'musica':
        nome = emptyToNone(data["nome"])

        if operation == 'create':
            ano = emptyToNone(data["ano"])
            duracao = emptyToNone(data["duracaosegundos"])
            plays = emptyToNone(data["plays"])
            genero = emptyToNone(data["genero"])
            nomeBanda = emptyToNone(data["nome da banda"])
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
            ano = emptyToNone(data["ano"])
            duracao = emptyToNone(data["duracaosegundos"])
            plays = emptyToNone(data["plays"])
            genero = emptyToNone(data["genero"])
            nomeBanda = emptyToNone(data["nome da banda"])  
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
            #TODO: Pedir também o nome da banda            
            if isAnyEmpty(data):
                conn.close()
                return "Erro: Não foi inserido o nome da música que será deletada!"
            banda = emptyToNone(data["banda"])
            result = crudDB.Musica(cur).deleteMusica(nome,banda) 
        elif operation == 'read':
            pass            

        
    elif tablename == 'playlist':
        try:
            nome = emptyToNone(data["nome"])
            if operation == 'create':
                descricao = emptyToNone(data["descricao"])
                horainicio = emptyToNone(data["horainicio"])
                if isAnyEmpty(data):
                    conn.close()
                    return "Erro: Os dados não foram inseridos completamente!" 
                if (horainicio and re.match(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$",horainicio)):              
                    result = crudDB.Playlist(cur).createPlaylist(
                        nome,descricao,horainicio )
                else:
                    return "Erro: A hora deve ter formato como 00:00 ou 23:59"  
            elif operation == 'update':
                where = data[msgUpdate]
                descricao = emptyToNone(data["descricao"])
                horainicio = emptyToNone(data["horainicio"])

                if where.strip() == '':
                    conn.close()
                    return "Erro: Não foi submetida o nome da entrada que deseja alterar" 
                if (horainicio and re.match(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$",horainicio)) or not horainicio:                
                    result = crudDB.Playlist(cur).updatePlaylist(where,nome,descricao,horainicio) 
                else:
                    conn.close()
                    return "Erro: A hora deve ter formato como 00:00 ou 23:59"    
            elif operation == 'delete':
                if isAnyEmpty(data):
                    conn.close()
                    return "Erro: Não foi inserido o nome da playlist que será deletada!"
                result = crudDB.Playlist(cur).deletePlaylist(nome)
            elif operation == 'read':
                pass
        except Exception:
            result = "Erro: Os dados não foram inseridos corretamente!"

    conn.close()
    return result