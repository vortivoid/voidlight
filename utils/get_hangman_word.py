import random

def get_hangman_wordlist() -> list | None:
    wordlist = []
    try:
        with open("wordlist.txt", "r") as file:
            wordlist = file.readlines()
    except FileNotFoundError:
        print("Error: Could not locate file!")
        return None
    word = random.choice(wordlist)[0:-1]
    return word