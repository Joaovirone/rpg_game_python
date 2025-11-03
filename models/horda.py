"""
Criado o arquivo horda.py para não aplicar no missao.py e ficar bagunçado
o objetivo do horda é gerar quantidade de inimigos
de acordo com a dificuldade e o cenario escolhido
"""

from random import choice
from models.inimigo import Inimigo  # ajuste o caminho se necessário


def generate_horde(cenario: str, dificuldade: str) -> list[Inimigo]:
    tipos = []
    if cenario == "Caverna":
        tipos = [Inimigo.ladrao, Inimigo.goblin, Inimigo.golem]
    elif cenario == "Floresta":
        tipos = [Inimigo.elfo, Inimigo.goblin]
    elif cenario == "Castelo":
        tipos = [Inimigo.goblin, Inimigo.golem, Inimigo.dragao]
    else:
        tipos = [Inimigo.goblin]

    # quantidade de inimigos pela dificuldade
    qtd = {"Fácil": 3, "Médio": 5, "Difícil": 7}.get(dificuldade, 3)

    horda = [choice(tipos)() for _ in range(qtd)]
    return horda