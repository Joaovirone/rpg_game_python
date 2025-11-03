from __future__ import annotations
import json
import os
import utils.logger as logger
from models.base import Atributos, Entidade
from models.inimigo import Inimigo
from models.personagem import Personagem, Entidade, Curandeiro, Arqueiro, Mago, Guerreiro
from dado import rolar_d6, rolar_d20
from models.missao import MissaoHordas, Missao

class Jogo:
    """
    Estrutura base com menus e submenus completos.
    A missão usa d20 para decidir a qualidade da ação e d6 para o dano.
    Exibe HUD com Mana e custos dos especiais e bloqueia execução sem mana.
    """

    def __init__(self) -> None:

        logger.Logger.self = logger.Logger()
        logger.Logger.self.info("Iniciando o jogo...")
        
        self.personagem = {
            "nome": None,
            "arquetipo": None,   # "Guerreiro", "Mago", "Arqueiro", "Curandeiro"
        }

        self.arquetipos = {
            "Guerreiro": Guerreiro,
            "Mago": Mago,
            "Arqueiro": Arqueiro,
            "Curandeiro": Curandeiro
        }

        self.missao_config = {
            
            "dificuldade": None,  # Fácil | Média | Difícil
            "cenario": None,     # rótulo ilustrativo
            "missao": None,      # rótulo da missão

        }
        self._ultimo_save = None
        self._ultimo_load = None

        #Caminha que é feito para os saves irem pra pasta saver
        self.save_dir = os.path.join(os.getcwd(), "saves")
        os.makedirs(self.save_dir, exist_ok=True) # garante que o diretório exista

    # ======================================================================
    # Construção do herói a partir do arquétipo escolhido no menu
    # ======================================================================

    
    # ======================================================================
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
        r = rolar_d20()
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
        self.logger.info(f"Nome do personagem sendo definido.")
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
            return arq


        else:
            print("Opção inválida. Arquétipo não alterado.")
            return None



    #AQUI estou tentando fazer o personagem escolhido aparecer os atributos deles vida, manda e etc (não consegui ainda)

    def mostrar_personagem(self, nome_arquetipo: str, nome_heroi: str):
        """
        Cria e retorna um personagem do arquétipo escolhido, exibindo preview das estatísticas.
        """
        # Pega a classe do arquétipo
        classe_arquetipo = self.arquetipos.get(nome_arquetipo)
        if not classe_arquetipo:
            print("Arquétipo não encontrado.")
            return None

        # Cria o personagem (atributos já são definidos no construtor do arquétipo)
        personagem = classe_arquetipo(nome_heroi)

        # Mostra estatísticas
        a = personagem._atrib
        print(f"\nPreview de {personagem.nome}:")
        print(f"🩸 Vida: {a.vida}/{a.vida_max}")
        print(f"⚔️ Ataque: {a.ataque}")
        print(f"🛡️ Defesa: {a.defesa}")
        print(f"🔮 Mana: {getattr(a, 'mana', 0)}")
        print(f"✨ Ataque Mágico: {personagem.ataque_magico}\n")

        return personagem

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
            print(f"Dificuldade atual: {self.missao_config['dificuldade'] or '(não definida)'}")
            print(f"Cenário atual:     {self.missao_config['cenario'] or '(não definido)'}")
            print(f"Missão atual:      {self.missao_config['missao'] or '(não definida)'}")

            print() # Pular linha

            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print("[3] Pré-visualizar missão")
            print("[4] Iniciar missão (com d20 e d6)")
            print("[5] Escolher missão específica")
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
            elif op == "5":
                self.escolher_missao()
            elif op == "9":
                self._ajuda_missao()
            elif op == "0":
                break
            else:
                print("Opção inválida.")


    def escolher_missao(self) -> None:
        self.logger.info("Escolhendo as missões disponíveis.")
        print("Escolha de Missões:")
        print("[1] Eliminar Ladrão")
        print("[2] Eliminar Goblin")
        print("[3] Eliminar Golem")
        print("[4] Eliminar Elfo")
        print("[5] Eliminar Dragão")
        op = input("> ").strip()
        mapa = {
            "1": Missao.missao_1(self),
            "2": Missao.missao_2(self),
            "3": Missao.missao_3(self),
            "4": Missao.missao_4(self),
            "5": Missao.missao_5(self),
        }

        escolha = mapa.get(op)
        if escolha:
            self.missao_config["missao"] = escolha
            print(f"Missão definida: {escolha}")


    def _escolher_dificuldade(self) -> None:
        print("\nDificuldades:")
        print("[1] Fácil")
        print("[2] Média")
        print("[3] Difícil")
        op = input("> ").strip()
        mapa = {"1": "Fácil", "2": "Média", "3": "Difícil"}
        escolha = mapa.get(op)
        if escolha:
            self.missao_config["dificuldade"] = escolha
            print(f"Dificuldade definida: {escolha}")
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
        print(f"- Dificuldade: {self.missao_config['dificuldade'] or '(não definida)'}")
        print(f"- Cenário:     {self.missao_config['cenario'] or '(não definido)'}")
        print("- Inimigos e recompensas: (em breve)")

    # ======================== Missão com combate ============================
    def _iniciar_missao_placeholder(self, inimigo=None) -> None:
        self.logger.info("Iniciando a missão.")
        if not self.personagem["nome"]:
            print("Crie um personagem antes de iniciar uma missão.")
            return

        # Cria inimigo se não informado
        if inimigo is None:
            inimigo = Inimigo.goblin()

        heroi = self.mostrar_personagem
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
        #parametro a ser usado para salvar na pasta saves
        nome_arquivo = os.path.join(self.save_dir, "quick_save.json")
        self.salvar_arquivo(nome_arquivo)
        self._ultimo_save = nome_arquivo
        print(f"✔ Salvo (simulado) em: {self._ultimo_save}")

    def _salvar_nomeado(self) -> None:
        nome = input("Nome do arquivo de save (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"
        #parametro a ser usado para salvar na pasta saves
        caminho_completo = os.path.join(self.save_dir, nome)
        self.salvar_arquivo(caminho_completo)
        self._ultimo_save = caminho_completo
        print(f"✔ Progresso Salvo Como: {self._ultimo_save}")

    def salvar_arquivo(self, nome_arquivo: str) -> None:
        dados ={
            "personagem": self.personagem,
            "missao_config": self.missao_config,
        }
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:

                json.dump(dados, f, indent=4, ensure_ascii=False)
                self.logger.info(f"Jogo salvo em : {nome_arquivo}")
        except Exception as error:
            self.logger.info(f"Erro ao salvar arquivo: {error}")
            print(f"Erro ao salvar arquivo: {error}")

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
            print("[3] Mostrar Saves disponíveis")  
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._carregar_ultimo()
            elif op == "2":
                self._carregar_nomeado()
            elif op == "3":
                self.listar_saves()
            elif op == "9":
                self._ajuda_carregar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _carregar_ultimo(self) -> None:
        
        if not self._ultimo_save:
            return print("Nenhum save recente encontrado.")
        if not os.path.exists(self._ultimo_save):
            return print(f"Arquivo '{self._ultimo_save}' não foi encontrado.")
        
        self.carregar_arquivo(self._ultimo_save)
        print(f"✔ Progresso carregado de: {self._ultimo_save}")

    def _carregar_nomeado(self) -> None:
        nome = input("Nome do arquivo para carregar (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"
        caminho_completo = os.path.join(self.save_dir,nome)
        #Verifica se o arquivo existe na pasta saves
        if not os.path.exists(caminho_completo):
            return print(f"Arquivo '{caminho_completo}' não foi encontrado.")
        self.carregar_arquivo(caminho_completo)
        print(f"✔ Progresso carregado de: {caminho_completo}")

    def listar_saves(self) -> None:
        """Lista os arquivos de save na pasta de saves."""
        print("\nArquivos de Save Disponíveis:")
        arquivos = os.listdir(self.save_dir)
        for arquivo in arquivos:
            if arquivo.endswith(".json"):
                print(f"- {arquivo}")

    def carregar_arquivo(self, nome_arquivo: str) -> None:
        try:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.personagem = dados.get("personagem", self.personagem)
            self.missao_config = dados.get("missao_config", self.missao_config)
        except Exception as error:
            self.logger.info(f"Erro ao carregar arquivo: {error}")
            print(f"Erro ao carregar arquivo: {error}")

    def _ajuda_carregar(self) -> None:
        print("\nAjuda — Carregar")
        print("- O carregamento aqui é apenas ilustrativo (sem leitura real).")
        print("- Use o nome que você “salvou” anteriormente para simular.")
