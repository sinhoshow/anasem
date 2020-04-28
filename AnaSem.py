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
    corpo_procedimentos = []
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
            for i, corpo_funcao in enumerate(self.corpo_funcoes):             
                self.verificar_chamada_funcoes(corpo_funcao, self.funcoes[i])
                self.verificar_tipo_atribuicoes(corpo_funcao, self.funcoes[i])
            for i, corpo_procedimento in enumerate(self.corpo_procedimentos):             
                self.verificar_chamada_funcoes(corpo_procedimento, self.procedimentos[i])
                self.verificar_tipo_atribuicoes(corpo_procedimento, self.procedimentos[i])            
            self.verificar_retorno_funcoes()
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
            self.estruturas.append(Estrutura(group[indice+1].lexema, atributos, group[indice+1].linha))

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
            self.corpo_procedimentos.append(content_procedure)

    def preencher_start(self, group):
        return

    def split_lists(self, lista, spliter):
        
        indexes_of_spliter = [i for i, e in enumerate(lista) if e.lexema == spliter]

        listas = [lista[i : j] for i, j in zip([0] + 
          indexes_of_spliter, indexes_of_spliter + [None])]
        del(listas[-1])

        for auxList in listas:
            indexes_of_spliter = [i for i, e in enumerate(auxList) if e.lexema == spliter]
            try:
                for spliter in indexes_of_spliter:
                    auxList.remove(auxList[spliter])
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
                if (elemento.lexema == 'local' or elemento.lexema == 'global'):
                    if elemento.lexema == 'local':
                        variavel = funcao.exists_variavel(content[i+2].lexema)
                    elif elemento.lexema == 'global':
                        variavel = self.verificar_existencia_variaveis(content[i+2].lexema)
                    if (not variavel):
                        self.erros.append(Erro('Variavel não declarada', content[i+2].lexema, content[i+2].linha))
                        continue    
                    if content[i+3].lexema == '.':
                            atributo_struct = content[i+4]
                            struct_name = variavel.tipo
                            estrutura_indice = [i for i, e in enumerate(self.estruturas) if e.nome == struct_name]
                            if (estrutura_indice):
                                estrutura = self.estruturas[estrutura_indice[0]]
                                atributo = estrutura.get_attribute(atributo_struct.lexema)
                                if(atributo):
                                    parametros.append(Variavel(atributo.tipo, atributo.nome, atributo_struct.linha))
                                else:
                                    self.erros.append(Erro('Atributo da estrutura inválido ou não declarado', atributo_struct.lexema, atributo_struct.linha))
                            else:
                                self.erros.append(Erro('Tipo de estrutura inválido ou não declarado', variavel.lexema, variavel.linha))
                    else:
                        parametros.append(variavel)
                elif elemento.token == 'Cadeia de caractere':
                    variavel = Variavel('string', 'string', elemento.linha)
                    parametros.append(variavel)
                elif elemento.token == 'Numero':
                    try:
                        if content[i-1].lexema != '[' and content[i+1] != ']':
                            if '.' in elemento.lexema:
                                variavel = Variavel('real', 'real', elemento.linha)
                            else:
                                variavel = Variavel('int', 'int', elemento.linha)
                            parametros.append(variavel)
                    except:
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
            if (group[indice-4].lexema != '.'):                
                escopo = group[indice-3].lexema
                variavel_aux = group[indice-1]
                tipo_variavel = None
                if escopo == 'local':
                    variavel = funcao.exists_variavel(variavel_aux.lexema)
                elif escopo == 'global':
                    variavel = self.verificar_existencia_variaveis(variavel_aux.lexema)
                if (not variavel):
                    self.erros.append(Erro('Variavel não declarada', variavel_aux.lexema, variavel_aux.linha))
                else:
                    tipo_variavel = variavel.tipo
            else:                           
                escopo = group[indice-5].lexema
                variavel_aux = group[indice-3]                
                atributo_struct = group[indice-1]
                tipo_variavel = None                
                if escopo == 'local':
                    variavel = funcao.exists_variavel(variavel_aux.lexema)
                elif escopo == 'global':
                    variavel = self.verificar_existencia_variaveis(variavel_aux.lexema)
                if (not variavel):
                    self.erros.append(Erro('Variavel não declarada', variavel_aux.lexema, variavel_aux.linha))
                else:                    
                    struct_name = variavel.tipo
                    estrutura_indice = [i for i, e in enumerate(self.estruturas) if e.nome == struct_name]
                    if (estrutura_indice):
                        estrutura = self.estruturas[estrutura_indice[0]]
                        atributo = estrutura.get_attribute(atributo_struct.lexema)
                        if(atributo):
                            tipo_variavel = atributo.tipo
                        else:
                            self.erros.append(Erro('Atributo da estrutura inválido ou não declarado', atributo_struct.lexema, atributo_struct.linha))
                    else:
                        self.erros.append(Erro('Tipo de estrutura inválido ou não declarado', variavel_aux.lexema, variavel_aux.linha))


            tipo_variavel2 = self.get_atribuivel(group, indice, funcao)
            if (tipo_variavel and tipo_variavel2 and (tipo_variavel != tipo_variavel2)):
                    erro = Erro('Atribuição de tipo diferente', variavel.nome, variavel.linha)
                    self.erros.append(erro)
                    continue
            if (group[indice+1].lexema == 'local' or group[indice+1].lexema == 'global' and not tipo_variavel2):              
                if group[indice+1].lexema == 'local':
                    variavel2_aux = group[indice+3]
                    variavel2 = funcao.exists_variavel(variavel2_aux.lexema)
                elif group[indice+1].lexema == 'global':
                    variavel2_aux = group[indice+3]
                    variavel2 = self.verificar_existencia_variaveis(variavel2_aux.lexema)
                if (not variavel2):
                    self.erros.append(Erro('Variavel não declarada', variavel2_aux.lexema, variavel2_aux.linha))
                    continue                
                if group[indice+4].lexema == '.':
                    atributo_struct2 = group[indice+5]                 
                    struct_name2 = variavel2.tipo
                    estrutura_indice2 = [i for i, e in enumerate(self.estruturas) if e.nome == struct_name2]
                    if (estrutura_indice2):
                        estrutura2 = self.estruturas[estrutura_indice2[0]]
                        atributo2 = estrutura2.get_attribute(atributo_struct2.lexema)
                        if(atributo2):
                            tipo_variavel2 = atributo2.tipo
                        else:
                            self.erros.append(Erro('Atributo da estrutura inválido ou não declarado', atributo_struct2.lexema, atributo_struct2.linha))
                    else:
                        self.erros.append(Erro('Tipo de estrutura inválido ou não declarado', variavel2_aux.lexema, variavel2_aux.linha))                
                else:
                    tipo_variavel2 = variavel2.tipo
            
                if (tipo_variavel and tipo_variavel2 and (tipo_variavel != tipo_variavel2)):
                    erro = Erro('Atribuição de tipo diferente', variavel2.nome, variavel2.linha)
                    self.erros.append(erro)
                    continue

            elif group[indice+1].token == 'identificador':
                indice_funcao = [i for i, e in enumerate(self.funcoes) if e.nome == group[indice+1].lexema]
                if(indice_funcao):
                    tipo_funcao = self.funcoes[indice_funcao[0]].tipo
                    if tipo_variavel != tipo_funcao:
                        erro = Erro('Tipo de funcao invalida', group[indice+1].lexema, group[indice+1].linha)
                        self.erros.append(erro)
                else:
                    erro = Erro('Procedimentos não são atribuíveis', group[indice+1].lexema, group[indice+1].linha)
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
                        erro = Erro('Parametros invalidos', group[indice-1].lexema, group[indice-1].linha)
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
                if (len(retorno_total) <= 3):
                    indice_retorno = [i for i, e in enumerate(variaveis) if e.nome == variavel_retorno]                
                    if indice_retorno:
                        retorno = variaveis[indice_retorno[0]]
                    if not indice_retorno:                        
                        indice_retorno = [i for i, e in enumerate(parametros) if e.nome == variavel_retorno]
                        if indice_retorno:
                            retorno = parametros[indice_retorno[0]]
                        if not indice_retorno:
                            self.erros.apped(Erro('Variável de retorno não declarada na funcao', funcao.nome, funcao.linha))
                
            elif (escopo == 'global'):
                if (len(retorno_total) <= 3):
                    indice_retorno = [i for i, e in enumerate(self.variaveis) if e.nome == variavel_retorno]
                    if indice_retorno:
                        retorno = self.variaveis[indice_retorno[0]]
                    if not indice_retorno:
                        indice_retorno = [i for i, e in enumerate(self.constantes) if e.nome == variavel_retorno]
                        if indice_retorno:
                            retorno = self.constantes[indice_retorno[0]]
                        if not indice_retorno:
                            self.erros.apped(Erro('Variável de retorno não declarada na funcao', funcao.nome, funcao.linha))
            
            
            if funcao.tipo != retorno.tipo:
                    erro = Erro('Tipo de retorno invalido', funcao.nome, funcao.linha)
                    self.erros.append(erro)

    def get_atribuivel(self, group, indice, funcao):
        group = group[indice+1:]
        auxGroup = []
        for element in group:
            if element.lexema == ';':
                break
            else:
                auxGroup.append(element)
        
        return self.verificar_expressoes(auxGroup, funcao)

    
    def verificar_expressoes(self, exp, funcao):
        auxElement = []
        delimitadores = ['+', '-', '*', '/', '(', ')']
        for elemento in exp:
            if (not elemento.lexema in delimitadores):
                auxElement.append(elemento)
        
        # for a in auxElement:
        #     print(a)

        tiposElementos = []
        for i, aux in enumerate(auxElement):
            
            if (aux.lexema == 'local' or aux.lexema == 'global'):
                if aux.lexema == 'local':
                    variavel2_aux = auxElement[i+2]
                    variavel2 = funcao.exists_variavel(variavel2_aux.lexema)
                elif aux.lexema == 'global':
                    variavel2_aux = auxElement[i+2]
                    variavel2 = self.verificar_existencia_variaveis(variavel2_aux.lexema)
                if (not variavel2):
                    self.erros.append(Erro('Variavel não declarada', variavel2_aux.lexema, variavel2_aux.linha))
                    continue                
                if auxElement[i+3].lexema == '.':
                    atributo_struct2 = auxElement[i+4]                 
                    struct_name2 = variavel2.tipo
                    estrutura_indice2 = [i for i, e in enumerate(self.estruturas) if e.nome == struct_name2]
                    if (estrutura_indice2):
                        estrutura2 = self.estruturas[estrutura_indice2[0]]
                        atributo2 = estrutura2.get_attribute(atributo_struct2.lexema)
                        if(atributo2):
                            tipo_variavel2 = atributo2.tipo
                            tiposElementos.append(tipo_variavel2)
                        else:
                            self.erros.append(Erro('Atributo da estrutura inválido ou não declarado', atributo_struct2.lexema, atributo_struct2.linha))
                    else:
                        self.erros.append(Erro('Tipo de estrutura inválido ou não declarado', variavel2_aux.lexema, variavel2_aux.linha))                
                else:
                    tipo_variavel2 = variavel2.tipo
                    tiposElementos.append(tipo_variavel2)         
            elif aux.token == 'Cadeia de caractere':
                tiposElementos.append('string')
            elif aux.token == 'Numero':
                try:
                    if content[i-1].lexema != '[' and content[i+1] != ']':
                        if '.' in aux.lexema:
                            tiposElementos.append('real')
                        else:
                            tiposElementos.append('int')
                except:
                    if '.' in aux.lexema:
                        tiposElementos.append('real')
                    else:
                        tiposElementos.append('int')
        
        if(all(x == tiposElementos[0] for x in tiposElementos)):
            return tiposElementos[0]
        else:
            self.erros.append(Erro('Expressão entre tipos diferentes', 'Exp Aritimetica', auxElement[0].linha))

        return False

analisador_semantico = AnaSem()
analisador_semantico.analisa()