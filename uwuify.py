import random

roleplay_actions = ["*boops*", "*blushes*", "*twerks*", "*pees a little*", "*nuzzles*", "*giggles*", "*meows*", "*purrs*", "*uwu*", "*owo*", "*nya!~*"]

def run(message: str):
    new_message = message
    new_message = new_message.replace("l", "w")
    new_message = new_message.replace("r", "w")

    new_new_message = ""
    for char in new_message:
        if char == " ":
            print("found space")
            random_action_chance = random.randint(1,5)
            if random_action_chance == 1:
                action = roleplay_actions[random.randint(0, (len(roleplay_actions) - 1))]
                new_new_message += " " + action + " "
                print("replaced space with " + action)
            else:
                new_new_message += char
        else:
            new_new_message += char
    new_message = new_new_message
    return new_message