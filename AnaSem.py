import sys
import os.path
import string
from Models import *

class AnaSem():
    metodos = []
    procedimentos = []
    constantes = []
    variaveis = []
    estruturas = []
    typedefs = []

    def analisa(self):
        arquivos = os.listdir('input')        
        for arquivo in arquivos:
            arquivo = open('input/' + arquivo, 'r')
            #codigo