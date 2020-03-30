import sys
import os.path
import string
from AnaLex import Analex
from Models import *

class AnaSem():
    metodos = []
    procedimentos = []
    constantes = []
    variaveis = []
    estruturas = []
    typedefs = []

    def analisa(self):
        erros = []
        analex = Analex()
        arquivos = os.listdir('input')        
        for nome_arquivo in arquivos:
            elementos = analex.analisa(nome_arquivo)
            for elemento in elementos:
                print(elemento.lexema)
            conteudo = ''            
            if (erros):
                conteudo += '\n\n\nErros: \n\n'
                for erro in erros:
                    conteudo += 'Linha:'+ str(erro.linha)+ ' / Lexema:'+ erro.lexema+ ' / Token: '+ erro.erro+ '\n'
            else:
                conteudo += "SUCESSO! sem erros"
            
            saida = open('output/' + nome_arquivo, 'w')
            saida.write(conteudo)
            saida.close()




analisador_semantico = AnaSem()
analisador_semantico.analisa()