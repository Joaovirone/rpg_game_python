from __future__ import annotations
from dataclasses import dataclass
from .personagem import Personagem
from .inimigo import Inimigo #generate_horde
from dado import rolar_d20, rolar_d6
from .horda import generate_horde


@dataclass
class ResultadoMissao:
    venceu: bool
    encontros_vencidos: int
    detalhes: str = ""



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

class Missao:
    """
    Estrutura da missão sem a mecânica de combate.
    Mantém a assinatura para futura integração com o jogo completo.
    """

    
    def __init__(self, inimigo: Inimigo, cenario: str, dificuldade: str, heroi: Personagem):
        self.inimigo = inimigo
        self.cenario = cenario
        self.dificuldade = dificuldade
        self.heroi = heroi

        self.missoes = [
            self.missao_1(),
            self.missao_2(),
            self.missao_3(),
            self.missao_4(),
            self.missao_5()
        ]
        self.missao_atual = 0


    def missao_1(self)-> dict:
        return "Matar Ladrões"
    def missao_2(self)-> dict:
        return "Matar Goblins"
    def missao_3(self)-> dict:
        return "Matar Golens"
    def missao_4(self)-> dict:
        return "Matar Elfos"
    def missao_5(self)-> str:
        return "Matar Dragões"

    def _mostrar_hud(self, inimigo: Inimigo) -> None:
        mana_atual = getattr(self.heroi._atrib, "mana", 0)
        print(f"HP {self.heroi.nome}: {self.heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")

    def mana_classe(self) -> None:
        custo_basico = {"Guerreiro": 0, "Mago": 1, "Arqueiro": 0, "Curandeiro": 0}.get(
            self.heroi.__class__.__name__, 0
        )
        mana_atual = getattr(self.heroi._atrib, "mana", 0)
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
                                self.heroi.habilidade_especial(_id, aliados=[])
                            elif _id == 2:
                                self.heroi.habilidade_especial(_id, aliado=None)
                            elif _id == 3:
                                self.heroi.habilidade_especial(_id)
                            elif _id == 4:
                                dano_causado = self.heroi.habilidade_especial(4, alvo=inimigo)
                        else:
                            dano_causado = self.heroi.habilidade_especial(_id, alvo=inimigo)

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
                    dano_in = max(0, rolar_d6() + inimigo._atrib.ataque)

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





    """
    # ======================== Missão com combate ============================
    def _iniciar_missao_placeholder(self, inimigo=None) -> None:
        self.logger.info("Iniciando a missão.")
        if not self.personagem["nome"] or not self.personagem["arquetipo"]:
            print("Crie um personagem antes de iniciar uma missão.")
            return

        # Cria inimigo se não informado
        if inimigo is None:
            inimigo = Inimigo.goblin()

        # Pega os dados do personagem criado no menu
        nome_arquetipo = self.personagem["arquetipo"]
        nome_heroi = self.personagem["nome"]

        heroi = self.mostrar_personagem(nome_arquetipo, nome_heroi)
        engine = Missao(
            inimigo= inimigo,
            heroi=heroi,
            cenario=self.missao_config['cenario'],
            dificuldade=self.missao_config['dificuldade']
        )




        resultado = engine.executar()
        # (opcional) usar resultado.venceu / resultado.encontros_vencidos / resultado.detalhes

        print("\nIniciando missão...")
        print(f"Cenário: {self.missao_config['cenario']} | Dificuldade: {self.missao_config['dificuldade']}")

        heroi = self._mostrar_personagem()
        inimigo = Inimigo.goblin()

        turno = 1
        while heroi.esta_vivo() and inimigo.esta_vivo():
            print(f"\n=== Turno {turno} ===")

            # Efeitos no início do turno do herói (veneno/eletro/etc.)
            dano_tick_heroi = heroi.inicio_turno()
            if dano_tick_heroi:
                print(f"(Efeitos) {heroi.nome} sofre {dano_tick_heroi} de dano | {heroi.barra_hp()}")

            if heroi.efeitos.get("nao_pode_atacar", 0) > 0:
                print(f"{heroi.nome} está impossibilitado de agir neste turno!")
            else:
                # HUD com Mana + custos dos especiais (+ prévia)
                self._mostrar_hud_turno(heroi, inimigo)
                acao = input("> ").strip()

                dano_causado = 0
                bloqueado = False

                # Bloqueio prévio para especiais (teclas 2..4) com mana insuficiente
                if acao in {"2", "3", "4"}:
                    esp_idx = int(acao) - 2  # 0,1,2
                    especiais = self._lista_especiais(heroi)
                    if 0 <= esp_idx < len(especiais):
                        _, nome_esp, custo_esp = especiais[esp_idx]
                        mana_atual = getattr(heroi._atrib, "mana", 0)
                        if mana_atual < custo_esp:
                            print(f"Mana insuficiente para {nome_esp} ({mana_atual}/{custo_esp}). Escolha outra ação.")
                            bloqueado = True  # impede a execução do especial

                # Execução das ações
                if acao == "1":
                    dano_causado = self._ataque_normal_com_d20(heroi, inimigo)
                elif acao == "2" and not bloqueado:
                    dano_causado = heroi.usar_especial(1, alvo=inimigo)
                elif acao == "3" and not bloqueado:
                    dano_causado = heroi.usar_especial(2, alvo=inimigo)
                elif acao == "4" and not bloqueado:
                    if isinstance(heroi, Personagem.Curandeiro):
                        print("(Curandeiro esp3 cura aliados — ignorado no 1x1)")
                        dano_causado = 0
                    else:
                        dano_causado = heroi.usar_especial(3, alvo=inimigo)
                elif acao == "0":
                    print("Você recuou da luta!")
                    break
                else:
                    if not bloqueado:
                        print("Ação inválida.")

                if dano_causado:
                    print(f"Você causou {dano_causado} de dano. HP do {inimigo.nome}: {inimigo.barra_hp()}")

            if not inimigo.esta_vivo():
                print(f"\n{inimigo.nome} foi derrotado!")
                break

            # Início do turno do inimigo — efeitos nele (veneno/eletro etc.)
            dano_tick_ini = tick_efeitos_inicio_turno(inimigo)
            if dano_tick_ini:
                print(f"(Efeitos) {inimigo.nome} sofre {dano_tick_ini} de dano | {inimigo.barra_hp()}")
            if not inimigo.esta_vivo():
                print(f"\n{inimigo.nome} caiu pelos efeitos!")
                break

            if inimigo.efeitos.get("nao_pode_atacar", 0) > 0:
                print(f"{inimigo.nome} está atordoado e não ataca.")
            else:
                # Ataque simples do inimigo: d6 + ataque - defesa do herói
                dano_in = max(0, rolar_d6() + inimigo._atrib.ataque - heroi._atrib.defesa)
                heroi.receber_dano(dano_in)
                print(f"{inimigo.nome} ataca e causa {dano_in} de dano. Seu HP: {heroi.barra_hp()} (Mana: {getattr(heroi._atrib, 'mana', 0)})")

            turno += 1

        print("\nMissão finalizada (simulado). Retornando ao menu de Missão...")
        """

