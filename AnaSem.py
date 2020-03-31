import sys
import os.path
import string
from AnaLex import Analex
from Models.Estrutura import Estrutura
from Models.Variavel import Variavel

class AnaSem():
    metodos = []
    procedimentos = []
    constantes = []
    variaveis = []
    estruturas = []
    typedefs = []
    linha=1

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
        contents_structs = self.find_bracket_groups(group)
        for i, indice in enumerate(indexes_structs):
            atributos = []
            atributosAux = self.split_lists(contents_structs[i], ';')
            for atributo in atributosAux:
                atributos.append(Variavel(atributo[0], atributo[1], self.linha))
            self.estruturas.append(Estrutura(group[indice+1], atributos, self.linha))

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

    def split_lists(self, lista, spliter):
        indexes_of_spliter = [i for i, e in enumerate(lista) if e == spliter]

        listas = [lista[i : j] for i, j in zip([0] + 
          indexes_of_spliter, indexes_of_spliter + [None])]
        del(listas[-1])

        for auxList in listas:
            try:
                auxList.remove(spliter)
            except:
                continue

        return listas



analisador_semantico = AnaSem()
analisador_semantico.analisa()