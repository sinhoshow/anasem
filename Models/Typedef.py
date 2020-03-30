import sys
import os.path
import string

class Typedef():
    def __init__(self,nome_struct,nome_typedef,linha):
        self.nome_struct = nome_struct
        self.nome_typedef = nome_typedef
        self.linha = linha

    def __str__(self):
        return self.linha + ' || ' + self.nome_struct + ' -> ' + self.nome_typedef
        