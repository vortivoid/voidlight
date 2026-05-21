def reconstruct_from_split(split_message: list, split_index: int) -> str:
    message: str = ""
    new_split: list = split_message[split_index:len(split_message)]
    for item in new_split:
        message += item + " "
    message = message.strip()
    return message