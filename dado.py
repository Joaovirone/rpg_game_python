import random

"""
Sistema de Rolar Dados com import random
Rolar D6 = Dados de 1 a 6
Rolar D20 = Dados de 1 a 20
"""


def rolar_d6():
    return random.randint(1, 6)


def rolar_d20():
    return random.randint(1, 20)


if __name__ == "__main__":
    while True:
        print("\nEscolha o dado:")
        print("[1] D6 (1 a 6)")
        print("[2] D20 (1 a 20)")
        print("[Q] Sair")
        cmd = input("> ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "1":
            print(f"Você rolou: {rolar_d6()}")
        elif cmd == "2":
            print(f"Você rolou: {rolar_d20()}")
        else:
            print("Opção inválida! Tente novamente.")
