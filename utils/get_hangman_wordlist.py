class get_hangman_wordlist:
    def __init__(self) -> list | None:
        wordlist = []
        try:
            with open("wordlist.txt", "r") as file:
                wordlist = file.readlines()
        except FileNotFoundError:
            print("Error: Could not locate file!")
            return None
        return wordlist