import numpy as np

class Movimento:
    __nomes_interno = ['Dorsiflexao', 'Flexao', 'Repouso', 'Eversao', 'Inversao']
    __nomes_externo = ['Dorsiflexão', 'Flexão plantar', 'Repouso', 'Eversão', 'Inversão']
    __descricoes = ['Dorsiflexão: levantar ponta do pé','Flexão plantar: levantar calcanhar','Repouso: apoiar sola totalmente no chão','Eversão: pés inclinados para dentro ','Inversão: pés inclinados para fora']
    __saidas = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0]
    ]

    def __init__(self, original = 0):
        if type(original == Movimento):
            self.id = original.id
        elif type(original == int):
            if 0>=id>=5:
                self.id = original.id
            else:
                raise Exception(f"index de movimento deve ser entre 0 e 5 ({original})")
        elif type(original == str):
            try:
                self.id = Movimento.__nomes_interno.index(original)
            except ValueError:
                try:
                    self.id = Movimento.__nomes_externo.index(original)
                except ValueError:
                    try:
                        Movimento(int(original))
                    except ValueError:
                        raise Exception(f"str não reconhecido como movimento ({original})")
        elif type(original) == np.ndarray and len(original) == 5:
            self.id == np.argmax(original)
        else:
            raise Exception(f"tipo não reconhecido como movimento ({type(original)})")

    def nome_interno(self) -> str:
        return Movimento.__nomes_interno[self.id]
    
    def nome_externo(self) -> str:
        return Movimento.__nomes_externo[self.id]

    def descricao(self) -> str:
        return Movimento.__descricoes[self.id]
    
    def descricao(self) -> int:
        return self.id
    
    def saida(self) -> list:
        return Movimento.__saidas[self.id]
