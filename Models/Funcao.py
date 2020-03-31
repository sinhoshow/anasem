import sys
import os.path
import string

class Funcao():
    def __init__(self,tipo,nome,parametros,variaveis,linha,):
        self.tipo = tipo
        self.nome = nome
        self.parametros = parametros
        self.linha = linha
        self.variaveis = variaveis


    def __str__(self):
        return self.linha + ' || ' + 'Metodo: ' + self.tipo + ' ' + self.nome   
        