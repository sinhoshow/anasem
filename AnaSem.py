import sys
import os.path
import string
from Models import *

class AnaSem():
    metodos = []
    procedimentos = []
    constantes = []
    variaveis = []
    estruturas = []
    typedefs = []

    def analisa(self):
        arquivos = os.listdir('input')        
        for arquivo in arquivos:
            arquivo = open('input/' + arquivo, 'r')
            erros = []
            #processar codigo


            arquivo.close()
            conteudo = ''            
            if (erros):
                conteudo += '\n\n\nErros: \n\n'
                for erro in erros:
                    conteudo += 'Linha:'+ str(erro.linha)+ ' / Lexema:'+ erro.lexema+ ' / Token: '+ erro.erro+ '\n'
            else:
                conteudo += "SUCESSO! sem erros"
            
            saida = open('output/' + arquivo, 'w')
            saida.write(conteudo)
            saida.close()
            