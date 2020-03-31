import sys
import os.path
import string

class Estrutura():
    def __init__(self,nome,atributos,linha):
        self.nome = nome
        self.atributos = atributos
        self.linha = linha

    def __str__(self):
        return str(self.linha) + ' || struct ' + self.nome