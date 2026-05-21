def get_help_message() -> str:
    message: str = ""
    try:
        with open("help_message.txt", "r") as file:
            message_lines = file.readlines()
            for line in message_lines:
                message += line
    except FileNotFoundError:
        print("Error: Could not locate file!")
        return "This is a debugging message. If you're seeing this then Vorti has fucked up lol."
    return message