from __future__ import annotations
from dataclasses import dataclass
from .personagem import Personagem, Curandeiro, tick_efeitos_inicio_turno
from .inimigo import Inimigo, generate_horde
from .dado import d6


@dataclass
class ResultadoMissao:
    venceu: bool
    encontros_vencidos: int
    detalhes: str = ""


<<<<<<< HEAD
class MissaoHordas:
    def __init__(self, heroi: Personagem, cenario: str, dificuldade: str):
        self.heroi = heroi
        self.cenario = cenario
        self.dificuldade = dificuldade

    # 4 habilidades por classe (além do ataque básico)
    def _lista_especiais(self) -> list[tuple[int, str, int]]:
        n = self.heroi.nivel
        base = {
            "Guerreiro": [
                (1, "Execução Pública", 7),
                (2, "Perseverança", 0),
                (3, "Golpe Trovejante", 1),
                (4, "Lâmina Ínfera", 2),
            ],
            "Mago": [
                (1, "Colapso Minguante", 15),
                (2, "Descarnar", 20),
                (3, "Distorção no Tempo", 0),
                (4, "Empurrão Sísmico", 8),
            ],
            "Arqueiro": [
                (1, "Curingas", 8),
                (2, "Cortes Certeiros", 6),
                (3, "Estilo do Caçador", 10),
                (4, "Marca Fatal", 10),
            ],
            "Curandeiro": [
                (1, "Capítulo Final", 3),
                (2, "Semente Engatilhada", 5),
                (3, "Ventos Revigorantes", 15),
                (4, "Golpe de Misericórdia", 0),
            ],
        }
        todos = base.get(self.heroi.__class__.__name__, [])
        desbloq = 1
        if n >= 2: desbloq += 1
        if n >= 4: desbloq += 1
        if n >= 6: desbloq += 1
        if n >= 8: desbloq += 1
        return todos[:desbloq]
=======
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
>>>>>>> 5a57af433b761848870b29a404392310ca007c28


    def _mostrar_hud(self, inimigo: Inimigo) -> None:
        mana_atual = getattr(self.heroi._atrib, "mana", 0)
        print(f"HP {self.heroi.nome}: {self.heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")


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


<<<<<<< HEAD
        custo_basico = {"Guerreiro": 0, "Mago": 1, "Arqueiro": 0, "Curandeiro": 0}.get(
            self.heroi.__class__.__name__, 0
        )
        print(f"[1] Ataque básico — custo {custo_basico} "
              f"({'ficará: ' + str(mana_atual - custo_basico) if mana_atual >= custo_basico else 'insuf.'})")

        for i, (_, nome, custo) in enumerate(self._lista_especiais(), start=2):
            if mana_atual >= custo:
                print(f"[{i}] {nome} — custo {custo} (ficará: {mana_atual - custo})")
            else:
                print(f"[{i}] {nome} — custo {custo} (insuficiente)")
        print("[0] Fugir")

    def executar(self) -> ResultadoMissao:
        print("\nIniciando missão...")
        print(f"Cenário: {self.cenario} | Dificuldade: {self.dificuldade}")

        horda = generate_horde(self.cenario, self.dificuldade)
        encontros_vencidos = 0

        for idx, inimigo in enumerate(horda, start=1):
            print(f"\n=== Encontro {idx}/{len(horda)} — {inimigo.nome} ===")
            turno = 1

            while self.heroi.esta_vivo() and inimigo.esta_vivo():
                print(f"\n--- Turno {turno} ---")

                # controle de turno do herói (para Execução Pública)
                self.heroi.efeitos["turnos"] = self.heroi.efeitos.get("turnos", 0) + 1

                # efeitos no herói
                dano_tick = self.heroi.inicio_turno()
                if dano_tick:
                    print(f"(Efeitos) {self.heroi.nome} sofre {dano_tick} | {self.heroi.barra_hp()}")

                if self.heroi.efeitos.get("nao_pode_atacar", 0) > 0:
                    print(f"{self.heroi.nome} está impossibilitado de agir neste turno!")
                else:
                    self._mostrar_hud(inimigo)
                    acao = input("> ").strip()

                    dano_causado = 0
                    bloqueado = False

                    custo_basico = {"Guerreiro": 0, "Mago": 1, "Arqueiro": 0, "Curandeiro": 0}.get(
                        self.heroi.__class__.__name__, 0
                    )
                    mana_atual = getattr(self.heroi._atrib, "mana", 0)

                    # bloqueio por mana
                    if acao == "1":
                        if mana_atual < custo_basico:
                            print(f"Mana insuficiente para Ataque Básico ({mana_atual}/{custo_basico}).")
                            bloqueado = True
                    elif acao in {"2", "3", "4", "5"}:
                        esp_idx = int(acao) - 2
                        especs = self._lista_especiais()
                        if 0 <= esp_idx < len(especs):
                            _id, nome, custo = especs[esp_idx]
                            if mana_atual < custo:
                                print(f"Mana insuficiente para {nome} ({mana_atual}/{custo}).")
                                bloqueado = True

                    # execução
                    if acao == "1" and not bloqueado:
                        dano_causado = self.heroi.ataque_basico(inimigo)
                    elif acao in {"2", "3", "4", "5"} and not bloqueado:
                        esp_idx = int(acao) - 2
                        especs = self._lista_especiais()
                        _id, nome, _c = especs[esp_idx]

                        if isinstance(self.heroi, Curandeiro):
                            if _id == 1:
                                self.heroi.usar_especial(1, aliados=[])
                            elif _id == 2:
                                self.heroi.usar_especial(2, aliado=None)
                            elif _id == 3:
                                self.heroi.usar_especial(3)
                            elif _id == 4:
                                dano_causado = self.heroi.usar_especial(4, alvo=inimigo)
                        else:
                            dano_causado = self.heroi.usar_especial(_id, alvo=inimigo)

                    elif acao == "0":
                        print("Você recuou da missão!")
                        return ResultadoMissao(False, encontros_vencidos, "Fugiu da missão.")
                    else:
                        if not bloqueado:
                            print("Ação inválida.")

                    if dano_causado:
                        print(f"Você causou {dano_causado}. HP do {inimigo.nome}: {inimigo.barra_hp()}")

                if not inimigo.esta_vivo():
                    print(f"{inimigo.nome} foi derrotado!")
                    encontros_vencidos += 1
                    break

                # efeitos no inimigo
                dano_tick_i = tick_efeitos_inicio_turno(inimigo)
                if dano_tick_i:
                    print(f"(Efeitos) {inimigo.nome} sofre {dano_tick_i} | {inimigo.barra_hp()}")
                if not inimigo.esta_vivo():
                    print(f"{inimigo.nome} caiu pelos efeitos!")
                    encontros_vencidos += 1
                    break

                if inimigo.efeitos.get("nao_pode_atacar", 0) > 0:
                    print(f"{inimigo.nome} está atordoado e não ataca.")
                else:
                    # NÃO subtrair defesa aqui; Entidade.receber_dano aplica defesa.
                    dano_in = max(0, d6() + inimigo._atrib.ataque)

                    # Invulnerável anula dano direto (checado na missão)
                    if self.heroi.efeitos.get("invulneravel_turnos", 0) > 0:
                        print(f"{self.heroi.nome} está invulnerável e não sofre dano.")
                        dano_in = 0

                    aplicado = self.heroi.receber_dano(dano_in)
                    print(f"{inimigo.nome} causa {aplicado}. Seu HP: {self.heroi.barra_hp()} (Mana: {getattr(self.heroi._atrib, 'mana', 0)})")

                    # Reflexão
                    if aplicado > 0 and self.heroi.efeitos.get("refletir_dano_turnos", 0) > 0:
                        refle = inimigo.receber_dano(aplicado)
                        print(f"Ventos Revigorantes refletem {refle} ao {inimigo.nome}! HP: {inimigo.barra_hp()}")

                turno += 1

            if not self.heroi.esta_vivo():
                print("\nVocê foi derrotado... Missão falhou.")
                return ResultadoMissao(False, encontros_vencidos, "Derrotado nas hordas.")

        print("\nParabéns! Você venceu todas as hordas da missão!")
        return ResultadoMissao(True, encontros_vencidos, "Vitória!")

=======
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




>>>>>>> 5a57af433b761848870b29a404392310ca007c28