import sys
import os.path
import string
from AnaLex import Analex
from Models import *

class AnaSem():
    metodos = []
    procedimentos = []
    constantes = []
    variaveis = []
    estruturas = []
    typedefs = []

    def analisa(self):
        erros = []
        analex = Analex()
        arquivos = os.listdir('input')        
        for nome_arquivo in arquivos:
            elementos = analex.analisa(nome_arquivo)
            elementos_lexemas = self.get_lexemas(elementos)
            groups = self.find_bracket_groups(elementos_lexemas)
            self.preencher_estruturas(groups[0])
            """self.preencher_typedefs(groups[1])
            self.preencher_constantes(groups[2])
            self.preencher_variaveis_globais(groups[3])
            self.preencher_funcoes(groups[4])
            self.preencher_procedimos(groups[5])
            self.preencher_start(groups[6])"""
            conteudo = ''
            if (erros):
                conteudo += '\n\n\nErros: \n\n'
                for erro in erros:
                    conteudo += 'Linha:'+ str(erro.linha)+ ' / Lexema:'+ erro.lexema+ ' / Token: '+ erro.erro+ '\n'
            else:
                conteudo += "SUCESSO! sem erros"
            
            saida = open('output/' + nome_arquivo, 'w')
            saida.write(conteudo)
            saida.close()

    def get_lexemas(self, elementos):
        lexemas = []
        for elemento in elementos:
            lexemas.append(elemento.lexema)
        return lexemas
        
    def find_bracket_groups(self, texts):
        open_brackets = 0
        groups = []
        current_group = []
        for i, elemento in enumerate(texts):
            if elemento == "{":
                open_brackets += 1
            if open_brackets > 0:
                current_group.append(texts[i])
            if elemento == "}":
                open_brackets -= 1
                if open_brackets == 0:
                    del(current_group[0])
                    del(current_group[-1])
                    groups.append(current_group)
                    current_group = []
                if open_brackets < 0:
                    open_brackets = 0
        return groups
    
    def preencher_estruturas(self, group):
        indexes_structs = [i for i, e in enumerate(group) if e == 'struct']
        contents_strucuts = self.find_bracket_groups(group)
        print(len(contents_strucuts))

    def preencher_typedefs(self, group):
        print(group)
    def preencher_constantes(self, group):
        print(group)
    def preencher_variaveis_globais(self, group):
        print(group)
    def preencher_funcoes(self, group):
        print(group)
    def preencher_procedimos(self, group):
        print(group)
    def preencher_start(self, group):
        print(group)



analisador_semantico = AnaSem()
analisador_semantico.analisa()