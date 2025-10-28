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

    def __init__(self, titulo: str, inimigo: Inimigo):
        self.titulo = titulo
        self.inimigo = inimigo

    def executar(self, p: Personagem) -> ResultadoMissao:
        """
        Placeholder de execução da missão:
        - Exibe um resumo e retorna um resultado simulado.
        - Sem combate real neste estágio.
        """
        print(f"\n=== Missão: {self.titulo} ===")
        print(f"Inimigo: {self.inimigo.nome} (HP: {self.inimigo._atrib.vida})")
        print(f"Mecânica de combate será implementada futuramente para {p.nome}.")
        print("Retornando ao menu...\n")
        return ResultadoMissao(venceu=False, detalhes="Execução placeholder; sem combate.")
