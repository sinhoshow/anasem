import sys
import os.path
import string

class Erro():
    def __init__(self,tipo,erro,linha):
        self.tipo = tipo
        self.erro = erro
        self.linha = linha

    def __str__(self):
        return self.tipo + '  ' + self.erro
