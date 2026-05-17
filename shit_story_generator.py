import random

## name1 and name2 get replaced during generation
actions = [
        "name1 kills name2",
        "name1 eats name2",
        "name1 kisses name2",
        "name1 fucks name2",
        "name1 goes on an adventure with name2",
        "name1 tickles name2",
        "name1 beats name2 at chess",
        "name1 beats name2 at monopoly",
        "name2 stares through name2's soul",
        "name1 flexes on name2 with a sick backflip",
        "name1 cuddles name2",
        "name1 gives name2 a nipple cripple",
        "name1 sleeps with name2",
        "name1 breaks name2's legs",
        "name1 gouges name2's eyes out",
        "name1 has a nice romantic dinner with name2",
        "name1 attaches a 'kick me' note to name2",
    ]

def generate_scenario(name1: str, name2: str):
    scenario: str = actions[random.randrange(0,len(actions))]
    scenario = scenario.replace("name1", name1)
    scenario = scenario.replace("name2", name2)
    return scenario

def new_slot_picker(used, slots):
    while True:
        slot = random.randint(0, slots - 1)
        if slot not in used:
            return slot


def character_interactor(character_list: list[str]):
    message: str = ""
    used_indexes = []
    while True:
        if len(used_indexes) == len(character_list):
            break
        elif len(used_indexes) == len(character_list) - 1:
            for index, i in enumerate(character_list):
                if index not in used_indexes:
                    message += (character_list[index] + " was left all alone and DIED </3")
            break
        else:
            rand1 = new_slot_picker(used_indexes, len(character_list))
            char1 = character_list[rand1]
            used_indexes.append(rand1)

            rand2 = new_slot_picker(used_indexes, len(character_list))
            char2 = character_list[rand2]
            used_indexes.append(rand2)
            message += (generate_scenario(char1, char2)+"\n")
    return message

def generate(characters: list[str]):
    """Returns a formatted string of pre-generated character interactions"""
    return character_interactor(characters)