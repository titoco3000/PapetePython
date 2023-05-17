import random
import numpy as np
import csv
import typing
import tensorflow.python.keras as keras
import os
import math
import time
import calendar
from movimento import Movimento

class Neural:
    movimentos = ['Dorsiflexao', 'Flexao', 'Repouso', 'Eversao', 'Inversao']
    
    def __init__(self) -> None:
        self.movimentos_registrados = []
        self.sessao = 0
    
    def normalizar(pitch:float, roll: float, pe_esq:bool):
        return (
            (pitch+360.0)/720.0,
            (roll+360.0)/720.0,
            1.0 if pe_esq else 0.0
        )
    
    def registrar(self, pitch:float,roll:float,pe_esq:bool, movimento:Movimento):
        self.movimentos_registrados.append((pitch,roll,pe_esq,movimento))
        return len(self.movimentos_registrados)
    
    def deregistrar(self):
        L = len(self.movimentos_registrados)
        if L>0:
            L-=1
            del self.movimentos_registrados[L]
        return L

    def zerar_dados(self):
        self.movimentos_registrados = []
        return 0
    
    def salvar_dados(self,destino:str, modo='a'):
        if not os.path.isfile(destino):
            arquivo = open(destino, 'w')
            arquivo.write('pitch,roll,lado,movimento,sessao')
            arquivo.close()
        arquivo = open(destino, modo)
        for e in self.movimentos_registrados:
            arquivo.write(f"\n{e[0]};{e[1]};{'E' if e[2] else 'D'};{e[3].nome_externo()};{self.sessao}")
        arquivo.close()    

    def iniciar_sessao(self):
        self.sessao = calendar.timegm(time.gmtime())

    def config_modelo(self,qtd_camadas_ocultas:int, nodes_por_camada:int, gamma:float):
        custom_activation = lambda x: 1 / (1 + math.e ** (-gamma * x))
        self.modelo = keras.Sequential()
        self.modelo.add(keras.layers.Dense(nodes_por_camada, input_shape=(3,), activation=custom_activation))
        for i in range(1,qtd_camadas_ocultas):
            self.modelo.add(keras.layers.Dense(nodes_por_camada, activation=custom_activation))
        self.modelo.add(keras.layers.Dense(5, activation=custom_activation))
        self.modelo.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    def treinar(self, entradas:np.ndarray, saidas:np.ndarray, epochs=300):
        return self.modelo.fit(entradas, saidas, epochs=epochs, batch_size=200, verbose=0).history['accuracy']

    def salvar_modelo(self, endereco:str = 'modelo_papete'):
        self.modelo.save(endereco)

    def transferir_aprendizado(self,entradas:np.ndarray = np.array([]), saidas:np.ndarray=np.array([]), epochs=180):
        layer_names = [layer.name for layer in self.modelo.layers]
        # bloqueia treinamento das primeiras camadas
        for layer_name in layer_names[:-1]:
            self.modelo.get_layer(layer_name).trainable = False

        if len(entradas)==0 or len(saidas)==0:
            entradas_treino = []
            saidas_treino = []
            for i in range(len(self.movimentos_registrados)):
                        entradas_treino.append(Neural.reshape(self.movimentos_registrados[i][0], self.movimentos_registrados[i][1]))
                        saidas_treino.append(Neural.saidas_movimentos[self.movimentos_registrados[i][2]])
            entradas_treino = np.array(entradas_treino)
            saidas_treino = np.array(saidas_treino)
        else:
            entradas_treino = entradas
            saidas_treino = saidas
        
        historico = self.modelo.fit(entradas_treino, saidas_treino, epochs=epochs,batch_size=30,verbose=0).history['accuracy']

        # libera treinamento das primeiras camadas
        for layer_name in layer_names[:-1]:
            self.modelo.get_layer(layer_name).trainable = False
        
        return historico
    
    def prever(self,pitch:float,roll:float,pe_esq:bool):
        network_input = Neural.normalizar(pitch, roll,pe_esq).reshape(-1, 3)
        nn_output = self.modelo.predict(network_input, verbose=0)[0]
        somatorio = 0.0
        for i in range(5):
            somatorio += nn_output[i]
        for i in range(5):
            nn_output[i] /= somatorio
        return nn_output
    
    #retorna tres ndarrays: entradas, saidas e sessoes
    def carregar_dados(arquivo: str, embaralhar = True) ->typing.Tuple[np.ndarray,np.ndarray, np.ndarray]:
        todas_entradas = []
        todas_saidas = []
        sessoes = []

        with open(arquivo) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # pula o cabeçalho
            next(csv_reader)
            for row in csv_reader:
                # lê e normaliza os valores
                if len(row) > 0:
                    item = row[:4]
                    item = Neural.normalizar(float(item[0]), float(item[1]),item[2] == 'E')

                    expected = Movimento(item[3]).saida()
                    
                    if len(row)>5:
                        sessoes.append(int(row[4]))
                    else:
                        sessoes.append(0)

                    todas_entradas.append(item)
                    todas_saidas.append(expected)

        if embaralhar:
            random.seed(0)
            random.shuffle(todas_entradas)
            random.seed(0)
            random.shuffle(todas_saidas)
            random.seed(0)
            random.shuffle(sessoes)

        return np.array(todas_entradas), np.array(todas_saidas), np.array(sessoes)

class Avaliacao():
    def __init__(self, neural:Neural):
        self.neural = neural
        self.arquivo_de_referencia = 'papete.csv'
    #funcoes estaticas
    #retorna (outra_parte, parte_k)
    def k_pastas(lista: np.ndarray, k: int, selecionada: int = 0):
        tamanho_pasta = len(lista) // k

        p1 = lista[:((selecionada+1) * tamanho_pasta)]
        p2 = lista[((selecionada + 1) * tamanho_pasta):]
        if len(p1) == 0:
            p = np.array(p2)
        elif len(p2) == 0:
            p = np.array(p1)
        else:
            p = np.concatenate((lista[:(selecionada * tamanho_pasta)], lista[((selecionada + 1) * tamanho_pasta):]))

        return p, np.array(lista[selecionada * tamanho_pasta:(selecionada + 1) * tamanho_pasta])
    