import discord
from discord import app_commands
import random
import json
import PkmnResistanceCalculator
import shit_story_generator
import uwuify as uwu
import os
from enum import Enum
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from mergedeep import merge
from utils import get_admins
from utils import get_help_message
from utils import get_hangman_word
from utils import get_eightball_response
from utils import reconstruct_from_split

MAINTAINENCE_MODE: bool = False

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
    "first_try": 10000,
    7: 500,
    6: 300,
    5: 200,
    4: 100,
    3: 80,
    2: 50,
    1: 20    
}

with open("badges.json", "r") as file:
    BADGES: dict = json.load(file)

with open("shop.json", "r") as file:
    SHOP: dict = json.load(file)


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
def get_user_data(member: discord.User):
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

def get_user_file_path(user:discord.User):
    return f"userdata/{user.id}.json"

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

async def grant_badge(user: dict, badge_name: str):
    if badge_name in user["badges"]:
        return None
    if badge_name not in BADGES:
        return None
    user["badges"].append(badge_name)
    return badge_name

async def update_badges(user: dict, interaction:discord.Interaction):
    if "stats" not in user:
        return False
    _earned_badges:list = []
    if user["stats"]["daily"]["longest_streak"] >= 3:
        _result = await grant_badge(user, "freshface")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["daily"]["longest_streak"] >= 7:
        _result = await grant_badge(user, "1weekwonder")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["daily"]["longest_streak"] >= 14:
        _result = await grant_badge(user, "fortnighter")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["daily"]["longest_streak"] >= 30:
        _result = await grant_badge(user, "loyaluser")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["daily"]["longest_streak"] >= 100:
        _result = await grant_badge(user, "professionalstreaker")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["daily"]["longest_streak"] >= 365:
        _result = await grant_badge(user, "lifelongfriend")
        if _result is not None:
            _earned_badges.append(_result)

    if user["stats"]["coinflip"]["biggest_winning_bet"] >= 1000:
        _result = await grant_badge(user, "risktaker")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["coinflip"]["biggest_winning_bet"] >= 10000:
        _result = await grant_badge(user, "bigrisktaker")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["coinflip"]["biggest_winning_bet"] >= 100000:
        _result = await grant_badge(user, "hugerisktaker")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["coinflip"]["biggest_winning_bet"] >= 500000:
        _result = await grant_badge(user, "instantmillionaire")
        if _result is not None:
            _earned_badges.append(_result)

    if user["stats"]["coinflip"]["longest_streak"] >= 5:
        _result = await grant_badge(user, "flippingpro")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["coinflip"]["longest_streak"] >= 10:
        _result = await grant_badge(user, "flippingmaster")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["coinflip"]["longest_streak"] >= 12:
        _result = await grant_badge(user, "flippingshinyhunter")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["coinflip"]["longest_streak"] >= 13:
        _result = await grant_badge(user, "flippingshinyhunter")
        if _result is not None:
            _earned_badges.append(_result)

    if user["stats"]["coinflip"]["games_played"] >= 500:
        _result = await grant_badge(user, "gamblingaddict")
        if _result is not None:
            _earned_badges.append(_result)

    if user["stats"]["coinflip"]["total_winnings"] >= 100000:
        _result = await grant_badge(user, "successfulgambler")
        if _result is not None:
            _earned_badges.append(_result)
        
    if user["stats"]["higherlower"]["first_attempt_wins"] >= 1:
        _result = await grant_badge(user, "luckyguesser")
        if _result is not None:
            _earned_badges.append(_result)
    if user["stats"]["higherlower"]["first_attempt_wins"] >= 5:
        _result = await grant_badge(user, "mindreader")
        if _result is not None:
            _earned_badges.append(_result)
    
    if user["stats"]["hangman"]["flawless_wins"] >= 5:
        _result = await grant_badge(user, "flawlesswordfinder")
        if _result is not None:
            _earned_badges.append(_result)
    
    if user["stats"]["hangman"]["games_played"] >= 100:
        _result = await grant_badge(user, "ropebunny")
        if _result is not None:
            _earned_badges.append(_result)
    
    if user["stats"]["hangman"]["games_won"] >= 20:
        _result = await grant_badge(user, "lifesaver")
        if _result is not None:
            _earned_badges.append(_result)
    
    if user["stats"]["hangman"]["flawless_wins"] >= 5:
        _result = await grant_badge(user, "flawlesswordfinder")
        if _result is not None:
            _earned_badges.append(_result)
    
    if len(user["badges"]) >= 10:
        _result = await grant_badge(user, "badgecollector")
        if _result is not None:
            _earned_badges.append(_result)

    if len(_earned_badges) == 0:
        return
    elif len(_earned_badges) == 1:
        interaction.followup.send(f"You earned the {_earned_badges[0]} badge!")
    else:
        interaction.followup.send(f"You earned the following badges:\n{", ".join(str(item) for item in _earned_badges)}")


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

        # Commands
        if message.content[0] == "!" or split_message[0] == "<@1388908602932203520>":
            if MAINTAINENCE_MODE:
                if user_id not in get_admins():
                    await reply("I am currently undergoing maintainence! Commands are disabled for non-admin users.")
                    return

            if message.content[0] == "!":
                split_message[0] = split_message[0][1:len(split_message[0])] #remove !
            elif split_message[0] == "<@1388908602932203520>":
                split_message.pop(0) #remove bot mention

            response_blocked = True
            
            if split_message[0] == "balance" or split_message[0] == "bal" or split_message[0] == "b":
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

                    #await update_badges(data)

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
                itemlist: str = ""
                for id, cost in SHOP.items():
                    if id not in BADGES:
                        print(f"Error: {id} not found in badges.json!")
                        continue
                    itemlist += f"- {BADGES[id]["title"]} ({cost} voidglow): {BADGES[id]["description"]}\n"
                await reply(f"Here are the current items:\n{itemlist}\nBuy items with !buy [item name]")
            
            elif split_message[0] == "top" or split_message[0] == "leaderboard" or split_message[0] == "lb":
                global_mode: bool =  False
                show_all: bool = False
                if len(split_message) > 1 and split_message[1] == "global":
                    global_mode = True
                if len(split_message) > 2 and split_message[2] == "all":
                    show_all = True
                userlist = []
                for entry in os.listdir("userdata/"):
                    with open(f"userdata/{entry}") as file:
                        data = json.load(file)
                    if not show_all and data["latest_known_name"] == "none":
                        print("No name detected and show_all not set. Skipping entry...")
                        continue
                    if not show_all and data["balance"] == 0:
                        print("No balance detected and show_all not set. Skipping entry...")
                        continue
                    if not global_mode:
                        if str(message.guild.id) in data["associated_guilds"]:
                            userlist.append(data)
                    else:
                        userlist.append(data)
                sorted_userlist = sorted(userlist, key=lambda x: x["balance"], reverse=True)
                if global_mode:
                    final_message = "Global Leaderboard:\n"
                else:
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
                requested_item_name = requested_item_name.lower()
                if requested_item_name not in SHOP:
                    await reply("That item could not be found!")
                    return
                if requested_item_name not in BADGES:
                    await reply("There was a problem fetching this badge's data. Please contact Vorti if this continues.")
                    return
                if requested_item_name in data["badges"]:
                    await reply("You already have this item!")
                    return
                cost = SHOP[requested_item_name]
                if data["balance"] < cost:
                    await reply("You do not have enough voidglow for this item!")
                    return
                success = await grant_badge(data, requested_item_name)
                if not success:
                    await reply("There was an error purchasing this badge. Please ensure you entered the name correctly!")
                    return
                data["balance"] -= SHOP[requested_item_name]
                await reply(f"purchased the {BADGES[requested_item_name]["title"]} badge for {cost} voidglow!")
                data["stats"]["voidglow"]["spent"] += cost
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
                for badge_name in target_data["badges"]:
                    final_message += f"\n{BADGES[badge_name]["title"]}: {BADGES[badge_name]["description"]}"
                await reply(final_message)

            elif split_message[0] == "hangman" or split_message[0] == "hm":
                if "games" in data:
                    await reply("You have a game in progress! Type !cancel to end the game.")
                    return
                randomword = get_hangman_word()
                if randomword is None:
                    await reply("There was an error fetching the word list. Please report this issue to Vorti.")
                    return
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

            elif split_message[0] == "listbadges" or split_message[0] == "allbadges" or split_message[0] == "badgelist":
                final_message:str = "All Badges:\n"
                for _, badgedata in BADGES.items():
                    final_message += f"- {badgedata["title"]}: {badgedata["description"]}\n"
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
                    await reply(f"Did absolutely fuck all to <@{recipient_id}>'s balance.")

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
                success = await grant_badge(recipient_data, badge_name)
                if success == False:
                    await reply("There was an error purchasing this badge. Please ensure you entered the name correctly!")
                    return
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
            if MAINTAINENCE_MODE and user_id not in get_admins():
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
                try:
                    attempt = int(message.content)
                except ValueError:
                    await reply("That is not a valid number. If you wish to cancel Higher or Lower please type !cancel.")
                    return
                if attempt < 1 or attempt > 100:
                    await reply("Please enter a number between 1-100!")
                    return
                else:
                    with open(filepath, "w") as file:
                        data["games"]["processing"] = True
                        json.dump(data, file, indent=4)
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
                        data["stats"]["higherlower"]["current_streak"] += 1
                        data["stats"]["higherlower"]["longest_streak"] = max(data["stats"]["higherlower"]["longest_streak"], data["stats"]["higherlower"]["current_streak"])
                        data.pop("games")

                    if "games" in data and data["games"]["higherlower"]["remaining_attempts"] <= 0:
                        await message.channel.send(f"<@{user_id}> You ran out of attempts! The answer was: {data["games"]["higherlower"]["answer"]}!")
                        data.pop("games")
                        data["stats"]["higherlower"]["games_lost"] += 1
                    
                    #await update_badges(data)
                        
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
                            if data["games"]["hangman"]["remaining_attempts"] == 7:
                                data["stats"]["hangman"]["flawless_wins"] += 1
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
    _data = json.load(file)
    TOKEN = _data["token"]

intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)
commands = app_commands.CommandTree(client)

@commands.command(
    name="say",
    description="Say whatever you want :p"
)
async def say(interaction:discord.Interaction, message:str):
    await interaction.response.send_message(f"<@{interaction.user.id}> says:\n{message}")

@commands.command(
        name="uwuify",
        description="Send an uwu-ified message!"
)
async def uwuify(interaction:discord.Interaction, message:str):
    new_message = uwu.run(message)
    await interaction.response.send_message(f"<@{interaction.user.id}> says:\n{new_message}")

@commands.command(
        name="decide",
        description="Get Voidlight to decide between 2 things."
)
async def decide(interaction:discord.Interaction, option1:str, option2:str):
    await interaction.response.send_message(f"Options: `{option1}` & `{option2}`\n\nI choose... {random.choice([option1, option2])}")

@commands.command(
        name="help",
        description="Displays all avaliable commands."
)
async def help(interaction:discord.Interaction):
    await interaction.response.send_message(get_help_message(), ephemeral=True)

@commands.command(
        name="rate",
        description="Rate something on a scale of 1-10."
)
async def rate(interaction:discord.Interaction, thing:str):
    not_so_random = random.Random(thing.content)
    await interaction.response.send_message(f"I rate {thing} a {str(not_so_random.randint(0, 10))}/10!")

@commands.command(
        name="shitty_story",
        description="Generates a sequence of random events using the provided names"
)
async def shitty_story(interaction:discord.Interaction, names:str):
    name_list = names.replace(" ", "").split(",")    
    if len(name_list) < 2:
        await interaction.response.send_message("Please provide a list of characters! Eg: '/shittystory bob jane mark sharon'", ephemeral=True)
    else:
        await interaction.response.send_message(str(shit_story_generator.generate(name_list)))

@commands.command(
        name="eightball",
        description="Ask a yes/no question and get a deep & insightful response."
)
async def eightball(interaction:discord.Interaction, query:str):
    response = get_eightball_response()
    if response is None:
        await interaction.response.send_message("There was a problem fetching 8ball responses! Please report this issue if it continues.", ephemeral=True)
        return
    else:
        await interaction.response.send_message(f"Query: `{query}`\n\n{response}")

@commands.command(
        name="typecheck",
        description="See how different types interact with the specified Pokemon."
)
async def typecheck(interaction:discord.Interaction, pokemon:str):
    try:
        await interaction.response.send_message(PkmnResistanceCalculator.calculate(pokemon))
    except:
        await interaction.response.send_message("Sorry, this Pokemon could not be checked. Make sure you spelt it correctly!", ephemeral=True)

@commands.command(
        name="daily",
        description="Claim your daily voidglow reward!"
)
async def daily(interaction:discord.Interaction):
    bonus_earned = 0
    _data = get_user_data(interaction.user)
    _filepath = get_user_file_path(interaction.user)
    if _data["last_daily"] == str(datetime.now().strftime("%Y-%m-%d")):
        await interaction.response.send_message("You have already claimed your daily reward!", ephemeral=True)
        return
    
    yesterday = (datetime.now() - timedelta(days = 1)).strftime("%Y-%m-%d")
    if _data["last_daily"] == yesterday:
        _data["daily_streak"] += 1
        _data["stats"]["daily"]["longest_streak"] = max(_data["stats"]["daily"]["longest_streak"], _data["daily_streak"])
        bonus_earned = min((STREAK_BONUS * (int(_data["daily_streak"] - 1))), DAILY_BONUS_MAX)
    else:
        _data["daily_streak"] = 1
    
    total_earnings = DAILY_REWARD + bonus_earned
    modify_balance(_data, total_earnings, BALANCE_MODIFIER.earned)
    _data["stats"]["daily"]["voidglow_earned"] += total_earnings
    _data["last_daily"] = datetime.now().strftime("%Y-%m-%d")

    await update_badges(_data, interaction)

    await interaction.response.send_message(f"Claimed {total_earnings} voidglow! Your new balance is " + str(_data["balance"]) + f" voidglow. ({_data["daily_streak"]} day streak!)")
    with open(_filepath, "w") as file:
        json.dump(_data, file, indent=4)




@client.event
async def on_ready():
    print("Syncing commands...")
    await commands.sync()
    print("Commands synced!")

client.run(TOKEN)