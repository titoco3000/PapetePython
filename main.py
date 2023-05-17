from papete import Papete
import time



def main():
    papete = Papete()
    minimo = 1000.0
    maximo = 0

    while(True):
        s = papete.obter_sensor()
        minimo = min(minimo,s[0],s[1])
        maximo = max(maximo,s[0],s[1])
        print(maximo,'\t',minimo)
        pass

main()