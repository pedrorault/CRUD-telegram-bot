import psycopg2
import os
from dotenv import load_dotenv
if not os.getenv('MYPORT'):
    load_dotenv()

class GrupoMusical():
    def __init__(self, cur):
        self.cur = cur

    def createGrupoMusical(self, name, biography, origin):
        commandString = "INSERT INTO grupomusical(nome,biografia,origem) VALUES (%s, %s, %s);"
        try:
            print(commandString, (name, biography, origin))
            self.cur.execute(commandString, (name, biography, origin))
            return("Grupo Musical cadastrado com sucesso!")
        except:
            return("Erro: Erro ao cadastrar grupo musical")

    def readGrupoMusical(self, name):
        commandString = "SELECT * FROM grupomusical WHERE nome = %s LIMIT 1;"
        try:
            self.cur.execute(commandString, (name, ))
            query = self.cur.fetchall()
            # print("ID Grupo Musical: ", query[0][0])
            # print("Nome: ", query[0][1])
            # print("Biography: ", query[0][2])
            # print("Origem: ", query[0][3])
            return(query)
        except:
            return("Erro: Grupo musical não encontrado")

    def readGrupoMusicalOrigem(self, origin):
        commandString = "SELECT * FROM grupomusical WHERE origem = %s;"
        try:
            self.cur.execute(commandString, (origin, ))
            query = self.cur.fetchall()
            return(query)
        except:
            return("Erro: Grupo musical não encontrado")

    def updateGrupoMusical(self, where, newName, biography, origin):
        # commandString = "UPDATE grupomusical SET nome = %s, biografia = %s, origem = %s WHERE nome = %s;"
        commandString = """UPDATE grupomusical SET
            nome = COALESCE(%(nome)s, nome),
            biografia = COALESCE(%(biografia)s, biografia),
            origem = COALESCE(%(origem)s,origem)            
            WHERE nome = %(where)s
            AND  (%(nome)s IS NOT NULL AND %(nome)s IS DISTINCT FROM nome OR
                %(biografia)s IS NOT NULL AND %(biografia)s IS DISTINCT FROM biografia OR
                %(origem)s IS NOT NULL AND %(origem)s IS DISTINCT FROM origem
            );
        """
        
        try:
            # self.cur.execute(commandString, (newName, biography, origin, where))
            self.cur.execute(commandString, {'nome':newName, 'biografia':biography, 'origem':origin, 'where':where})
            return("Grupo Musical atualizado com sucesso")
        except Exception as e:
            print(e)
            return("Erro: Grupo Musical não encontrado")

    def deleteGrupoMusical(self, name):
        commandString = "DELETE FROM grupomusical WHERE nome = %s;"
        try:
            self.cur.execute(commandString, (name, ))
            if(self.cur.statusmessage.endswith("1")):
                return("Grupo Musical deletado com sucesso!")
            else:
                return("Erro: Grupo Musical não encontrado!")
        except:
            return("Erro: Grupo Musical não encontrado!")

class Playlist():
    def __init__(self, cur):
        self.cur = cur

    def createPlaylist(self, name, description, startTime):
        commandString = "INSERT INTO playlist(nome,descricao,horainicio) VALUES (%s, %s, %s);"
        try:
            self.cur.execute(commandString, (name, description, startTime))
            return("Playlist Criada com Sucesso")
        except:
            return("Erro: Erro na criacao da Playlist")

    def readPlaylist(self, name):
        commandString = "SELECT * FROM playlist WHERE nome = %s LIMIT 1;"
        try:
            self.cur.execute(commandString, (name, ))
            query = self.cur.fetchall()
            # print("Playlist encontrada!")
            # print("IdPlaylist: ", query[0][0])
            # print("nome: ", query[0][1])
            # print("Descricao: ", query[0][2])
            # print("Hora Inicio: ", query[0][3])
            return(query)
        except:
            return("Erro: Playlist não encontrada")

    def readPlaylistHoraInicio(self, startTime):
        commandString = "SELECT * FROM playlist WHERE horainicio = %s LIMIT 1;"
        try:
            self.cur.execute(commandString, (startTime, ))
            query = self.cur.fetchall()
            return(query)
        except:
            return("Erro: Playlist não econtrada")

    def updatePlaylist(self, where, newName, newBio, newStarTime):
        # commandString = "UPDATE playlist SET nome = %s, descricao = %s, horainicio = %s WHERE nome = %s;"
        commandString = """
        UPDATE playlist SET
            nome = COALESCE(%(nome)s, nome), 
            descricao = COALESCE(%(descricao)s, descricao), 
            horainicio = COALESCE(%(horainicio)s, horainicio) 
        WHERE nome = %(where)s
        AND (%(nome)s IS NOT NULL AND %(nome)s IS DISTINCT FROM nome OR
            %(descricao)s IS NOT NULL AND %(descricao)s IS DISTINCT FROM descricao OR
            %(horainicio)s IS NOT NULL AND %(horainicio)s IS DISTINCT FROM horainicio 
        );
        """
        try:
            # self.cur.execute(commandString, (newName, newBio, newStarTime, where))
            self.cur.execute(commandString, {"nome":newName, "descricao":newBio, "horainicio":newStarTime, "where":where})
            return("Playlist atualizada com sucesso")
        except:
            return("Erro: Playlist não encontrada")

    def deletePlaylist(self, name):
        commandString = "DELETE FROM playlist WHERE nome = %s;"
        try:
            self.cur.execute(commandString, (name, ))
            if(self.cur.statusmessage.endswith("1")):
                return("Playlist deletada com sucesso!")
            else:
                return("Erro: Playlist não encontrada!")            
        except Exception as e:
            return("Erro: Playlist não encontrada")

class Musica():
    def __init__(self, cur):
        self.cur = cur

    def createMusica(self, name, year, durationSec, plays, genre, nameGrupoMusical):
        commandString = "INSERT INTO musica(nome,ano,duracaosegundos,plays,genero,fk_grupomusical_idgrupomusical) VALUES (%s, %s, %s, %s, %s, %s);"
        commandStringGrupoMusical = "SELECT * FROM grupomusical WHERE nome = %s LIMIT 1;"
        try:
            self.cur.execute(commandStringGrupoMusical, (nameGrupoMusical,))
            query = self.cur.fetchall()
            idGrupoMusical = query[0][0]
            try:
                self.cur.execute(commandString, (name, year, durationSec, plays, genre, idGrupoMusical))
                return("Musica adicionada com Sucesso!")
            except:
                return("Erro: Erro ao adicionar Musica")
        except Exception as e:
            print (e)
            return("Erro: Grupo musical não encontrado")

    def readMusica(self, name):
        commandString = "SELECT * FROM musica WHERE nome = %s LIMIT 1;"
        try:
            self.cur.execute(commandString, (name, ))
            query = self.cur.fetchall()
            # print("idMusica: ", query[0][0])
            # print("nomeMusica: ", query[0][1])
            # print("anoMusica: ", query[0][2])
            # print("duracaoMusica: ", query[0][3])
            # print("numero de Plays: ", query[0][4])
            # print("genero Musical: ", query[0][5])
            # print("idGrupoMusical: ", query[0][6])
            return(query)
        except:
            return("Erro: Musica não encontrada")

    def readMusicaGenero(self, genre):
        commandString = "SELECT * FROM musica WHERE genero = %s;"
        try:
            self.cur.execute(commandString, (genre, ))
            query = self.cur.fetchall()
            return(query)
        except:
            return("Erro: Musica não encontrada")

    def readMusicaGrupoMusical(self, nameGrupoMusical):
        commandString = "SELECT * FROM musica WHERE fk_grupomusical_idgrupomusical = %s;"
        commandStringGrupoMusical = "SELECT * FROM grupomusical WHERE nome = %s LIMIT 1;"
        try:
            self.cur.execute(commandStringGrupoMusical, (nameGrupoMusical, ))
            query = self.cur.fetchall()
            idGrupoMusical = query[0][0]
            try:
                self.cur.execute(commandString, (idGrupoMusical, ))
                query = self.cur.fetchall()
                return(query)
            except:
                return("Erro: Musica não encontrada")
        except:
            return("Erro: Grupo Musical não encontrado")


    def updateMusica(self, where, newName, newYear, newDurationSec, newPlays, newGenre, nameGrupoMusical):
        # commandString = "UPDATE musica SET nome = %s, ano = %s, duracaosegundos = %s, plays = %s, genero = %s, fk_grupomusical_idgrupomusical = %s WHERE nome = %s;"
        commandStringGrupoMusical = "SELECT * FROM grupomusical WHERE nome = %s LIMIT 1;"
        commandString= """
        UPDATE musica SET
            nome = COALESCE(%(nome)s,nome),
            ano = COALESCE(%(ano)s,ano),
            duracaosegundos = COALESCE(%(duracao)s,duracaosegundos),
            plays = COALESCE(%(plays)s,plays),
            genero = COALESCE(%(genero)s,genero),
            fk_grupomusical_idgrupomusical = COALESCE(%(fk)s,fk_grupomusical_idgrupomusical)
        WHERE nome = %(where)s
        AND (
            %(nome)s IS NOT NULL AND %(nome)s IS DISTINCT FROM nome OR
            %(ano)s IS NOT NULL AND %(ano)s IS DISTINCT FROM ano OR
            %(duracao)s IS NOT NULL AND %(duracao)s IS DISTINCT FROM duracaosegundos OR
            %(plays)s IS NOT NULL AND %(plays)s IS DISTINCT FROM plays OR
            %(genero)s IS NOT NULL AND %(genero)s IS DISTINCT FROM genero OR
            %(fk)s IS NOT NULL AND %(fk)s IS DISTINCT FROM fk_grupomusical_idgrupomusical
        );
        """
        try:
            self.cur.execute(commandStringGrupoMusical, (nameGrupoMusical, ))            
            query = self.cur.fetchall()
            idGrupoMusical = query[0][0]
            try:
                # self.cur.execute(commandString, (newName, newYear, newDurationSec, newPlays, newGenre, idGrupoMusical, where))
                self.cur.execute(commandString, 
                {"nome":newName, "ano":newYear, "duracao":newDurationSec, 
                "plays":newPlays, "genero":newGenre, "fk":idGrupoMusical, "where":where})
                
                return("Musica atualizada com sucesso")
            except:
                return("Erro: Musica não encontrada")
        except:
            return("Erro: Grupo Musical não encontrado")

    def deleteMusica(self, name, banda):
        # commandString = "DELETE FROM musica WHERE nome = %s;"
        cm = """DELETE FROM musica USING grupomusical
                WHERE 
                    musica.fk_grupomusical_idgrupomusical = grupomusical.idgrupomusical
                AND musica.nome = %s
                AND grupomusical.nome = %s;   
        """
        try:
            # self.cur.execute(commandString, (name, ))
            self.cur.execute(cm, (name,banda, ))
            if(self.cur.statusmessage.endswith("1")):
                return("Música deletada com sucesso!")
            else:
                return("Erro: Música ou banda não encontrada!")
        except:
            return("Erro: Musica não encontrada")


class PlaylistCompostaPorMusica():
    def __init__(self, cur):
        self.cur = cur

    def createPlaylistCompostaPorMusica(self, namePlaylist, nameMusic):
        commandString = "INSERT INTO playlistcompostapormusica(fk_playlist_idplaylist, fk_musica_idmusica) VALUES (%s, %s);"
        commandStringIdPlaylist = "SELECT * FROM playlist WHERE nome = %s LIMIT 1;"
        commandStringIdMusica = "SELECT * FROM Musica WHERE nome = %s LIMIT 1;"
        try:
            self.cur.execute(commandStringIdPlaylist, (namePlaylist, ))
            query = self.cur.fetchall()
            idPlaylist = query[0][0]
            self.cur.execute(commandStringIdMusica, (nameMusic, ))
            query = self.cur.fetchall()
            idMusica = query[0][0]
            try:
                self.cur.execute(commandString, (idPlaylist, idMusica))
                return("Playlist Atualizada!")
            except:
                return("Erro: Falha ao atualzar")
        except:
            return("Erro: Musica ou Playlist não encontrado")

    def readPlaylistCompostaPorMusica(self, idPlaylist):
        commandString = "SELECT * FROM playlistcompostapormusica WHERE fk_playlist_idplaylist = %s;"
        try:
            self.cur.execute(commandString, idPlaylist)
            query = self.cur.fetchall()
            # for a in query:
            #     print(a)
            return(query)
        except:
            return("Erro: Playlist não encontrada")
    def updatePlaylistCompostaPorMusica(self, idPlaylist, idMusic, newIdPlaylist, newIdMusic):
        commandString = "UPDATE playlistcompostapormusica SET fk_playlist_idplaylist = %s, fk_musica_idmusica = %s WHERE fk_playlist_idplaylist = %s AND fk_musica_idmusica = '%s';"
        commandString = """UPDATE playlistcompostapormusica SET 
                fk_playlist_idplaylist = COALESCE(%(fk1)s,fk_playlist_idplaylist), 
                fk_musica_idmusica = COALESCE(%(fk2)s,fk_musica_idmusica) 
            WHERE fk_playlist_idplaylist = %(fk3)s AND fk_musica_idmusica = %(fk4)s
            AND (
                %(fk1)s IS NOT NULL AND %(fk1)s IS DISTINCT FROM fk_playlist_idplaylist OR
                %(fk2)s IS NOT NULL AND %(fk2)s IS DISTINCT FROM fk_musica_idmusica 
            );
        """
        try:
            # self.cur.execute(commandString, (newIdPlaylist, newIdMusic, idPlaylist, idMusic))
            self.cur.execute(commandString, 
            {"fk1":newIdPlaylist, "fk2":newIdMusic, "fk3":idPlaylist, "fk4":idMusic})
            return("Playlist atualizada")
        except:
            return("Erro: Playlist não encontrada")

    def deletePlaylistCompostaPorMusica(self, idPlaylist, idMusic):
        commandString = "DELETE FROM playlistcompostapormusica WHERE fk_playlist_idplaylist = %s AND fk_musica_idmusica = %s;"
        try:
            self.cur.execute(commandString, (idPlaylist, idMusic))
            if(self.cur.statusmessage.endswith("1")):
                return("Música removida da playlist com sucesso")
            else:
                return("Erro: Música ou playlist não encontrada!")
        except:
            return("Erro: Música não encontrada na playlist")

class Conexao():
    def __init__(self):
        self._conn = None
        self.cur = self.conectar()

    def conectar(self):
        try:
            dbinfo  = f'dbname={os.getenv("DBNAME")} user={os.getenv("USER")} host={os.getenv("HOST")} password={os.getenv("PWBD")}'
            self._conn = psycopg2.connect(dbinfo)
            self._conn.autocommit = True
            self._conn.set_client_encoding('UTF8')            
            # print("Conectado ao bd!")
            return self._conn.cursor()
        except Exception as e:
            print(e)
            return "Não foi possível conectar com o BD."

    def close(self):
        self._conn.close()

if __name__ == "__main__":
    a = Conexao()
    b = a.cur
    gm = GrupoMusical(b)
    print(gm.deleteGrupoMusical("Lexuss 210"))