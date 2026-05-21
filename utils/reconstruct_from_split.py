class reconstruct_from_split:
    def __init__(self, split_message: list, split_index: int):
        message: str = ""
        new_split: list = split_message[split_index:len(split_message)]
        for item in new_split:
            message += item + " "
        message = message.strip()
        return message