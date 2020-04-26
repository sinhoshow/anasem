import sys
import os.path
import string

class Variavel():
    def __init__(self,tipo,nome,linha):
        self.tipo = tipo
        self.nome = nome
        self.linha = linha

    def __str__(self):
        return str(self.linha) + ' || ' + self.tipo + '  ' + self.nome + '  '  

    def __eq__(self, other):
        return self.nome == other.nome
