import random

def rolar_d6():
    return random.randint(1, 6)

if __name__ == "__main__":
    print("Dado d6. Pressione Enter para rolar, ou 'q' para sair.")
    while True:
        cmd = input("> ")
        if cmd.strip().lower() == "q":
            break
        print(f"Você rolou: {rolar_d6()}")

# d20.py
import random

def rolar_d20():
    return random.randint(1, 20)

if __name__ == "__main__":
    print("Dado d20. Pressione Enter para rolar, ou 'q' para sair.")
    while True:
        cmd = input("> ")
        if cmd.strip().lower() == "q":
            break
        print(f"Você rolou: {rolar_d20()}")
