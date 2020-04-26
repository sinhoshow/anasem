import sys
import os.path
import string

class Funcao():
    def __init__(self,tipo,nome,parametros,variaveis,retorno, linha):
        self.tipo = tipo
        self.nome = nome
        self.parametros = parametros
        self.linha = linha
        self.variaveis = variaveis
        self.retorno = retorno
    
    def __str__(self):
        return str(self.linha) + ' || ' + 'Metodo: ' + self.tipo + ' ' + self.nome
    
    def exists_variavel(self, variavel):
        for parametro in self.parametros:
            if variavel == parametro.nome:
                return parametro
        for variavel_funcao in self.variaveis:
            if variavel == variavel_funcao.nome:
                return variavel_funcao
        return False

    def verify_params(self, params):
        if (len(self.parametros) != len(params)):
            return False
        for i, parametro in enumerate(self.parametros):
            if (parametro.tipo != params[i].tipo):
                return False
        return True