import sys
import os.path
import string

from Models import *
from AnaLex import Analex
from Models.Typedef import Typedef
from Models.Variavel import Variavel
from Models.Funcao import Funcao
from Models.Estrutura import Estrutura 
from Models.Procedimento import Procedimento
from Models.Erro import Erro

class AnaSem():
    funcoes = []
    procedimentos = []
    constantes = []
    variaveis = []
    estruturas = []
    typedefs = []
    erros = []

    def analisa(self):
        
        analex = Analex()
        arquivos = os.listdir('input')        
        for nome_arquivo in arquivos:
            elementos = analex.analisa(nome_arquivo)
            groups = self.find_bracket_groups(elementos)
            self.preencher_estruturas(groups[0])
            self.preencher_typedefs(groups[1])
            self.preencher_constantes(groups[2])
            self.preencher_variaveis_globais(groups[3])
            self.preencher_funcoes(groups[4])
            self.preencher_procedimentos(groups[5])
            self.preencher_start(groups[6])
            self.verificar_retorno_funcoes()
            conteudo = ''
            if (self.erros):
                conteudo += '\n\n\nErros: \n\n'
                for erro in self.erros:
                    conteudo += 'Linha:'+ str(erro.linha)+ ' / '+ erro.tipo +  '\n'
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
        
    def find_bracket_groups(self, elementos):
        open_brackets = 0
        groups = []
        current_group = []
        for i, elemento in enumerate(elementos):
            if elemento.lexema == "{":
                open_brackets += 1
            if open_brackets > 0:
                current_group.append(elementos[i])
            if elemento.lexema == "}":
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
        indexes_structs = [i for i, e in enumerate(group) if e.lexema == 'struct']
        indexes_extends = [i for i, e in enumerate(group) if e.lexema == 'extends']
        contents_structs = self.find_bracket_groups(group)
        for i, indice in enumerate(indexes_structs):
            atributos = []
            atributos_aux = self.split_lists(contents_structs[i], ';')
            for atributo in atributos_aux:
                atributos.append(Variavel(atributo[0].lexema, atributo[1].lexema, atributo[1].linha))
            self.estruturas.append(Estrutura(group[indice+1], atributos, group[indice+1].linha))

        for indice_extends in indexes_extends:
            for estrutura in self.estruturas:
                if estrutura.nome == group[indice_extends-1]:
                    estrutura.extends = group[indice_extends+1]

    def preencher_typedefs(self, group):
        for i, elemento in enumerate(group):
            if elemento.lexema == "typedef":
                td = Typedef(group[i+2].lexema, group[i+3].lexema, group[i+2].linha)
                self.typedefs.append(td)

    def preencher_funcoes(self, group):
        
        indexes_functions = [i for i, e in enumerate(group) if e.lexema == 'function']
        for i, indice in enumerate(indexes_functions):            
            variaveis = []
            params = []

            params = self.get_params_functions(group, indice)
            content_function = self.find_bracket_groups(group)[i]            
            content_var = self.find_bracket_groups(content_function)[0]

            index_retorno = [i for i, e in enumerate(content_function) if e.lexema == 'return']
            retorno = content_function[index_retorno[0]+1].lexema + content_function[index_retorno[0]+2].lexema + content_function[index_retorno[0]+3].lexema

            variaveis = self.get_variaveis(content_var)
            funcao = Funcao(group[indice+1].lexema, group[indice+2].lexema, params, variaveis, retorno, group[indice+1].linha)
            self.funcoes.append(funcao)
            self.verificar_tipo_atribuicoes(content_function, funcao)

    def preencher_constantes(self, group):
        self.constantes = self.get_variaveis(group)

    def preencher_variaveis_globais(self, group):
        self.variaveis = self.get_variaveis(group)

    def preencher_procedimentos(self, group):
        indexes_procedures = [i for i, e in enumerate(group) if e.lexema == 'procedure']
        for i, indice in enumerate(indexes_procedures):
            variaveis = []
            params = []
            params = self.get_params_functions(group, indice)
            content_procedure = self.find_bracket_groups(group)[i]
            content_var = self.find_bracket_groups(content_procedure)[0]
            variaveis = self.get_variaveis(content_var)
            self.procedimentos.append(Procedimento(group[indice+1].lexema, params, variaveis, group[indice+1].linha))

    def preencher_start(self, group):
        return

    def split_lists(self, lista, spliter):
        indexes_of_spliter = [i for i, e in enumerate(lista) if e.lexema == spliter]

        listas = [lista[i : j] for i, j in zip([0] + 
          indexes_of_spliter, indexes_of_spliter + [None])]
        del(listas[-1])

        for auxList in listas:
            try:
                auxList.remove(spliter)
            except:
                continue

        return listas

    def get_variaveis(self, content):
        variaveis = []
        if(len(content)!=0):
            for i, elemento in enumerate(content):
                if i==0:
                    tipo = content[i].lexema
                    var = Variavel(content[i].lexema, content[i+1].lexema, content[i].linha)
                    variaveis.append(var)
                elif elemento.lexema == ",":
                    var = Variavel(tipo, content[i+1].lexema, content[i].linha)
                    variaveis.append(var)
                elif elemento.lexema == ";" and i+1 != len(content):
                    tipo = content[i+1].lexema
                    var = Variavel(tipo, content[i+2].lexema, content[i+1].linha)
                    variaveis.append(var)
        return variaveis

    def get_params_functions(self, group, indice):
        open_parenteses = 0
        group = group[indice:]
        auxGroup = []
        for elemento in group:
            if elemento.lexema == "(":
                open_parenteses += 1
            if open_parenteses > 0:
                auxGroup.append(elemento)
            if elemento.lexema == ")":
                del(auxGroup[0])
                del(auxGroup[-1])
                break
        params = self.get_variaveis(auxGroup)
        return params

    def verificar_tipo_atribuicoes(self, group, funcao):
        indices_igual = [i for i, e in enumerate(group) if e.lexema == '=']
        
        for i ,indice in enumerate(indices_igual):
            variavel = group[indice-1].lexema
            indice_variavel = [i for i, e in enumerate(funcao.variaveis) if e.nome == variavel]
            tipo_variavel = funcao.variaveis[indice_variavel[0]].tipo
            
            if group[indice+1].lexema == 'local' or group[indice+1].lexema == 'global':
                variavel2 = group[indice+3]                
                indice_variavel2 = [i for i, e in enumerate(funcao.variaveis) if e.nome == variavel2]
                tipo_variavel2 = funcao.variaveis[indice_variavel2[0]].tipo
                if (tipo_variavel != tipo_variavel2):
                    erro = Erro('Atribuição de tipo diferente', variavel2, 1)
                    self.erros.append(erro)
                    continue

            if group[indice+1].token == 'identificador':
                indice_funcao = [i for i, e in enumerate(self.funcoes) if e.nome == group[indice+1].lexema]
                if(indice_funcao):
                    tipo_funcao = self.funcoes[indice_funcao[0]].tipo
                    if tipo_variavel != tipo_funcao:
                        erro = Erro('Tipo de funcao invalida', group[indice+1].lexema, group[indice+1].linha)
                        self.erros.append(erro)
                else:   
                        erro = Erro('Funcao nao encontrada ou ainda nao declarada', group[indice+1].lexema, group[indice+1].linha)
                        self.erros.append(erro)
            elif tipo_variavel == 'int' and not group[indice+1].lexema.isdigit():
                erro = Erro('Tipo inteiro invalido', group[indice+1].lexema, group[indice+1].linha)
                self.erros.append(erro)

            elif tipo_variavel == 'boolean' and not (group[indice+1].lexema == 'true' or group[indice+1].lexema == 'false'):
                erro = Erro('Tipo booleano invalido', group[indice+1].lexema, group[indice+1].linha)
                self.erros.append(erro)

            elif tipo_variavel == 'string' and not group[indice+1].token == 'Cadeia de caractere':
                erro = Erro('Tipo string invalido', group[indice+1].lexema, group[indice+1].linha)
                self.erros.append(erro)

            elif (tipo_variavel == 'real' and group[indice+1].token == 'Numero') and '.' in group[indice+1].lexema:
                erro = Erro('Tipo real invalido', group[indice+1].lexema, group[indice+1].linha)
                self.erros.append(erro)
            
            


    def verificar_retorno_funcoes(self):
        for funcao in self.funcoes:
            variaveis = funcao.variaveis
            parametros = funcao.parametros
            retorno_total = funcao.retorno.split('.')
            variavel_retorno = retorno_total[-1]
            escopo = retorno_total[0]
            if (escopo == 'local'):
                indice_retorno = [i for i, e in enumerate(variaveis) if e.nome == variavel_retorno]                
                if indice_retorno:
                    retorno = variaveis[indice_retorno[0]]
                if not indice_retorno:
                    
                    indice_retorno = [i for i, e in enumerate(parametros) if e.nome == variavel_retorno]
                    if indice_retorno:
                        retorno = parametros[indice_retorno[0]]
                
            elif (escopo == 'global'):
                indice_retorno = [i for i, e in enumerate(self.variaveis) if e.nome == variavel_retorno]
                if indice_retorno:
                    retorno = self.variaveis[indice_retorno[0]]
                if not indice_retorno:
                    indice_retorno = [i for i, e in enumerate(self.constantes) if e.nome == variavel_retorno]
                    if indice_retorno:
                        retorno = self.constantes[indice_retorno[0]]
            
            
            if funcao.tipo != retorno.tipo:
                    erro = Erro('Tipo de retorno invalido', funcao.nome, funcao.linha)
                    self.erros.append(erro)



analisador_semantico = AnaSem()
analisador_semantico.analisa()