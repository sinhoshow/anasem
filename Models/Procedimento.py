import sys
import os.path
import string

class Procedimento():
    def __init__(self,nome,parametros,linha):
        self.nome = nome
        self.linha = linha
        self.variaveis = []


    def __str__(self):
        return self.linha + ' || ' + 'Metodo: ' + self.tipo + ' ' + self.nome   
        