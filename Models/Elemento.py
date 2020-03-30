import sys
import os.path
import string

class Elemento():
    def __init__(self,token,lexema,linha):
        self.lexema = lexema
        self.token = token
        self.linha = linha

    def __str__(self):
        return self.lexema + '  ' + self.token
