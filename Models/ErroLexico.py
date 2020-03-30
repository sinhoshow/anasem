import sys
import os.path
import string

class ErroLexico():
    def __init__(self,erro,lexema,linha):
        self.lexema = lexema
        self.erro = erro
        self.linha = linha

    def __str__(self):
        return self.lexema + '  ' + self.erro
