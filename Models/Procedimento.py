import sys
import os.path
import string

class Procedimento():
    def __init__(self,nome,parametros, variaveis, linha):
        self.nome = nome
        self.parametros = parametros
        self.linha = linha
        self.variaveis = variaveis


    def __str__(self):
        return self.linha + ' || ' + 'Procedimento: ' + self.nome
        