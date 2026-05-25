import random

def get_eightball_response() -> str | None:
    try:
        with open("eightball_responses.txt", "r") as file:
            possible_responses = file.readlines()
            response = random.choice(possible_responses).strip()
            return response
    except FileNotFoundError:
        print("Error: File not found!")
        return None