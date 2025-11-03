from __future__ import annotations
import json
import os

class Jogo:
    """
    Estrutura base com menus e submenus completos.
    Implementem a logica do jogo ou persistência real.
    """

    def __init__(self) -> None:
        self.personagem = {
            "nome": None,
            "arquetipo": None,  # ex.: "Guerreiro", "Mago" (placeholder textual)
        }
        self.missao_config = {
            "dificuldade": "Fácil",  # Fácil | Média | Difícil
            "cenario": "Trilha",  # rótulo ilustrativo
        }
        self._ultimo_save = None
        self._ultimo_load = None

        #  Define o nome da pasta
        self.save_directory = "saves"

        #  Garante que essa pasta exista
        try:

            os.makedirs(self.save_directory, exist_ok=True)
        except OSError as e:
            print(f"Erro ao criar o diretório de saves: {e}")

    def SaveFile(self, GameSaveFile: str) -> bool:


        full_save_path = os.path.join(self.save_directory, GameSaveFile)


        game_state = {
            "personagem": self.personagem,
            "missao_config": self.missao_config,
        }

        try:

            with open(full_save_path, 'w', encoding='utf-8') as f:

                json.dump(game_state, f, indent=4, ensure_ascii=False)

            self._ultimo_save = GameSaveFile
            # Mostre o caminho completo para o usuário
            print(f"✔ Jogo salvo com sucesso em: {full_save_path}")

            return True
        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")
            return False
        except Exception as e:
            print(f"Um erro inesperado ocorreu ao salvar: {e}")
            return False

    def _real_load(self, GameSaveFile: str) -> bool:

        # Cria o caminho completo para LER o arquivo, ex: "saves/meu_save.json"
        full_load_path = os.path.join(self.save_directory, GameSaveFile)
        if not os.path.exists(full_load_path):
            print(f"Erro: Arquivo de save não encontrado: {full_load_path}")
            return False

        try:
            with open(full_load_path, 'r', encoding='utf-8') as f:

                dados_carregados = json.load(f)

            self.personagem = dados_carregados.get("personagem", self.personagem)
            self.missao_config = dados_carregados.get("missao_config", self.missao_config)

            self._ultimo_load = GameSaveFile

            print(f"✔ Jogo carregado com sucesso de: {full_load_path}")

            print(f"Personagem carregado: {self.personagem['nome']} ({self.personagem['arquetipo']})")
            return True
        except json.JSONDecodeError:
            print(f"Erro: O arquivo '{full_load_path}' está corrompido ou não é um JSON válido.")
            return False
        except IOError as e:
            print(f"Erro ao ler o arquivo: {e}")
            return False
        except Exception as e:
            print(f"Um erro inesperado ocorreu ao carregar: {e}")
            return False

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
        print("\nArquétipos disponíveis (apenas ilustrativos):")
        print("[1] Guerreiro")
        print("[2] Mago")
        print("[3] Arqueiro")
        print("[4] Curandeiro")
        print("[5] Personalizado")
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
        print("(Obs.: criação ilustrativa; sem atributos ainda.)")

    def _ajuda_criar_personagem(self) -> None:
        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo para continuar.")
        print("- Esta etapa não cria atributos reais; é apenas o fluxo do menu.")
        print("- Implementações futuras podem usar essas escolhas para gerar status.")

    def menu_missao(self) -> None:
        while True:
            print("\n=== Missão ===")
            print(f"Dificuldade atual: {self.missao_config['dificuldade']}")
            print(f"Cenário atual:     {self.missao_config['cenario']}")
            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print("[3] Pré-visualizar missão")
            print("[4] Iniciar missão (placeholder)")
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
        print("- Regras de combate: (em breve)")

    def _iniciar_missao_placeholder(self) -> None:
        if not self.personagem["nome"]:
            print("Crie um personagem antes de iniciar uma missão.")
            return
        print("\nIniciando missão...")
        print("(Placeholder) Combate e lógica de jogo serão implementados futuramente.")
        print("Missão finalizada (simulado). Retornando ao menu de Missão...")

    def _ajuda_missao(self) -> None:
        print("\nAjuda — Missão")
        print("- Selecione dificuldade e cenário.")
        print("- A opção 'Iniciar missão' executará apenas um placeholder.")
        print("- Uma futura implementação pode usar essas escolhas para montar encontros.")

    def menu_salvar(self) -> None:
        while True:
            print("\n=== Salvar ===")
            print("[1] Salvar rápido (quick_save.json)")
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

        self.SaveFile("quick_save.json")

    def _salvar_nomeado(self) -> None:
        nome = input("GameSaveFile: ").strip()

        # Adiciona .json se o usuário esquecer
        if nome and not nome.endswith(".json"):
            nome += ".json"

        if nome:
            # CORREÇÃO AQUI: Chame 'SaveFile' em vez de '_real_load'
            self.SaveFile(nome)
        else:
            print("Nome inválido. Operação cancelada.")

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
            # Chama a lógica real de load
            self._real_load(self._ultimo_save)
        else:
            print("Nenhum save recente encontrado.")

    def _carregar_nomeado(self) -> None:
        nome = input("Nome do arquivo para carregar (ex.: meu_jogo.json): ").strip()

        # Adiciona .json se o usuário esquecer
        if nome and not nome.endswith(".json"):
            nome += ".json"

        if nome:
            # Chama a lógica real de load
            self._real_load(nome)
        else:
            print("Nome não informado.")

    def _ajuda_carregar(self) -> None:
        print("\nAjuda — Carregar")
        print("- Carrega os dados de personagem e missão do arquivo JSON.")
        print("- Use o nome que você salvou anteriormente.")