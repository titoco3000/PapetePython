import random
import numpy as np
import typing
import tensorflow.python.keras as keras
from movimento import Movimento
from neural import Neural

class Avaliacao():
    def __init__(self, neural:Neural):
        self.neural = neural
        self.arquivo_de_referencia = 'papete.csv'

    def dez_pastas(self):
        entradas,saidas,sessoes =  Neural.carregar_dados(self.arquivo_de_referencia)
        
        novo_shape = (len(entradas)-(len(entradas)%10),3)
        #limita tamanho para multiplo de 10
        entradas.resize(novo_shape)
        saidas.resize(novo_shape)
        sessoes.resize(novo_shape)

        tamanho_bloco = int(len(entradas)/10)
        tamanho_treino = int(novo_shape[0]*0.9)
        self.neural.modelo.save_weights('pesos_iniciais.h5')

        resultados = []
        acertos = 0

        for i in range(10):
            print(i+1,'/ 10')
            entrada_treino = np.delete(np.split(entradas,10), i, axis=0)
            entrada_treino.resize((tamanho_treino,3))
            
            saida_treino = np.delete(np.split(saidas,10), i, axis=0)
            saida_treino.resize((tamanho_treino,5))

            entrada_teste = entradas[i*tamanho_bloco:(i+1)*tamanho_bloco]
            saida_teste = saidas[i*tamanho_bloco:(i+1)*tamanho_bloco]
            
            self.neural.treinar(entrada_treino,saida_treino)

            output = self.neural.modelo.predict(entrada_treino,verbose=0)
            for j in range(len(output)):
                # print(output[j],' =?= ',saida[j])
                resultados.append(output[j])
                if np.argmax(saida_teste[j]) == np.argmax(output[j]):
                    acertos+=1
            # limpa a rede
            self.neural.modelo.load_weights('pesos_iniciais.h5')

        print(acertos)
        print((len(saidas),len(resultados)))
        Avaliacao.matriz_de_confusao(saidas,resultados)

    def matriz_de_confusao(esperadas:np.array, obtidas:np.array, endereco='matriz.png', titulo='matriz de confusão'):
        from sklearn.metrics import confusion_matrix
        import matplotlib.pyplot as plt
        import itertools
        
        y_pred = np.argmax(esperadas, axis=1)
        y_test = np.argmax(obtidas, axis=1)
        
        cm = confusion_matrix(y_test, y_pred)

        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title(titulo)
        plt.colorbar()
        tick_marks = np.arange(len(Neural.movimentos))
        plt.xticks(tick_marks, Neural.movimentos, rotation=45)
        plt.yticks(tick_marks, Neural.movimentos)

        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, cm[i, j],
                    horizontalalignment="center",
                    color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.gcf().subplots_adjust(bottom=0.2)
        plt.xlabel('Valor real')
        plt.ylabel('Valor previsto')
        plt.savefig(endereco)
        plt.clf()