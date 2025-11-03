from __future__ import annotations
from .base import Entidade, Atributos


class Inimigo(Entidade):
    """
    Inimigo genérico.
    Sem IA/variações — apenas o contêiner para atributos básicos.
    """

    def __init__(self, nome: str, vida: int, ataque: int, defesa: int):
        super().__init__(nome, Atributos(vida=vida, ataque=ataque, defesa=defesa, vida_max=vida))

    def ladrao()-> Inimigo:
        return Inimigo(nome="Ladrão", vida=15, ataque=10, defesa=10)
    
    def goblin()-> Inimigo:
        return Inimigo(nome="Goblin", vida=20, ataque=10, defesa=5)
    
    def golem()-> Inimigo:
        return Inimigo(nome="Golem", vida=35, ataque=20, defesa=25)
    
    def elfo()-> Inimigo:
        return Inimigo(nome="Elfo", vida=15, ataque=10, defesa=10)
    
    def dragao()-> Inimigo:
        return Inimigo("dragao", vida=40, ataque=30, defesa=35)