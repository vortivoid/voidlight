import discord
import random
import json
import PkmnResistanceCalculator
import shit_story_generator
import uwuify
import os
from enum import Enum
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from mergedeep import merge

MAINTAINENCE_MODE: bool = False

ADMINS: list = [1377945939859341373]

DAILY_REWARD: int = 10
STREAK_BONUS: int = 10
DAILY_BONUS_MAX: int = 100

HIGHER_LOWER_PRIZES: dict = {
    5: 500,
    4: 300,
    3: 100,
    2: 50,
    1: 20
}

HANGMAN_PRIZES: dict = {
    "first_try": 1000,
    7: 500,
    6: 300,
    5: 200,
    4: 100,
    3: 80,
    2: 50,
    1: 20    
}

with open("achievements.json", "r") as file:
    ACHIEVEMENTS: dict = json.load(file)

with open("shop.json", "r") as file:
    SHOP: dict = json.load(file)

help_message: str = "Commands:\n" \
"- !help: You literally just used it bruh you know what this does :sob:.\n" \
"- !say [text]: Repeats whatever is sent following the command.\n" \
"- !decide [choices]: Chooses a random word from a list seperated by spaces.\n" \
"- !typecheck [pokemon]: Lists the type matchups against the specified pokemon (data sourced from [PokeAPI](<https://pokeapi.co/>)).\n" \
"- !shittystory [names]: Writes random interactions between all the names entered.\n" \
"- !8ball [question]: Responds to the question via a deep and meaningful thought process.\n" \
"- !uwuify [text]: Absolutely ruins the provided text and makes you want to gouge your eyes out.\n" \
"- !daily: Claim your daily voidglow reward.\n" \
"- !coinflip <prediction> <bet>: Flip a coin. Can __optionally__ enter a predition and a bet amount to potentially earn voidglow from a correct prediction.\n" \
"- !balance: Check your voidglow balance.\n" \
"- !transfer [@recipient] [amount]: Transfer a specified amount of voidglow from your balance to the recipient.\n" \
"- !higherlower: Starts a game of Higher or Lower where you can guess the number the bot chooses. You can win voidglow equivilent to the number of remaining attempts you finish with.\n" \
"- !shop: Lists all the items in the shop.\n" \
"- !buy [item name]: Buys an item from the shop.\n" \
"- !top: Lists server members by order of voidglow balance.\n" \
"- !badges <@member>: Lists all badges owned by the user.\n" \
"- !streak: Gets your current daily streak.\n" \
"- !cancel: Cancels any ongoing games.\n" \
"- !stats <@member>: Lists all tracked statictics on the user."

eightball_responses: list = [
                    "Certainly!", 
                    "Why yes of course!", 
                    "Yeah 100%", 
                    "Uhhhhh... maybe?", 
                    "I suppose so.", 
                    "It's within the realm of possibility.", 
                    "Girl I have no clue :sob:", 
                    "I don't know and I don't care.", 
                    "Boring question :yawning_face:", 
                    "NO!", 
                    "Nuh uh.", 
                    "NO?!?!?", 
                    "That is simply impossible.", 
                    "Ask someone else.", 
                    "Wouldn't YOU like to know!", 
                    "Maybe the real question is the friends we made along the way.",
                    "Idk ask Google",
                    "Idk ask Bing",
                    "Good question.",
                    "What's it to ya?",
                    "Yeah no yeah no yeah",
                    "Yes...?",
                    "No...?",
                    "Maybe...?",
                    "Abso-freaking-lutely!",
                    "I'm afraid your question has been deemed STUPID and DUMB, and therefore I cannot answer it.",
                    "42.",
                    "Calculating.... just kidding i have no clue lol.",
                    "You must be a special breed of stupid to ask something so obvious.",
                    "I could answer that, but I have decided not to.",
                    "Lol idk.",
                    "YES!..... maybe?",
                    "Yes but only on wednesdays.",
                    "No but only on thursdays.",
                    "Only if you say the magic word.",
                    "No but also yes.",
                    "Yeah! :D",
                    "Error: Could not calculate response to such a dumb question. Please try again with a less dumb question.",
                    "Well yes, but...",
                    "What does that even mean?",
                    "Probably.",
                    "Probably not.",
                    ":sob: sorry :sob: that :sob: question :sob: is :sob: too :sob: sad :sob: for :sob: me :sob: to :sob: answer :sob:.",
                    "YES?!?!?",
                    "Well duh, obviously."
                    "I just opened a fortune cookie and it didn't answer your question, but apparently you're going to die soon."
                    "If you ask one more question like that I'm gonna lose it.",
                    "No. Just no.",
                    "Fun fact, this is the 49th possible response I have for 8ball! Oh right, your question. Uhh... Sorry I wasn't listening.",
                    "Well, if you asked a random homeless guy, what would he say? Probably something like... 'I'm starving, please could you spare a dollar?'. So there you go, that's the answer to your question. Give me your money! :money_mouth: >:3 ",
                ]

# Forms a single string from a list of strings
def reconstruct_from_split(split_message: list, split_index: int):
    message: str = ""
    new_split: list = split_message[split_index:len(split_message)]
    for item in new_split:
        message += item + " "
    message = message.strip()
    return message

def update_all_user_data():
    for entry in os.listdir("userdata/"):
        with open(f"userdata/{entry}", "r") as file:
            data: dict = json.load(file)
            data = update_user_data(data)
        with open(f"userdata/{entry}", "w") as file:
            json.dump(data, file, indent=4)

def update_user_data(data: dict, guild_id = ""):
    with open("default_user_profile.json", "r") as file:
        default_data: dict = json.load(file)
    updated_data: dict = merge({}, default_data, data)        
    if guild_id != "" and str(guild_id) not in updated_data["associated_guilds"]:
        updated_data["associated_guilds"].append(str(guild_id))
    return updated_data

# Returns a dictionary from a json file at the provided filepath
def get_user_data(member: discord.Member):
    filepath: str = f"userdata/{member.id}.json"
    try:
        with open(filepath, "r") as file:
            data: dict = json.load(file)
    except FileNotFoundError:
        with open("default_user_profile.json") as file:
            data: dict = json.load(file)
            data["latest_known_name"] = member.name
    except JSONDecodeError:
        if os.path.getsize(filepath) == 0:
            pass
        else:
            os.rename(filepath, filepath+".bak")
        with open("default_user_profile.json") as file:
            data: dict = json.load(file)
            data["latest_known_name"] = member.name

    if member.name != data["latest_known_name"]:
        if data["latest_known_name"] != "none":
            data["past_known_names"] += data["latest_known_name"]
        data["latest_known_name"] = member.name

    data: dict = update_user_data(data)

    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)
    return data

def get_user_data_from_id(id: str, name: str = ""):
    filepath = f"userdata/{id}.json"
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        with open("default_user_profile.json") as file:
            data = json.load(file)
            if name != "":
                data["latest_known_name"] = name
    except JSONDecodeError:
        if os.path.getsize(filepath) == 0:
            pass
        else:
            os.rename(filepath, filepath+".bak")
        with open("default_user_profile.json") as file:
            data = json.load(file)
            if name != "" and name != data["latest_known_name"]:
                data["past_known_names"] += data["latest_known_name"]
                data["latest_known_name"] = name
    
    data = update_user_data(data)

    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)
    return data


class BALANCE_MODIFIER(Enum):
    earned = 1
    lost = 2
    spent = 3
    given = 4
    recieved = 5
    granted = 6

def modify_balance(user: dict, amount: int, modifier: BALANCE_MODIFIER):
    if "balance" not in user:
        return False
    if amount <= 0:
        print("Error: Balance modification only accepts positive values")
        return False
    match modifier:
        case BALANCE_MODIFIER.earned:
            user["balance"] += amount
            user["stats"]["voidglow"]["earned"] += amount
            return True
        case BALANCE_MODIFIER.lost:
            user["balance"] -= amount
            user["stats"]["voidglow"]["lost"] += amount
            return True
        case BALANCE_MODIFIER.spent:
            user["balance"] -= amount
            user["stats"]["voidglow"]["spent"] += amount
            return True
        case BALANCE_MODIFIER.given:
            user["balance"] -= amount
            user["stats"]["voidglow"]["given"] += amount
            return True
        case BALANCE_MODIFIER.recieved:
            user["balance"] += amount
            user["stats"]["voidglow"]["recieved"] += amount
            return True
        case BALANCE_MODIFIER.granted:
            user["balance"] += amount
            user["stats"]["voidglow"]["granted"] += amount
            return True


class MyClient(discord.Client):

    async def process_message(self, message):

        response_blocked = False
        split_message: list[str] = message.content.split()

        if message.author == self.user:
            return
        if message.guild is None:
            return
        if len(split_message) == 0:
            return

        user_id: str = str(message.author.id)
        filepath: str = f"userdata/{user_id}.json"
        data: dict = get_user_data(message.author)
        data = update_user_data(data, str(message.guild.id))
        with open(f"userdata/{user_id}.json", "w") as file:
            json.dump(data, file, indent=4)


        # Process Functions
        async def reply(text: str):
            await message.channel.send(f"<@{user_id}>\n{text}")
        
        async def grant_badge(user: dict, badge_name: str):
            if badge_name in user["badges"]:
                return False
            if badge_name in ACHIEVEMENTS:
                badge = ACHIEVEMENTS[badge_name]
                user["badges"].update({badge_name: badge})
            elif badge_name in SHOP:
                badge = SHOP[badge_name]
                user["badges"].update({badge_name: badge})
            else:
                return False
            await message.channel.send(f"<@{user_id}> has earned the {badge["title"]} badge!")
            return True

        async def update_badges(user: dict):
            if "stats" not in user:
                return False
            if user["stats"]["daily"]["longest_streak"] >= 3:
                await grant_badge(user, "freshface")
            if user["stats"]["daily"]["longest_streak"] >= 7:
                await grant_badge(user, "1weekwonder")
            if user["stats"]["daily"]["longest_streak"] >= 14:
                await grant_badge(user, "fortnighter")
            if user["stats"]["daily"]["longest_streak"] >= 30:
                await grant_badge(user, "loyaluser")
            if user["stats"]["daily"]["longest_streak"] >= 100:
                await grant_badge(user, "professionalstreaker")
            if user["stats"]["daily"]["longest_streak"] >= 365:
                await grant_badge(user, "lifelongfriend")

            if user["stats"]["coinflip"]["biggest_winning_bet"] >= 1000:
                await grant_badge(user, "risktaker")
            if user["stats"]["coinflip"]["biggest_winning_bet"] >= 10000:
                await grant_badge(user, "bigrisktaker")
            if user["stats"]["coinflip"]["biggest_winning_bet"] >= 100000:
                await grant_badge(user, "hugerisktaker")
            if user["stats"]["coinflip"]["biggest_winning_bet"] >= 500000:
                await grant_badge(user, "instantmillionaire")
            if user["stats"]["coinflip"]["longest_streak"] >= 5:
                await grant_badge(user, "flippingpro")
            if user["stats"]["coinflip"]["longest_streak"] >= 10:
                await grant_badge(user, "flippingmaster")
            if user["stats"]["coinflip"]["longest_streak"] >= 12:
                await grant_badge(user, "flippingshinyhunter")
            if user["stats"]["coinflip"]["longest_streak"] >= 13:
                await grant_badge(user, "flippingshinyhunter")
                
            if user["stats"]["higherlower"]["first_attempt_wins"] >= 1:
                await grant_badge(user, "luckyguesser")
            if user["stats"]["higherlower"]["first_attempt_wins"] >= 5:
                await grant_badge(user, "mindreader")

        # Commands
        if message.content[0] == "!" or split_message[0] == "<@1388908602932203520>":
            if MAINTAINENCE_MODE:
                if user_id not in ADMINS:
                    await reply("I am currently undergoing maintainence! Commands are disabled for non-admin users.")
                    return

            if message.content[0] == "!":
                split_message[0] = split_message[0][1:len(split_message[0])] #remove !
            elif split_message[0] == "<@1388908602932203520>":
                split_message.pop(0) #remove bot mention

            response_blocked = True

            if split_message[0] == "help":
                await message.channel.send(help_message)

            elif split_message[0] == "say":
                if len(split_message) < 2:
                    await message.channel.send("*says nothing*\n(Useage: !say [message])")
                else:
                    await message.channel.send(f"{reconstruct_from_split(split_message, 1)} \n-<@{user_id}>")
                    await message.delete()
            
            elif split_message[0] == "decide":
                if len(split_message) < 3:
                    await reply("I need at least 2 options you freaking dingus")
                else:
                    await reply(f"I choose... {split_message[random.randint(1, (len(split_message) - 1))]}")
            
            elif split_message[0] == "rate":
                if len(split_message) < 2:
                    await reply("Rate what exactly? (Usage:\n!rate [thing to rate])")
                else:
                    not_so_random = random.Random(message.content)
                    await reply("I rate " + reconstruct_from_split(split_message, 1) + "a " + str(not_so_random.randint(0, 10)) + "/10!")
            
            elif split_message[0] == "typecheck" or split_message[0] == "tc":
                if len(split_message) < 2:
                    await reply("Usage:\n!typecheck [pokemon]")
                else:
                    try:
                        await reply(str(PkmnResistanceCalculator.calculate(split_message[1])))
                    except:
                        await reply("Sorry, this Pokemon could not be checked. Make sure you spelt it correctly! (Or get Vorti to get off their lazy ass and fix this if you did)")

            elif split_message[0] == "shittystory" or split_message[0] == "ss":
                if len(split_message) < 2:
                    await reply("Please provide a list of characters! Eg: '!shittystory bob jane mark sharon'")
                else:
                    await reply(str(shit_story_generator.generate(split_message[1:len(split_message)])))
            
            elif split_message[0] == "8ball" or split_message[0] == "8b":
                if len(split_message) < 2:
                    await reply("Uhh... you're supposed to ask a question, dumbass.")
                else:
                    not_so_random = random.Random(message.content)
                    await reply(eightball_responses[not_so_random.randint(0, (len(eightball_responses) - 1))])
            
            elif split_message[0] == "uwuify" or split_message[0] == "uwu":
                if len(split_message) < 2:
                    await reply("U-uhhm, y-yuwu need tu put a s-swentence, siwwy biwwy >w<")
                else:
                    new_message = uwuify.run(reconstruct_from_split(split_message, 1))
                    await message.channel.send(f"<@{user_id}> says:\n{new_message}")
                    await message.delete()

            elif split_message[0] == "daily" or split_message[0] == "d":
                bonus_earned = 0
                if data["last_daily"] == str(datetime.now().strftime("%Y-%m-%d")):
                    await reply("You have already claimed your daily reward!")
                    return
                
                yesterday = (datetime.now() - timedelta(days = 1)).strftime("%Y-%m-%d")
                if data["last_daily"] == yesterday:
                    data["daily_streak"] += 1
                    data["stats"]["daily"]["longest_streak"] = max(data["stats"]["daily"]["longest_streak"], data["daily_streak"])
                    bonus_earned = min((STREAK_BONUS * (int(data["daily_streak"] - 1))), DAILY_BONUS_MAX)
                else:
                    data["daily_streak"] = 1
                
                total_earnings = DAILY_REWARD + bonus_earned
                modify_balance(data, total_earnings, BALANCE_MODIFIER.earned)
                data["stats"]["daily"]["voidglow_earned"] += total_earnings
                data["last_daily"] = datetime.now().strftime("%Y-%m-%d")
            
                await update_badges(data)

                await reply(f"Claimed {total_earnings} voidglow! Your new balance is " + str(data["balance"]) + f" voidglow. ({data["daily_streak"]} day streak!)")
                with open(filepath, "w") as file:
                    json.dump(data, file, indent=4)
            
            elif split_message[0] == "balance" or split_message[0] == "bal" or split_message[0] == "b":
                if len(split_message) > 1:
                    if split_message[1][0] != "<":
                        await reply("Useage: !balance <@user>")
                        return
                    target_id: str = split_message[1][2:-1]
                    target_data = get_user_data_from_id(target_id)
                    await reply(f"{target_data["latest_known_name"]}'s balance is {target_data["balance"]} voidglow.")
                else:
                    await reply(f"{data["latest_known_name"]}'s' balance is {data["balance"]} voidglow.")
        
            elif split_message[0] == "coinflip" or split_message[0] == "cf" or split_message[0] == "flip":
                local_random = random.Random(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                result = local_random.choice(['heads', 'tails'])
                if len(split_message) < 2:
                    await reply(f"Flipping a coin... It's {result}!")
                else:
                    bet_amount = 0
                    if len(split_message) >= 3:
                        try:
                            bet_amount = int(split_message[2])
                        except ValueError:
                            await reply("Invalid bet amount! Please enter a valid number. (Usage: !coinflip [heads/tails] [bet amount])")
                            return
                        if bet_amount > data["balance"]:
                            await reply(f"You don't have enough voidglow to make that bet! Your current balance is {str(data["balance"])} voidglow.")
                            return
                        if bet_amount <= 0:
                            await reply("Please enter a positive number.")
                            return
                    
                    if split_message[1].lower()[0] == "h":
                        user_guess: str = "heads"
                    elif split_message[1].lower()[0] == "t":
                        user_guess: str = "tails"
                    else:
                        await reply(f"Invalid choice! Please choose heads or tails. (Usage: !coinflip [heads/tails])")
                        return
                    
                    if user_guess == result:
                        await reply(f"You chose {user_guess} and the coin landed on {result}. You win!")
                        await reply(f"You won {bet_amount} voidglow! Your new balance is {data['balance'] + bet_amount} voidglow.")
                        modify_balance(data, bet_amount, BALANCE_MODIFIER.earned)
                        data["stats"]["coinflip"]["total_winnings"] += bet_amount
                        data["stats"]["coinflip"]["correct_predictions"] += 1
                        data["stats"]["coinflip"]["current_streak"] += 1
                        data["stats"]["coinflip"]["longest_streak"] = max(data["stats"]["coinflip"]["current_streak"], data["stats"]["coinflip"]["longest_streak"])
                        data["stats"]["coinflip"]["biggest_winning_bet"] = max(data["stats"]["coinflip"]["biggest_winning_bet"], bet_amount)
                    else:
                        await reply(f"You chose {user_guess} but the coin landed on {result}. You lose!")
                        await reply(f"You lost {bet_amount} voidglow! Your new balance is {data['balance'] - bet_amount} voidglow.")
                        modify_balance(data, bet_amount, BALANCE_MODIFIER.lost)
                        data["stats"]["coinflip"]["total_losings"] += bet_amount
                        data["stats"]["coinflip"]["incorrect_predictions"] += 1
                        data["stats"]["coinflip"]["current_streak"] = 0
                        data["stats"]["coinflip"]["biggest_losing_bet"] = max(data["stats"]["coinflip"]["biggest_losing_bet"], bet_amount)
                    
                    data["stats"]["coinflip"]["total_betted"] += bet_amount
                    data["stats"]["coinflip"]["games_played"] += 1

                    await update_badges(data)

                    with open(filepath, "w") as file:
                        json.dump(data, file, indent=4)

            elif split_message[0] == "transfer" or split_message[0] == "trans":
                if len(split_message) < 3:
                    await reply("Useage: !transfer [@recipient] [amount]")
                recipient_id: str = split_message[1][2:-1]

                if user_id == recipient_id:
                    await reply("You cannot transfer voidglow to yourself!")
                    return
                
                if recipient_id == "1388908602932203520":
                    await reply("No thank you :3")
                    return

                try:
                    amount = int(split_message[2])
                except ValueError:
                    await reply("Invalid transfer amount! Please enter a valid number.")
                    return
                
                if amount <= 0:
                    await reply("Invalid transfer amount! Please enter a positive number.")
                    return
                
                if data["balance"] < amount:
                    await reply(f"Insufficient voidglow! Your balance is {data["balance"]}!")
                    return

                recipient_data = get_user_data_from_id(recipient_id)
                
                data["balance"] -= amount
                data["stats"]["voidglow"]["given"] += amount
                with open(f"userdata/{user_id}.json", "w") as file:
                    json.dump(data, file, indent=4)

                recipient_data["balance"] += amount
                recipient_data["stats"]["voidglow"]["received"] += amount
                with open(f"userdata/{recipient_id}.json", "w") as file:
                    json.dump(recipient_data, file, indent=4)
                
                await message.channel.send(f"{data["latest_known_name"]} sent {amount} voidglow to {recipient_data["latest_known_name"]}!\n" \
                                            f"<@{user_id}>'s balance: {data["balance"]}!\n" \
                                            f"<@{recipient_id}>'s balance: {recipient_data["balance"]}!")

            elif split_message[0] == "higherlower" or split_message[0] == "hl" or split_message[0] == "higherorlower":
                if data.__contains__("games"):
                    await reply("You have a game in progress! Type !cancel to end the game.")
                    return
                randomnumber = random.randint(1,100)
                data["games"] = {"higherlower": {"answer": randomnumber, "remaining_attempts": 5}}
                data["stats"]["higherlower"]["games_played"] += 1
                with open(filepath, "w") as file:
                    json.dump(data, file, indent=4)
                await reply("I have chosen a random number between 1 and 100. You have 5 attempts.")

            elif split_message[0] == "shop" or split_message[0] == "s":
                with open("shop.json", "r") as file:
                    shop_data = json.load(file)
                itemlist: str = ""
                for _, details in shop_data.items():
                    itemlist += f"- {details["title"]} ({details["cost"]} voidglow): {details["description"]}\n"
                await reply(f"Here are the current items:\n{itemlist}\nBuy items with !buy [item name]")
            
            elif split_message[0] == "top" or split_message[0] == "leaderboard" or split_message[0] == "lb":
                userlist = []
                for entry in os.listdir("userdata/"):
                    with open(f"userdata/{entry}") as file:
                        data = json.load(file)
                    if str(message.guild.id) in data["associated_guilds"]:
                        userlist.append(data)
                sorted_userlist = sorted(userlist, key=lambda x: x["balance"], reverse=True)
                final_message = f"{message.guild.name} leaderboard:\n"
                for user in sorted_userlist:
                    final_message += f"- {user["latest_known_name"]}: {user["balance"]} voidglow.\n"
                await reply(final_message)

            elif split_message[0] == "buy":
                if len(split_message) < 2:
                    await reply("Useage: !buy [item name]")
                    return
                
                requested_item_name: str = reconstruct_from_split(split_message, 1)
                requested_item_name = requested_item_name.replace(" ", "").replace("_", "").strip()
                with open("shop.json", "r") as file:
                    shop_data: dict = json.load(file)
                requested_item: dict = shop_data[requested_item_name]

                if requested_item_name in data["badges"]:
                    await reply("You already have this item!")
                    return
                if data["balance"] < requested_item["cost"]:
                    await reply("You do not have enough voidglow for this item!")
                    return
                
                data["balance"] -= requested_item["cost"]
                success = await grant_badge(data, requested_item_name)
                if not success:
                    await reply("There was an error purchasing this badge. Please ensure you entered the name correctly!")
                    return
                await reply(f"purchased the {requested_item["title"]} badge for {requested_item["cost"]} voidglow!")

                data["stats"]["voidglow"]["spent"] += requested_item["cost"]

                with open(filepath, "w") as file:
                    json.dump(data, file, indent=4)

            elif split_message[0] == "badges":
                if len(split_message) >= 2:
                    target_id: str = split_message[1][2:-1]
                    target_data = get_user_data_from_id(target_id)
                else:
                    target_id = user_id
                    target_data = data
                if target_data["badges"] == {} and len(split_message) < 2:
                    await reply("you do not have any badges!")
                    return
                elif target_data["badges"] == {}:
                    await reply("that user does not have any badges!")
                
                final_message: str = f"<@{target_id}>'s badges:"
                for _, badge in target_data["badges"].items():
                    final_message += f"\n{badge["title"]}: {badge["description"]}"
                await reply(final_message)

            elif split_message[0] == "hangman" or split_message[0] == "hm":
                if "games" in data:
                    await reply("You have a game in progress! Type !cancel to end the game.")
                    return
                with open("wordlist.txt", "r") as file:
                    wordlist = file.readlines()
                randomword = random.choice(wordlist)[0:-1]
                blanked_answer: str = "-" * len(randomword)
                data["games"] = {"hangman": {"answer": randomword, "remaining_attempts": 7, "progress": blanked_answer, "first_guess": True, "absent_letters": []}}
                data["stats"]["hangman"]["games_played"] += 1
                with open(filepath, "w") as file:
                    json.dump(data, file, indent=4)
                await reply(f"I have chosen a word, try to guess the word or letters the word contains. You have 7 lives and will lose one for every wrong guess.\nprogress: {blanked_answer}")
                    
            elif split_message[0] == "streak":
                today = str(datetime.now().strftime("%Y-%m-%d"))
                yesterday = (datetime.now() - timedelta(days = 1)).strftime("%Y-%m-%d")
                if data["last_daily"] != today and data["last_daily"] != yesterday:
                    await reply("You do not currently have a daily streak! Start claiming daily rewards with !daily to begin a new streak!")
                    return
                elif data["last_daily"] != today:
                    await reply(f"your current daily streak is: {data["daily_streak"]}!\n(Note: You have not yet claimed today's daily reward! Use !daily to get it!)")
                    return
                else:
                    await reply(f"your current daily streak is: {data["daily_streak"]}!")
                    return

            elif split_message[0] == "cancel" or split_message[0] == "c":
                if "games" not in data:
                    await reply("you do not have any games active!")
                data.pop("games")
                with open(filepath, "w") as file:
                    json.dump(data, file, indent=4)
                await reply("the game was successfully cancelled.")

            elif split_message[0] == "stats":
                if len(split_message) >= 2:
                    target_id = split_message[1][2:-1]
                    target_data = get_user_data_from_id(target_id)
                else:
                    target_id = user_id
                    target_data = data
                final_message = f"<@{target_id}>'s stats are:"
                for category, category_data in target_data["stats"].items():
                    final_message += f"\n**__{category}__**:"
                    for subcategory, subcategory_data in category_data.items():
                        final_message += f"\n- {subcategory.replace("_", " ").title()}: {subcategory_data}"
                await reply(final_message)


            # Admin Commands
            elif split_message[0] == "modvoidglow" or split_message[0] == "modifyvoidglow":
                if str(user_id) != "1377945939859341373":
                    await reply("You do not have permission to use that command.")
                    return
                if len(split_message) < 3:
                    await reply("Useage: !modvoidglow [@user] [amount]")
                    return
                try:
                    amount = int(split_message[2])
                except ValueError:
                    await reply("Invalid amount. Please enter an integer.")
                    return
                recipient_id: str = split_message[1][2:-1]
                recipient_filepath = f"userdata/{recipient_id}.json"
                recipient_data = get_user_data_from_id(recipient_id)
                recipient_data["balance"] += amount
                recipient_data["stats"]["voidglow"]["granted"] += amount
                with open(recipient_filepath, "w") as file:
                    json.dump(recipient_data, file, indent=4)
                if amount > 0:
                    await reply(f"Added {amount} to <@{recipient_id}>'s balance. (New balance: {recipient_data["balance"]})")
                elif amount < 0:
                    await reply(f"Removed {amount} from <@{recipient_id}>'s balance. (New balance: {recipient_data["balance"]})")
                else:
                    await reply(f"Did absolutely fuck all to <@{recipient_id}'s balance.")

            elif split_message[0] == "grantbadge" or split_message[0] == "addbadge":
                if str(user_id) != "1377945939859341373":
                    await reply("You do not have permission to use that command.")
                    return
                if len(split_message) < 3:
                    await reply("Useage: !grantbadge [@user] [badgename]")
                    return
                badge_name = split_message[2]
                recipient_id: str = split_message[1][2:-1]
                recipient_filepath = f"userdata/{recipient_id}.json"
                recipient_data = get_user_data_from_id(recipient_id)
                success = grant_badge(recipient_data, badge_name)
                if not success:
                    await reply("There was an error purchasing this badge. Please ensure you entered the name correctly!")
                with open(recipient_filepath, "w") as file:
                    json.dump(recipient_data, file, indent=4)
                await reply(f"<@{recipient_id}> has been granted the {badge_name} badge!")

            # Undocumented/Secret Commands
            elif split_message[0] == "helpmesleep": 
                await reply("sure thing bestiepop, just stand still a sec...")
                await reply("https://media.tenor.com/AhBxuESbEQsAAAAi/jefrooo-brick.gif")

            else:
                response_blocked = False

        # Responses
        if response_blocked == False:
            if MAINTAINENCE_MODE:
                if user_id not in ADMINS:
                    return
            
            elif "cat" in message.content.lower():
                await message.add_reaction("🐱")
            
            elif ":3" in message.content.lower():
                await message.channel.send(":3")
            
            # Games
            if "games" not in data:
                return
            elif "higherlower" in data["games"]:
                if "processing" in data["games"]:
                    if data["games"]["processing"] == True:
                        await reply("please slow down!")
                        return
                with open(filepath, "w") as file:
                    data["games"]["processing"] = True
                    json.dump(data, file, indent=4)
                try:
                    attempt = int(message.content)
                except ValueError:
                    await reply("That is not a valid number. If you wish to cancel Higher or Lower please type !cancel.")
                    return
                if attempt < 1 or attempt > 100:
                    await reply("Please enter a number between 1-100!")
                else:
                    if attempt != data["games"]["higherlower"]["answer"]:
                        data["games"]["higherlower"]["remaining_attempts"] -= 1

                    if attempt < data["games"]["higherlower"]["answer"]:
                        await reply(f"higher. ({data["games"]["higherlower"]["remaining_attempts"]} attempt remaining!)")
                    elif attempt > data["games"]["higherlower"]["answer"]:
                        await reply(f"lower. ({data["games"]["higherlower"]["remaining_attempts"]} attempt remaining!)")
                    else:    
                        prize: int = HIGHER_LOWER_PRIZES[data["games"]["higherlower"]["remaining_attempts"]]

                        if data["games"]["higherlower"]["remaining_attempts"] == 5:
                            await reply("You got it first try!! :D")
                            data["stats"]["higherlower"]["first_attempt_wins"] += 1
                        else:
                            await reply(f"You got it! :D. (Finished with {data["games"]["higherlower"]["remaining_attempts"]} attempts remaining!)")
                        await reply(f"You have been awarded {prize} voidglow!")
                        data["balance"] += prize
                        data["stats"]["voidglow"]["earned"] += prize
                        data["stats"]["higherlower"]["total_winnings"] += prize
                        data["stats"]["higherlower"]["games_won"] += 1
                        data.pop("games")

                    if "games" in data and data["games"]["higherlower"]["remaining_attempts"] <= 0:
                        await message.channel.send(f"<@{user_id}> You ran out of attempts! The answer was: {data["games"]["higherlower"]["answer"]}!")
                        data.pop("games")
                        data["stats"]["higherlower"]["games_lost"] += 1
                    
                    await update_badges(data)
                        
                    with open(filepath, "w") as file:
                        if "games" in data:
                            data["games"]["processing"] = False
                        json.dump(data, file, indent=4)

            elif "hangman" in data["games"]:
                if "processing" in data["games"]:
                    if data["games"]["processing"] == True:
                        await reply("please slow down!")
                        return
                with open(filepath, "w") as file:
                    data["games"]["processing"] = True
                    json.dump(data, file, indent=4)
                if len(split_message) > 1:
                    await reply("Please only enter 1 letter/word! type !cancel if you wish to end the game.")
                else:
                    if len(message.content) > 1:
                        if message.content.lower() == data["games"]["hangman"]["answer"]:
                            if data["games"]["hangman"]["first_guess"] == True:
                                await reply(f"you got it on your first guess! The word was: {data["games"]["hangman"]["answer"]}!")
                                data["stats"]["hangman"]["first_attempt_wins"] += 1
                                prize: int = HANGMAN_PRIZES["first_try"]
                            else:
                                await reply(f"you got it! The word was: {data["games"]["hangman"]["answer"]}!\nFinished with {data["games"]["hangman"]["remaining_attempts"]} lives remaining!")
                                prize: int = HANGMAN_PRIZES[data["games"]["hangman"]["remaining_attempts"]]
                            data["balance"] += prize
                            data["stats"]["voidglow"]["earned"] += prize
                            data["stats"]["hangman"]["total_winnings"] += prize
                            data["stats"]["hangman"]["games_won"] += 1
                            data["stats"]["hangman"]["current_streak"] += 1
                            data["stats"]["hangman"]["longest_streak"] = max(data["stats"]["hangman"]["current_streak"], data["stats"]["hangman"]["longest_streak"])
                            await reply(f"You have been awarded {prize} voidglow!")
                            data.pop("games")
                        else:
                            data["games"]["hangman"]["first_guess"] = False
                            data["games"]["hangman"]["remaining_attempts"] -= 1
                            await reply(f"incorrect word!\nYou have {data["games"]["hangman"]["remaining_attempts"]} lives remaining!\ncurrent progress: {data["games"]["hangman"]["progress"]}\nAbsent Letters: {str(data["games"]["hangman"]["absent_letters"])}")
                            if data["games"]["hangman"]["remaining_attempts"] <= 0:
                                await reply(f"you ran out of lives!\nThe word was: {data["games"]["hangman"]["answer"]}!")
                                data["stats"]["hangman"]["current_streak"] = 0
                                data["stats"]["hangman"]["games_lost"] += 1
                                data.pop("games")
                    else:
                        if message.content.lower() in data["games"]["hangman"]["absent_letters"] or message.content.lower() in data["games"]["hangman"]["progress"]:
                            await reply("you already guessed that letter!")
                        else:
                            i = 0
                            while i <= len(data["games"]["hangman"]["answer"]) - 1:
                                if data["games"]["hangman"]["answer"][i] == message.content.lower():
                                    new_progress: str = data["games"]["hangman"]["progress"][:i] + message.content.lower() + data["games"]["hangman"]["progress"][i+1:]
                                    data["games"]["hangman"]["progress"] = new_progress
                                i += 1

                            if message.content.lower() in data["games"]["hangman"]["answer"]:
                                await reply(f"that letter is in the word!\ncurrent progress: {data["games"]["hangman"]["progress"]}\nAbsent Letters: {str(data["games"]["hangman"]["absent_letters"])}")
                                if data["games"]["hangman"]["progress"] == data["games"]["hangman"]["answer"]:
                                    await reply(f"you got it! The word was: {data["games"]["hangman"]["answer"]}!\nFinished with {data["games"]["hangman"]["remaining_attempts"]} lives remaining!")
                                    prize: int = HANGMAN_PRIZES[data["games"]["hangman"]["remaining_attempts"]]
                                    data["balance"] += prize
                                    data["stats"]["voidglow"]["earned"] += prize
                                    data["stats"]["hangman"]["total_winnings"] += prize
                                    data["stats"]["hangman"]["games_won"] += 1
                                    data["stats"]["hangman"]["current_streak"] += 1
                                    data["stats"]["hangman"]["longest_streak"] = max(data["stats"]["hangman"]["current_streak"], data["stats"]["hangman"]["longest_streak"])
                                    await reply(f"You have been awarded {prize} voidglow!")
                                    data.pop("games")
                                else:
                                    data["games"]["hangman"]["first_guess"] = False
                            else:
                                data["games"]["hangman"]["absent_letters"] += message.content.lower()
                                data["games"]["hangman"]["first_guess"] = False
                                data["games"]["hangman"]["remaining_attempts"] -= 1
                                await reply(f"that letter is NOT in the word!\nYou have {data["games"]["hangman"]["remaining_attempts"]} lives remaining!\ncurrent progress: {data["games"]["hangman"]["progress"]}\nAbsent Letters: {str(data["games"]["hangman"]["absent_letters"])}")
                                if data["games"]["hangman"]["remaining_attempts"] <= 0:
                                    await reply(f"you ran out of lives!\nThe word was: {data["games"]["hangman"]["answer"]}!")
                                    data["stats"]["hangman"]["current_streak"] = 0
                                    data["stats"]["hangman"]["games_lost"] += 1
                                    data.pop("games")
                with open(filepath, "w") as file:
                    if "games" in data:
                        data["games"]["processing"] = False
                    json.dump(data, file, indent=4)

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
    
    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")
        await self.process_message(message)

update_all_user_data()

with open("token.json", "r") as file:
    data = json.load(file)
    TOKEN = data["token"]

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)