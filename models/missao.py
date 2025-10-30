from __future__ import annotations
from dataclasses import dataclass
from .personagem import Personagem
from .inimigo import Inimigo


@dataclass
class ResultadoMissao:
    """Resultado ilustrativo (placeholder)."""
    venceu: bool = False
    detalhes: str = "Missão simulada."


class Missao:
    """
    Estrutura da missão sem a mecânica de combate.
    Mantém a assinatura para futura integração com o jogo completo.
    """
    missao =
    def __init__(self, titulo: str, inimigo: Inimigo):
        self.missoes = [{
            "titulo":missao_1,
            "titulo":missao_2,
            "titulo":missao_3,
            "titulo":missao_4,
            "titulo":missao_5,
        }]
        self.missao_atual = 0;
        self.inimigo = inimigo


    def executar(self, p: Personagem) -> ResultadoMissao:
        """
        Placeholder de execução da missão:
        - Exibe um resumo e retorna um resultado simulado.
        - Sem combate real neste estágio.
        """
        missao = self.missoes_atual = [missao_atual]
        titulo = missao["titulo"]

        if self.missao_atual >= len(self.missao):
        print("\nAs missões foram concluídas")
        return
        
        print(f"\n=== Missão: {self.missao_atual + 1}:{titulo} ===")
        print(f"Inimigo: {self.inimigo.nome} (HP: {self.inimigo._atrib.vida})")
        print(f"Personagem: {self.Personagem.nome} está pronto para lutar!")
        print(f"Mecânica de combate será implementada futuramente para {p.nome}.")
        print("Retornando ao menu...\n")
        return ResultadoMissao(venceu=False, detalhes="Execução placeholder; sem combate.")

    def missao_1(self, titulo:str)
        self.titulo = "Matar Ladrões"
    def missao_2(self, titulo:str)
        self.titulo = "Matar Goblins"
    def missao_3(self, titulo:str)
        self.titulo = "Matar Golens"
    def missao_4(self, titulo:str)
        self.titulo = "Matar Elfos"
    def missao_5(self, titulo:str)
        self.titulo = "Matar Dragões"



