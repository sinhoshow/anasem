import sys
import os.path
import string
from Models.Elemento import Elemento
from Models.ErroLexico import ErroLexico as Erro

class Analex():
    delimitadores = [';', ',', '(', ')', '[', ']', '{', '}', '.']
    palavras_reservadas = ['var', 'const', 'typedef', 'struct', 'extends', 'procedure', 'function', 'start', 'return', 'if', 'else', 'then', 'while', 'read', 'print', 'int', 'real', 'boolean', 'string', 'true', 'false', 'global', 'local']
    operadores_aritmeticos = ['+','-', '*', '/', '--', '++']
    operadores_logicos = ['!=', '==', '<', '<=', '>', '>=', '=']
    operadores_relacionais = ['!', '&&', '||']
    simbolos = ['#','$','%','&','?','^','~','´','@','_','`','\\',' ']
    digitos = ['0','1','2', '3','4','5','6','7','8' ,'9']    
    letras = list(string.ascii_letters)
    lexema = ''
    estado_erro = True
    alfabeto = delimitadores + operadores_aritmeticos + operadores_relacionais + simbolos + letras + digitos
    
    
       

    def analisa(self, a):
        arquivo = open('input/' + a, 'r')
        arquivoAux = open('input/' + a, 'r')        
        erros = []
        elementos = []        
        linhaAtual = 1
        totalLinhas = 0
        ##Contagem do total de linhas do arquivo
        with arquivo as f:
            for line in f:
                totalLinhas += 1

        

        while linhaAtual <= totalLinhas:
            
            linha = arquivoAux.readline()
            
            y = 0
            
            while(y<len(linha)):
                if linha[y] in self.digitos:
                    y = self.autoDigito(y, linha, elementos, linhaAtual, totalLinhas, erros)
                elif linha[y] == "\"":
                    y = self.autoCadCaracteres(y, linha, elementos, linhaAtual, totalLinhas, erros)
                elif linha[y] in self.letras:                    
                    y = self.autoIdentificador(y, linha, elementos, linhaAtual, totalLinhas, erros)
                elif linha[y] == ';' or linha[y] == ',' or linha[y] == '(' or linha[y] == ')' or linha[y] == '[' or linha[y] == ']' or linha[y] == '{' or linha[y] == '}' or linha[y] == '.': 
                    y = self.autoDelimitador(y,linha,elementos,linhaAtual)
                elif linha[y] == '+' or linha[y] == '*' or linha[y] == '-' or linha[y] == '/':
                    xy = self.autoOpAritmetico(y,linha,elementos,linhaAtual,totalLinhas, erros)
                    y = xy[1]
                    
                    #Caso tenha pulado linhas (Processo de bloco de comentarios)
                    # x = Linhas puladas
                    # y = Caracter atual
                    if xy[0] != 0:
                        linhasPuladas = xy[0]
                        for cont in range(0,linhasPuladas):
                            linha = arquivoAux.readline()
                            linhaAtual += 1

                elif linha[y] == '<' or linha[y] == '>' or linha[y] == '=' or linha[y] == '!' or linha[y] == '&' or linha[y] == '|':
                    y = self.autoOpRelacionaisLogicos(y,linha,elementos,linhaAtual, erros)
                elif linha[y] == ' ' or linha[y] == '\n':
                    y += 1
                else:
                    self.lexema += linha[y]
                    erro = Erro("Simbolo não identificado", self.lexema, linhaAtual)
                    erros.append(erro)
                    self.lexema = ''
                    y += 1
                    

            linhaAtual += 1        
            print('-------------------------------') 

        
        arquivoAux.close()
        arquivo.close()
        return elementos

    def autoIdentificador(self, y, linha, elementos, linhaAtual, totalLinhas, erros):
        self.lexema += linha[y]
        if (y < len(linha)):
            y += 1
        while y < len(linha) and (linha[y] in self.letras or linha[y] in self.digitos or linha[y] == '_'):
            self.lexema += linha[y]
            if (y < len(linha)):
                y += 1
        if (self.lexema in self.palavras_reservadas):
            elemento = Elemento("palavra_reservada", self.lexema, linhaAtual)
        else:
            elemento = Elemento("identificador", self.lexema, linhaAtual)
        elementos.append(elemento)
        self.lexema = ''
        return y

    def autoDigito(self, y, linha, elementos, linhaAtual, totalLinhas, erros):        
        self.estado_erro = False
        self.lexema += linha[y]
        if (y < len(linha)):
            y+=1
        while y < len(linha) and (linha[y] in self.digitos):
            self.estado_erro = False
            self.lexema += linha[y]                       
            if (y < len(linha)):
                y += 1
        if y < len(linha) and linha[y] == '.':
            self.lexema += linha[y]
            self.estado_erro = True            
            if (y < len(linha)):
                y+=1
            while y < len(linha) and (linha[y] in self.digitos):
                self.estado_erro = False
                self.lexema += linha[y]                
                if (y < len(linha)):
                    y += 1
        
        if (self.estado_erro):
            erro = Erro("Numero mal formado", self.lexema, linhaAtual)
            erros.append(erro)
        else:
            elemento = Elemento("Numero", self.lexema, linhaAtual)
            elementos.append(elemento)

        self.lexema = ''
        self.estado_erro = True
        return y
            
    def autoCadCaracteres(self, y, linha, elementos, linhaAtual, totalLinhas, erros):
        self.lexema += linha[y]
        if (y < len(linha)):
            y+=1
        while y < len(linha) and (linha[y] in self.alfabeto or linha[y] == "\"") :            
            self.lexema += linha[y]
            if (linha[y] == "\""):                
                self.estado_erro = False
                y+=1
                break
            if (y < len(linha)):
                y+=1
            
        if (self.estado_erro):
            erro = Erro("Cadeia de caractere mal formada", self.lexema, linhaAtual)
            erros.append(erro)
        else:
            elemento = Elemento("Cadeia de caractere", self.lexema, linhaAtual)
            elementos.append(elemento)

        self.lexema = ''
        self.estado_erro = True
        return y

    def autoDelimitador(self, y, linha, elementos, linhaAtual):
        self.lexema += linha[y]
        elemento = Elemento("delimitador", self.lexema, linhaAtual)
        elementos.append(elemento)
        self.lexema = ''
        y += 1
        return y

    def autoComentario(self,y,linha,elementos,linhaAtual,totalLinhas, erros):
        ## Marcador :   // 
        self.lexema += linha[y]
        if linha[y] == '/':
            elemento = Elemento("marcador de comentario", self.lexema, linhaAtual)
            elementos.append(elemento)
            self.lexema = ''
            y = len(linha)
            xy = [0,y]
            return xy

        ## Marcador :   /*
        elif linha[y] == '*':
            y+=1
            elemento = Elemento("marcador de comentario", self.lexema, linhaAtual)
            elementos.append(elemento)
            self.lexema = ''
            ## Procura se o */ está no restante da linha atual
            while y < len(linha):
                if linha[y] == '*':
                    self.lexema = linha[y]
                    y+=1
                    if y != len(linha):
                        ## Marcador :   */
                        if linha[y] == '/':
                            self.lexema += linha[y]
                            elemento = Elemento("marcador de bloco de comentario", self.lexema, linhaAtual)
                            elementos.append(elemento)
                            self.lexema = ''
                            y+=1
                            xy = [0,y]
                            return xy
                else:
                    y+=1            
            ## Procura se o */ está no restante das linhas
            linhasPuladas = 0

            arquivoAux2 = open('input/teste.txt', 'r')
            linha_inicio = linhaAtual
            for x in range(0,linhaAtual):
                linha = arquivoAux2.readline()    

            while linhaAtual < totalLinhas:
                linha = arquivoAux2.readline()
                linhasPuladas += 1
                linhaAtual += 1
                y = 0

                while y < len(linha):
                    if linha[y] == '*':
                        self.lexema = linha[y]
                        y += 1
                        if y != len(linha) and linha[y] == '/':
                            self.lexema += linha[y]
                            elemento = Elemento("marcador de comentario", self.lexema, linhaAtual)
                            elementos.append(elemento)
                            self.lexema = ''
                            linhaAtual += 1
                            y += 1
                            xy = [linhasPuladas,y]
                            return xy
                    else:
                        y += 1


            if linhaAtual == totalLinhas:
                erro = Erro('Bloco de comentário não finalizado', self.lexema, linha_inicio)
                erros.append(erro)
                return [linhasPuladas, y+1]
                

    def autoOpRelacionaisLogicos(self,y,linha,elementos,linhaAtual, erros):
        self.lexema += linha[y]
        if linha[y] == '<' or linha[y] == '>' or linha[y] == '=':
            if (y+1 < len(linha)):
                y+=1           
                if  linha[y] == '=': 
                    self.lexema += linha[y]
                    elemento = Elemento("op relacional", self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                    y += 1
                else:
                    elemento = Elemento("op relacional", self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                return y
            # self.lexema :  < ou > ou = 
            else:
                elemento = Elemento("op relacional", self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
            return y+1
        elif linha[y] == '!':
            if (y+1 < len(linha)):
                y+=1
                if linha[y] == '=':
                    self.lexema += linha[y]
                    elemento = Elemento("op relacional", self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                    y+=1
                else:
                    elemento = Elemento("op logico", self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                return y
            else:
                elemento = Elemento("op logico", self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
                return y+1
        elif linha[y] == '&':
            if (y+1 < len(linha)):
                y+=1
                if linha[y] == '&':
                    self.lexema += linha[y]
                    elemento = Elemento("op logico", self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                    y += 1                    
                else:
                    erro = Erro("Operador logico mal formado", self.lexema, linhaAtual)
                    erros.append(erro)
                    self.lexema = ''
            else:
                erro = Erro("Operador logico mal formado", self.lexema, linhaAtual)
                erros.append(erro)
                self.lexema = ''
                y += 1
            return y
        elif linha[y] == '|':
            if (y+1 < len(linha)):
                y+=1
                if linha[y] == '|':
                    self.lexema += linha[y]
                    elemento = Elemento("op logico", self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                    y += 1                    
                else:
                    erro = Erro("Operador logico mal formado", self.lexema, linhaAtual)
                    erros.append(erro)
                    self.lexema = ''
            else:
                erro = Erro("Operador logico mal formado", self.lexema, linhaAtual)
                erros.append(erro)
                self.lexema = ''
                y += 1
            return y



    def autoOpAritmetico(self,y,linha,elementos,linhaAtual,totalLinhas,erros):
        self.lexema += linha[y]
        if linha[y] == '+':
            y += 1
            if y != len(linha) and linha[y] == '+':
                self.lexema += linha[y]
                elemento = Elemento("op aritmetico", self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
                y += 1
                xy = [0,y]
                return xy
            else:
                elemento = Elemento("op aritmetico", self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
                xy = [0,y]
                return xy
        elif linha[y] == '-':
            y += 1
            if (y < len(linha) and (linha[y] == ' '  or linha[y] in self.digitos)):
                while y < len(linha) and (linha[y] == ' ' or linha[y] in self.digitos):
                    if y < len(linha) and (linha[y] in self.digitos):
                        y = self.autoDigito(y, linha, elementos, linhaAtual, totalLinhas, erros)                    
                        xy = [0, y]
                        return xy
                    self.lexema += linha[y]
                    y += 1
                    
            if y < len(linha) and linha[y] == '-':
                self.lexema += linha[y]
                elemento = Elemento("op aritmetico", self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
                y += 1
                xy = [0,y]
                return xy
            else:
                elemento = Elemento("op aritmetico", self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
                xy = [0,y]
                return xy
        elif linha[y] == '*':
            elemento = Elemento("op aritmetico", self.lexema, linhaAtual)
            elementos.append(elemento)
            self.lexema = ''
            y += 1
            xy = [0,y]
            return xy
        ##Caso seja '/'
        elif linha[y] == '/':
            y += 1
            ##Caso seja '//' ou '/*'
            if y != len(linha):
                if linha[y] == '/' or linha [y] == '*':
                    xy = self.autoComentario(y,linha,elementos,linhaAtual,totalLinhas, erros)
                    return xy
                else:
                    elemento = Elemento("op aritmetico",self.lexema, linhaAtual)
                    elementos.append(elemento)
                    self.lexema = ''
                    xy = [0,y]
                    return xy
            else:
                elemento = Elemento("op aritmetico",self.lexema, linhaAtual)
                elementos.append(elemento)
                self.lexema = ''
                xy = [0,y]
                return xy    
    


