import sys
import os.path
import string

class Estrutura():
    def __init__(self,nome,atributos,linha, extends = None):
        self.nome = nome
        self.atributos = atributos
        self.linha = linha
        self.extends = extends

    def __str__(self):
        return str(self.linha) + ' || struct ' + self.nome