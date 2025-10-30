from __future__ import annotations

from base import Atributos
from inimigo import Inimigo
from personagem import (
    Guerreiro, Mago, Arqueiro, Curandeiro,
    tick_efeitos_inicio_turno,
)
from dado import d6, d20
from missao import MissaoHordas

class Jogo:
    """
    Estrutura base com menus e submenus completos.
    A missão usa d20 para decidir a qualidade da ação e d6 para o dano.
    Exibe HUD com Mana e custos dos especiais e bloqueia execução sem mana.
    """

    def __init__(self) -> None:
        self.personagem = {
            "nome": None,
            "arquetipo": None,   # "Guerreiro", "Mago", "Arqueiro", "Curandeiro"
        }
        self.missao_config = {
<<<<<<< HEAD
            "dificuldade": "Fácil",  # Fácil | Média | Difícil
            "cenario": "Trilha",
=======
            "dificuldade": None,  # Fácil | Média | Difícil
            "cenario": None,     # rótulo ilustrativo
>>>>>>> 5a57af433b761848870b29a404392310ca007c28
        }
        self._ultimo_save = None
        self._ultimo_load = None

    # ======================================================================
    # Construção do herói a partir do arquétipo escolhido no menu
    # ======================================================================
    def _construir_personagem(self):
        arq = (self.personagem.get("arquetipo") or "Guerreiro").strip()
        if arq == "Guerreiro":
            cls, atrib, atk_mag = (
                Guerreiro,
                Atributos(vida=50, ataque=8, defesa=10, mana=5,  vida_max=50),
                0,
            )
        elif arq == "Mago":
            cls, atrib, atk_mag = (
                Mago,
                Atributos(vida=30, ataque=1, defesa=4,  mana=40, vida_max=30),
                10,
            )
        elif arq == "Arqueiro":
            cls, atrib, atk_mag = (
                Arqueiro,
                Atributos(vida=35, ataque=5, defesa=4,  mana=25, vida_max=35),
                3,
            )
        elif arq == "Curandeiro":
            cls, atrib, atk_mag = (
                Curandeiro,
                Atributos(vida=20, ataque=0, defesa=3,  mana=35, vida_max=20),
                8,
            )
        else:
            # Fallback (inclui "Personalizado")
            cls, atrib, atk_mag = (
                Guerreiro,
                Atributos(vida=50, ataque=8, defesa=10, mana=5,  vida_max=50),
                0,
            )
        heroi = cls(self.personagem.get("nome") or "Herói", atrib)
        heroi.ataque_magico = atk_mag  # campo simples para referência futura
        return heroi

    # ======================================================================
    # Tabela de especiais por classe (nome, custo) + HUD
    # ======================================================================
    def _lista_especiais(self, heroi) -> list[tuple[int, str, int]]:
        """Retorna [(id, nome, custo_mana), ...] conforme o arquétipo do herói."""
        if isinstance(heroi, Guerreiro):
            return [
                (1, "Duro na Queda",        0),
                (2, "Determinação Mortal",  2),
                (3, "Golpe Estilhaçador",   0),
            ]
        if isinstance(heroi, Mago):
            return [
                (1, "Paradoxo",             3),
                (2, "Eletrocussão",         2),
                (3, "Explosão Florescente", 8),
            ]
        if isinstance(heroi, Arqueiro):
            return [
                (1, "Aljava da Ruína",      1),
                (2, "Contaminar",           3),
                (3, "Ás na Manga",          7),
            ]
        # Curandeiro
        return [
            (1, "Hemofagia",              4),
            (2, "Transfusão Vital",      30),
            (3, "Resplendor Cósmico",    15),
        ]

    def _mostrar_hud_turno(self, heroi, inimigo) -> None:
        """Imprime HUD com HP/Mana e os especiais com custo/disponibilidade e prévia."""
        mana_atual = getattr(heroi._atrib, "mana", 0)
        print(f"HP {heroi.nome}: {heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")
        print("[1] Ataque normal (usa d20 para decidir a qualidade)")
        especiais = self._lista_especiais(heroi)
        for i, (esp_id, nome, custo) in enumerate(especiais, start=2):
            if mana_atual >= custo:
                previa = mana_atual - custo
                print(f"[{i}] {nome} — custo {custo} mana (ficará: {previa})")
            else:
                print(f"[{i}] {nome} — custo {custo} mana (insuficiente)")
        print("[0] Fugir")

    # ======================================================================
    # Ataque normal com d20 para decidir a qualidade da ação
    # 1–5: péssima (erra) | 6–10: normal | 11–15: boa (+1) | 16–20: excelente (crítico)
    # ======================================================================
    def _ataque_normal_com_d20(self, heroi, inimigo) -> int:
        r = d20()
        print(f"\n[d20] Você rolou: {r}")

        if 1 <= r <= 5:
            print("→ Ação PÉSSIMA: você erra o golpe. Sem dano.")
            return 0

        base = heroi.calcular_dano_base()

        if 6 <= r <= 10:
            dano = base
            print(f"→ Ação NORMAL: dano base = {base}")
        elif 11 <= r <= 15:
            dano = base + 1
            print(f"→ Ação BOA: {base} + 1 = {dano}")
        else:  # 16–20
            dano = base * 2
            print(f"→ Ação EXCELENTE (crítico): {base} x 2 = {dano}")

        efetivo = inimigo.receber_dano(dano)
        if efetivo != dano:
            print(f"(Defesa do alvo reduziu o dano para {efetivo})")
        return efetivo

    # ============================ MENUS ===================================

    def menu_criar_personagem(self) -> None:
        while True:
            print("\n=== Criar Personagem ===")
            print(f"Nome atual: {self.personagem['nome'] or '(não definido)'}")
            print(f"Arquétipo:  {self.personagem['arquetipo'] or '(não definido)'}")
            print("[1] Definir nome")
            print("[2] Escolher arquétipo")
            print("[3] Confirmar criação")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._definir_nome()
            elif op == "2":
                self._escolher_arquetipo()
            elif op == "3":
                self._confirmar_criacao()
            elif op == "9":
                self._ajuda_criar_personagem()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _definir_nome(self) -> None:
        nome = input("Digite o nome do personagem: ").strip()
        if nome:
            self.personagem["nome"] = nome
            print(f"Nome definido: {nome}")
        else:
            print("Nome não alterado.")

    def _escolher_arquetipo(self) -> None:
        print("\nArquétipos disponíveis:")
        print("[1] Guerreiro")
        print("[2] Mago")
        print("[3] Arqueiro")
        print("[4] Curandeiro")
        print("[5] Personalizado (usa Guerreiro por padrão)")
        escolha = input("> ").strip()

        mapa = {
            "1": "Guerreiro",
            "2": "Mago",
            "3": "Arqueiro",
            "4": "Curandeiro",
            "5": "Personalizado",
        }
        arq = mapa.get(escolha)
        if arq:
            self.personagem["arquetipo"] = arq
            print(f"Arquétipo definido: {arq}")
        else:
            print("Opção inválida. Arquétipo não alterado.")

    def _confirmar_criacao(self) -> None:
        if not self.personagem["nome"]:
            print("Defina um nome antes de confirmar a criação.")
            return
        if not self.personagem["arquetipo"]:
            print("Escolha um arquétipo antes de confirmar a criação.")
            return
        print("\nPersonagem criado com sucesso!")
        print(f"Nome: {self.personagem['nome']} | Arquétipo: {self.personagem['arquetipo']}")
        print("(Obs.: atributos base são definidos automaticamente na missão.)")

    def _ajuda_criar_personagem(self) -> None:
        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo para continuar.")
        print("- As escolhas afetam os especiais disponíveis na missão.")

    def menu_missao(self) -> None:
        while True:
            print("\n=== Missão ===")
            print(f"Dificuldade atual: {self.missao_config['dificuldade']}")
            print(f"Cenário atual:     {self.missao_config['cenario']}")
            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print("[3] Pré-visualizar missão")
            print("[4] Iniciar missão (com d20 e d6)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._escolher_dificuldade()
            elif op == "2":
                self._escolher_cenario()
            elif op == "3":
                self._preview_missao()
            elif op == "4":
                self._iniciar_missao_placeholder()
            elif op == "9":
                self._ajuda_missao()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _escolher_dificuldade(self) -> None:
        print("\nDificuldades:")
        print("[1] Fácil")
        print("[2] Média")
        print("[3] Difícil")
        op = input("> ").strip()
        mapa = {"1": "Fácil", "2": "Média", "3": "Difícil"}
        dif = mapa.get(op)
        if dif:
            self.missao_config["dificuldade"] = dif
            print(f"Dificuldade definida: {dif}")
        else:
            print("Opção inválida.")

    def _escolher_cenario(self) -> None:
        print("\nCenários:")
        print("[1] Trilha")
        print("[2] Floresta")
        print("[3] Caverna")
        print("[4] Ruínas")
        op = input("> ").strip()
        mapa = {"1": "Trilha", "2": "Floresta", "3": "Caverna", "4": "Ruínas"}
        cen = mapa.get(op)
        if cen:
            self.missao_config["cenario"] = cen
            print(f"Cenário definido: {cen}")
        else:
            print("Opção inválida.")

    def _preview_missao(self) -> None:
        print("\nPré-visualização da Missão")
        print(f"- Dificuldade: {self.missao_config['dificuldade']}")
        print(f"- Cenário:     {self.missao_config['cenario']}")
        print("- Inimigos e recompensas: (em breve)")

    # ======================== Missão com combate ============================
    def _iniciar_missao_placeholder(self) -> None:
        if not self.personagem["nome"]:
            print("Crie um personagem antes de iniciar uma missão.")
            return

        heroi = self._construir_personagem()
        engine = MissaoHordas(
            heroi=heroi,
            cenario=self.missao_config['cenario'],
            dificuldade=self.missao_config['dificuldade']
        )
        resultado = engine.executar()
        # (opcional) usar resultado.venceu / resultado.encontros_vencidos / resultado.detalhes

        print("\nIniciando missão...")
        print(f"Cenário: {self.missao_config['cenario']} | Dificuldade: {self.missao_config['dificuldade']}")

        heroi = self._construir_personagem()
        inimigo = Inimigo("Goblin", vida=18, ataque=3, defesa=1)

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
                    if isinstance(heroi, Curandeiro):
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
                dano_in = max(0, d6() + inimigo._atrib.ataque - heroi._atrib.defesa)
                heroi.receber_dano(dano_in)
                print(f"{inimigo.nome} ataca e causa {dano_in} de dano. Seu HP: {heroi.barra_hp()} (Mana: {getattr(heroi._atrib, 'mana', 0)})")

            turno += 1

        print("\nMissão finalizada (simulado). Retornando ao menu de Missão...")

    def _ajuda_missao(self) -> None:
        print("\nAjuda — Missão")
        print("- Em 'Iniciar missão', o ataque **normal** usa d20 para decidir a qualidade:")
        print("  1–5: péssima (erra), 6–10: normal, 11–15: boa (+1), 16–20: excelente (crítico).")
        print("- O HUD mostra sua Mana atual, o custo e a **prévia** de mana que ficará.")
        print("- Especiais são bloqueados se a mana for insuficiente.")

    # ========================= SALVAR/CARREGAR ==============================

    def menu_salvar(self) -> None:
        while True:
            print("\n=== Salvar ===")
            print("[1] Salvar rápido (simulado)")
            print("[2] Salvar com nome (simulado)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._salvar_rapido()
            elif op == "2":
                self._salvar_nomeado()
            elif op == "9":
                self._ajuda_salvar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _salvar_rapido(self) -> None:
        self._ultimo_save = "quick_save.json"
        print(f"✔ Salvo (simulado) em: {self._ultimo_save}")

    def _salvar_nomeado(self) -> None:
        nome = input("Nome do arquivo de save (ex.: meu_jogo.json): ").strip() or "save.json"
        self._ultimo_save = nome
        print(f"✔ Salvo (simulado) em: {self._ultimo_save}")

    def _ajuda_salvar(self) -> None:
        print("\nAjuda — Salvar")
        print("- Salvar rápido usa um nome padrão fictício.")
        print("- Salvar nomeado permite escolher um nome fictício.")
        print("- Não há escrita em disco nesta base — é apenas navegação.")

    def menu_carregar(self) -> None:
        while True:
            print("\n=== Carregar ===")
            print("[1] Carregar último save (simulado)")
            print("[2] Carregar por nome (simulado)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._carregar_ultimo()
            elif op == "2":
                self._carregar_nomeado()
            elif op == "9":
                self._ajuda_carregar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _carregar_ultimo(self) -> None:
        if self._ultimo_save:
            self._ultimo_load = self._ultimo_save
            print(f"✔ Carregado (simulado) de: {self._ultimo_load}")
        else:
            print("Nenhum save recente encontrado (simulado).")

    def _carregar_nomeado(self) -> None:
        nome = input("Nome do arquivo para carregar (ex.: meu_jogo.json): ").strip()
        if nome:
            self._ultimo_load = nome
            print(f"✔ Carregado (simulado) de: {self._ultimo_load}")
        else:
            print("Nome não informado.")

    def _ajuda_carregar(self) -> None:
        print("\nAjuda — Carregar")
        print("- O carregamento aqui é apenas ilustrativo (sem leitura real).")
        print("- Use o nome que você “salvou” anteriormente para simular.")
