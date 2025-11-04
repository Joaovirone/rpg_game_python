from __future__ import annotations
from typing import Callable, Dict, List, Optional, Union
from .base import Entidade, Atributos
import random


class Inimigo(Entidade):
    """Inimigo genérico.

    Contém fábricas estáticas para tipos comuns. Cada fábrica retorna
    uma nova instância de Inimigo para evitar compartilhamento de estado.
    """

    def __init__(self, nome: str, vida: int, ataque: int, defesa: int):
        super().__init__(nome, Atributos(vida=vida, ataque=ataque, defesa=defesa, vida_max=vida))

    def esta_vivo(self) -> bool:
        return self._atrib.vida > 0

    @staticmethod
    def ladrao() -> "Inimigo":
        return Inimigo(nome="Ladrão", vida=15, ataque=10, defesa=10)

    @staticmethod
    def goblin() -> "Inimigo":
        return Inimigo(nome="Goblin", vida=20, ataque=10, defesa=5)

    @staticmethod
    def golem() -> "Inimigo":
        return Inimigo(nome="Golem", vida=35, ataque=20, defesa=25)

    @staticmethod
    def elfo() -> "Inimigo":
        return Inimigo(nome="Elfo", vida=15, ataque=10, defesa=10)

    @staticmethod
    def dragao() -> "Inimigo":
        return Inimigo(nome="Dragão", vida=40, ataque=30, defesa=35)


# Dicionário de fábricas: nome legível -> função que cria nova instância
lista_inimigos: Dict[str, Callable[[], Inimigo]] = {
    "Ladrão": Inimigo.ladrao,
    "Goblin": Inimigo.goblin,
    "Golem": Inimigo.golem,
    "Elfo": Inimigo.elfo,
    "Dragão": Inimigo.dragao,
}


def inimigo_aleatorio(count: int = 1, pool: Optional[Dict[str, Callable[[], Inimigo]]] = None, unique: bool = False) -> Union[Inimigo, List[Inimigo]]:
    """Retorna um ou mais inimigos aleatórios.

    Args:
        count: número de inimigos a retornar. Se 1, retorna uma única instância.
        pool: dicionário nome -> fábrica. Por padrão usa ENEMIGOS_FACTORIES.
        unique: se True, garante inimigos com nomes distintos (erro se count > len(pool)).

    Retorna:
        Uma instância de Inimigo quando count == 1, ou uma lista de instâncias quando count > 1.
    """
    if count < 1:
        raise ValueError("count deve ser >= 1")

    pool = pool or lista_inimigos
    nomes = list(pool.keys())

    if unique:
        if count > len(nomes):
            raise ValueError("count maior que número de inimigos únicos disponíveis no pool")
        escolhidos = random.sample(nomes, count)
    else:
        escolhidos = [random.choice(nomes) for _ in range(count)]

    instancias = [pool[n]() for n in escolhidos]
    return instancias[0] if count == 1 else instancias


def inimigos_para_dicionario(pool: Optional[Dict[str, Callable[[], Inimigo]]] = None) -> Dict[str, Inimigo]:
    """Retorna um dicionário nome -> instância (fresh) para todas as fábricas no pool."""
    pool = pool or lista_inimigos
    return {nome: fabrica() for nome, fabrica in pool.items()}


__all__ = ["Inimigo", "lista_inimigos", "inimigo_aleatorio", "inimigos_para_dicionario"]