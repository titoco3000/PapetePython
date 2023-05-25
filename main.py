from papete import Papete
from avaliacao import Avaliacao
from movimento import Movimento
import time
import sys

def commands_parser(comandos, entrada:str):
    entrada = entrada.split(' ')
    comando = entrada[0]
    args = entrada[1:]
    possibilidades = [x for x in range(len(comandos))]
    for i in range(len(comando)):
        for n in range(len(possibilidades)-1, -1, -1):
            if len(comandos[possibilidades[n]][0]) <= i or comandos[possibilidades[n]][0][i] != comando[i]:
                del possibilidades[n]
                
    if len(possibilidades)==1:
        try:
            comandos[possibilidades[0]][1](*args)
        except Exception as e:
            print(e)
        return True
    return False

def coleta():
    papete = Papete()
    print('aguardando conexão...',end='')
    while papete.obter_dados()[2] == 'desconectado':
        pass
    print(' conectado')

    papete.neural.iniciar_sessao()
    for j in range(5):
        print(j+1,'/ 5')
        for i in [2,0,1,3,4]:
            input(Movimento(i).descricao())
            for _ in range(10):
                papete.registrar(Movimento(i))
                print('.',end='', flush=True)
                time.sleep(0.1)
            print('')
    papete.neural.salvar_dados()
    papete.neural.zerar_dados()

def jogo():
    print('não implementado')

def avaliacao():
    papete = Papete()
    papete.neural.config_modelo(2, 30, 1.0)
    aval = Avaliacao(papete.neural)
    aval.dez_pastas()
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        commands_parser([
            ('coleta',coleta),
            ('jogo',jogo),
            ('avaliacao',avaliacao)
        ], 
        sys.argv[1])
    else:
        jogo()
