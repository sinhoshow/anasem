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
    corpo_funcoes = []
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
            for i, corpo_funcao in enumerate(self.corpo_funcoes):
                self.verificar_chamada_funcoes(corpo_funcao, self.funcoes[i])
                self.verificar_tipo_atribuicoes(corpo_funcao, self.funcoes[i])            
            self.verificar_retorno_funcoes()
            #Verificacao de erros
            #1-Unicidade
            #self.verificar_unicidade()
            conteudo = ''
            if (self.erros):
                conteudo += '\n\n\nErros: \n\n'
                for erro in self.erros:
                    conteudo += 'Linha:'+ str(erro.linha)+ ' / '+ erro.tipo + ' '+ erro.erro+ '\n'
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
            self.corpo_funcoes.append(content_function)

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
        tipo = ""
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

    def get_params(self, content):
        parametros = []
        tipo = ""        
        if(len(content)!=0):
            for i, elemento in enumerate(content):
                if i==0:
                    tipo = content[i].lexema
                    identificador = content[i+1].lexema
                    var = Variavel(content[i].lexema, identificador, content[i].linha)
                    parametros.append(var)
                elif elemento.lexema == ",":
                    tipo = content[i+1].lexema
                    identificador = content[i+2].lexema
                    var = Variavel(tipo, identificador, content[i].linha)
                    parametros.append(var)
        return parametros

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
        params = self.get_params(auxGroup)
        return params
    
    def get_call_params_functions(self, group, indice, funcao):
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
        params = self.get_call_params(auxGroup, funcao)
        return params
    
    def get_call_params(self, content, funcao):
        parametros = []
        if(len(content)!=0):
            for i, elemento in enumerate(content):
                if elemento.lexema == 'local':
                    variavel = funcao.exists_variavel(content[i+2].lexema)
                    if (not variavel):
                        self.erros.append(Erro('Variavel não declarada', content[i+2].lexema, content[i+2].linha))
                        continue
                    parametros.append(variavel)
                elif elemento.lexema == 'global':
                    variavel = self.verificar_existencia_variaveis(content[i+2].lexema)
                    if (not variavel):
                        self.erros.append(Erro('Variavel não declarada', content[i+2].lexema, content[i+2].linha))
                        continue
                    parametros.append(variavel)
                elif elemento.token == 'Cadeia de caractere':
                    variavel = Variavel('string', 'string', elemento.linha)
                    parametros.append(variavel)
                elif elemento.token == 'Numero' and content[i-1].lexema != '[' and content[i+1] != ']':
                    if '.' in elemento.lexema:
                        variavel = Variavel('real', 'real', elemento.linha)
                    else:
                        variavel = Variavel('int', 'int', elemento.linha)
                    parametros.append(variavel)
                elif elemento == ",":
                    continue
        
        return parametros

    def verificar_tipo_atribuicoes(self, group, funcao):
        indices_igual = [i for i, e in enumerate(group) if e.lexema == '=']
        
        for i ,indice in enumerate(indices_igual):
            escopo = group[indice-3].lexema
            variavel_aux = group[indice-1]
            tipo_variavel = None
            if escopo == 'local':
                variavel = funcao.exists_variavel(variavel_aux.lexema)
                if (not variavel):
                    self.erros.append(Erro('Variavel não declarada', variavel_aux.lexema, variavel_aux.linha))
                else:
                    tipo_variavel = variavel.tipo
            elif escopo == 'global':
                variavel = self.verificar_existencia_variaveis(variavel_aux.lexema)
                if (not variavel):
                    self.erros.append(Erro('Variavel não declarada', variavel_aux.lexema, variavel.linha))
                else:
                    tipo_variavel = variavel.tipo
            
            #verificar caso seja o parâmetro de uma struct
            tipo_variavel2 = None
            if group[indice+1].lexema == 'local':
                variavel2_aux = group[indice+3]
                variavel2 = funcao.exists_variavel(variavel2_aux.lexema)
                if (not variavel2):
                    self.erros.append(Erro('Variavel não declarada', variavel2_aux.lexema, variavel2_aux.linha))
                    continue
                else:
                    tipo_variavel2 = variavel2.tipo
            elif group[indice+1].lexema == 'global':
                variavel2_aux = group[indice+3]
                variavel2 = self.verificar_existencia_variaveis(variavel2_aux.lexema)
                if (not variavel2):
                    self.erros.append(Erro('Variavel não declarada', variavel2_aux.lexema, variavel2_aux.linha))
                    continue
                else:
                    tipo_variavel2 = variavel2.tipo
            
            if (tipo_variavel and tipo_variavel2 and (tipo_variavel != tipo_variavel2)):
                erro = Erro('Atribuição de tipo diferente', variavel2.lexema, variavel2.linha)
                self.erros.append(erro)
                continue
            
            #Verificar expressões

            if group[indice+1].token == 'identificador':
                ##verificar se a funcao existe comparando os parâmetros passados
                indice_funcao = [i for i, e in enumerate(self.funcoes) if e.nome == group[indice+1].lexema]
                if(indice_funcao):
                    tipo_funcao = self.funcoes[indice_funcao[0]].tipo
                    if tipo_variavel != tipo_funcao:
                        erro = Erro('Tipo de funcao invalida', group[indice+1].lexema, group[indice+1].linha)
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

    def verificar_chamada_funcoes(self, group, funcao):
        indices_parenteses = [i for i, e in enumerate(group) if e.lexema == '(']
        for i ,indice in enumerate(indices_parenteses):
            if (group[indice-1].token == 'identificador'):
                indice_funcao = [i for i, e in enumerate(self.funcoes) if e.nome == group[indice-1].lexema]
                if(not indice_funcao):
                    indice_procedimento = [i for i, e in enumerate(self.procedimentos) if e.nome == group[indice-1].lexema]
                    if (indice_procedimento):
                        parametros_procedimento = self.get_call_params_functions(group, indice-1, funcao)
                        if (not self.procedimentos[indice_procedimento[0]].verify_params(parametros_procedimento)):
                            erro = Erro('Parametros invalidos', group[indice-1].lexema, group[indice-1].linha)
                            self.erros.append(erro)
                    else:
                        erro = Erro('Funcao ou procedimento nao encontrado', group[indice-1].lexema, group[indice-1].linha)
                        self.erros.append(erro)
                if(indice_funcao):
                    ##pegando parametros da funcao
                    parametros_funcao = self.get_call_params_functions(group, indice-1, funcao)
                    if (not self.funcoes[indice_funcao[0]].verify_params(parametros_funcao)):
                        erro = Erro('Parametros invalidos', group[indice+1].lexema, group[indice+1].linha)
                        self.erros.append(erro)

            
    def verificar_existencia_variaveis(self, variavel):
        for variavel_global in self.variaveis:
            if variavel == variavel_global.nome:
                return variavel_global
        for constante in self.constantes:
            if variavel == constante.nome:
                return constante
        return False
    # def verificar_existencia_variaveis(self, group, funcao):

    # def verificar_expressoes(self, group):

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