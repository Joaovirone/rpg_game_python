🧙‍♂️ RPG Game em Python

Um RPG de turnos totalmente em Python, estruturado em módulos, com sistema de personagens, inimigos, combate, inventário e drops de itens.
O projeto é orientado a objetos e modularizado para facilitar expansão de classes, missões e balanceamento futuro.

🚀 Funcionalidades Principais
⚔️ Sistema de Combate

Batalhas baseadas em turnos (jogador x inimigo).

Sistema de ataque, defesa, dano crítico e efeitos.

HUD com informações do personagem durante a batalha.

Enemies gerados dinamicamente de acordo com o cenário e dificuldade.

🧩 Sistema de Personagem

Criação de personagem com nome e arquétipo:

Guerreiro → Alta defesa e força física.

Mago → Alto dano mágico, baixa defesa.

Arqueiro → Equilíbrio entre ataque e agilidade.

Curandeiro → Suporte, cura e resistência.

Cada personagem possui atributos como:

vida, mana, ataque, defesa, nivel.

💀 Sistema de Inimigos

Inimigos possuem vida, ataque e defesa base.

Estrutura configurada em ENEMY_BASE_STATS e SCENARIO_PLAN.

Chefes têm HP escalável pela dificuldade.

Geração automática de hordas com base no cenário:

Trilha, Floresta, Caverna, Ruínas.

🎲 Sistema de Drop de Itens

Cada inimigo pode dropar um item ao ser derrotado.

O drop é calculado pela classe Drop_rate, com base em:

Raridade do item (comum, incomum, raro, épico, lendário);

Nível do personagem;

Chance base de drop (limitada a 50%).

Itens possuem atributos específicos:

nome, tipo, valor, raridade, dano, defesa.

🎒 Inventário

Gerenciado pela classe Inventario.

Permite:

Adicionar e remover itens;

Listar itens atuais;

Capacidade máxima configurável.

O jogador pode remover itens digitando o nome no terminal.

💾 Sistema de Save/Load

Os saves ficam armazenados em uma pasta /saves/ dentro do diretório do jogo.

Guarda o progresso, inventário e status do personagem.


rpg_game_python/
│
├── main.py                  # Ponto de entrada do jogo
├── jogo.py                  # Classe principal Jogo (menus, fluxo, saves)
│
├── models/
│   ├── personagem.py        # Criação e lógica dos personagens
│   ├── inimigo.py           # Classe Inimigo, sistema de hordas e drop
│   ├── inventario.py        # Gerenciamento de itens e drop_rate
│   ├── base.py              # Classe Entidade e Atributos
│   └── logger.py            # Logger customizado do jogo
│
├── saves/                   # Diretório de saves automáticos
└── README.md                # (este arquivo)



# Clonar o repositório
git clone https://github.com/seuusuario/rpg_game_python.git
cd rpg_game_python

# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# Executar o jogo
python main.py

Digite o nome do seu personagem: Arthas
Escolha o arquétipo: Guerreiro | Mago | Arqueiro | Curandeiro
> Guerreiro


Você encontra um Goblin!
Goblin recebeu 10 de dano! (HP restante: 2)
💀 Goblin foi derrotado!
🎲 Goblin está tentando dropar um item...
🎁 Goblin dropou: Espada Enferrujada (comum)!



====== Itens do Inventário ======
1. Espada Enferrujada
2. Escudo de Madeira
Digite o nome do item para removê-lo: Escudo de Madeira
Item 'Escudo de Madeira' removido com sucesso!
