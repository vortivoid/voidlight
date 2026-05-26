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
from typing import Literal, Optional


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

async def revoke_badge(user: dict, badge_name: str):
    if badge_name not in user["badges"]:
        return None
    if badge_name not in BADGES:
        return None
    user["badges"].remove(badge_name)
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

async def process_hangman(user:discord.User, message:discord.Message):
    _split_message: list[str] = message.content.split()
    _data = get_user_data(user)
    _filepath = get_user_file_path(user)
    with open(_filepath, "w") as file:
        _data["games"]["hangman"]["processing"] = True
        json.dump(_data, file, indent=4)
    if len(_split_message) > 1:
        await message.reply("Please only enter 1 letter/word! type !cancel if you wish to end the game.")
    else:
        if len(message.content) > 1:
            if message.content.lower() == _data["games"]["hangman"]["answer"]:
                if _data["games"]["hangman"]["first_guess"] == True:
                    await message.channel.send(f"you got it on your first guess! The word was: {_data["games"]["hangman"]["answer"]}!")
                    _data["stats"]["hangman"]["first_attempt_wins"] += 1
                    prize: int = HANGMAN_PRIZES["first_try"]
                else:
                    await message.channel.send(f"you got it! The word was: {_data["games"]["hangman"]["answer"]}!\nFinished with {_data["games"]["hangman"]["remaining_attempts"]} lives remaining!")
                    prize: int = HANGMAN_PRIZES[_data["games"]["hangman"]["remaining_attempts"]]
                _data["balance"] += prize
                _data["stats"]["voidglow"]["earned"] += prize
                _data["stats"]["hangman"]["total_winnings"] += prize
                _data["stats"]["hangman"]["games_won"] += 1
                _data["stats"]["hangman"]["current_streak"] += 1
                _data["stats"]["hangman"]["longest_streak"] = max(_data["stats"]["hangman"]["current_streak"], _data["stats"]["hangman"]["longest_streak"])
                if _data["games"]["hangman"]["remaining_attempts"] == 7:
                    _data["stats"]["hangman"]["flawless_wins"] += 1
                await message.channel.send(f"You have been awarded {prize} voidglow!")
                _data.pop("games")
            else:
                _data["games"]["hangman"]["first_guess"] = False
                _data["games"]["hangman"]["remaining_attempts"] -= 1
                await message.channel.send(f"incorrect word!\nYou have {_data["games"]["hangman"]["remaining_attempts"]} lives remaining!\ncurrent progress: {_data["games"]["hangman"]["progress"]}\nAbsent Letters: {str(_data["games"]["hangman"]["absent_letters"])}")
                if _data["games"]["hangman"]["remaining_attempts"] <= 0:
                    await message.channel.send(f"you ran out of lives!\nThe word was: {_data["games"]["hangman"]["answer"]}!")
                    _data["stats"]["hangman"]["current_streak"] = 0
                    _data["stats"]["hangman"]["games_lost"] += 1
                    _data.pop("games")
        else:
            if message.content.lower() in _data["games"]["hangman"]["absent_letters"] or message.content.lower() in _data["games"]["hangman"]["progress"]:
                await message.channel.send("you already guessed that letter!")
            else:
                i = 0
                while i <= len(_data["games"]["hangman"]["answer"]) - 1:
                    if _data["games"]["hangman"]["answer"][i] == message.content.lower():
                        new_progress: str = _data["games"]["hangman"]["progress"][:i] + message.content.lower() + _data["games"]["hangman"]["progress"][i+1:]
                        _data["games"]["hangman"]["progress"] = new_progress
                    i += 1

                if message.content.lower() in _data["games"]["hangman"]["answer"]:
                    await message.channel.send(f"that letter is in the word!\ncurrent progress: {_data["games"]["hangman"]["progress"]}\nAbsent Letters: {str(_data["games"]["hangman"]["absent_letters"])}")
                    if _data["games"]["hangman"]["progress"] == _data["games"]["hangman"]["answer"]:
                        await message.channel.send(f"you got it! The word was: {_data["games"]["hangman"]["answer"]}!\nFinished with {_data["games"]["hangman"]["remaining_attempts"]} lives remaining!")
                        prize: int = HANGMAN_PRIZES[_data["games"]["hangman"]["remaining_attempts"]]
                        _data["balance"] += prize
                        _data["stats"]["voidglow"]["earned"] += prize
                        _data["stats"]["hangman"]["total_winnings"] += prize
                        _data["stats"]["hangman"]["games_won"] += 1
                        _data["stats"]["hangman"]["current_streak"] += 1
                        _data["stats"]["hangman"]["longest_streak"] = max(_data["stats"]["hangman"]["current_streak"], _data["stats"]["hangman"]["longest_streak"])
                        await message.channel.send(f"You have been awarded {prize} voidglow!")
                        _data.pop("games")
                    else:
                        _data["games"]["hangman"]["first_guess"] = False
                else:
                    _data["games"]["hangman"]["absent_letters"] += message.content.lower()
                    _data["games"]["hangman"]["first_guess"] = False
                    _data["games"]["hangman"]["remaining_attempts"] -= 1
                    await message.channel.send(f"that letter is NOT in the word!\nYou have {_data["games"]["hangman"]["remaining_attempts"]} lives remaining!\ncurrent progress: {_data["games"]["hangman"]["progress"]}\nAbsent Letters: {str(_data["games"]["hangman"]["absent_letters"])}")
                    if _data["games"]["hangman"]["remaining_attempts"] <= 0:
                        await message.channel.send(f"you ran out of lives!\nThe word was: {_data["games"]["hangman"]["answer"]}!")
                        _data["stats"]["hangman"]["current_streak"] = 0
                        _data["stats"]["hangman"]["games_lost"] += 1
                        _data.pop("games")
    with open(_filepath, "w") as file:
        if "games" in _data:
            _data["games"]["hangman"]["processing"] = False
        json.dump(_data, file, indent=4)

async def process_higherlower(user:discord.User, message:discord.Message):
    _filepath = get_user_file_path(user)
    _data = get_user_data(user)
    _user_id = str(user.id)
    _attempt: int
    with open(_filepath, "w") as file:
        _data["games"]["higherlower"]["processing"] = True
        json.dump(_data, file, indent=4)
    try:
        _attempt = int(message.content)
    except ValueError:
        await message.channel.send("That is not a valid number. If you wish to cancel Higher or Lower please type !cancel.")
        return
    if _attempt < 1 or _attempt > 100:
        await message.channel.send("Please enter a number between 1-100!")
        return
    else:
        with open(_filepath, "w") as file:
            _data["games"]["processing"] = True
            json.dump(_data, file, indent=4)
        if _attempt != _data["games"]["higherlower"]["answer"]:
            _data["games"]["higherlower"]["remaining_attempts"] -= 1

        if _attempt < _data["games"]["higherlower"]["answer"]:
            await message.channel.send(f"higher. ({_data["games"]["higherlower"]["remaining_attempts"]} attempt remaining!)")
        elif _attempt > _data["games"]["higherlower"]["answer"]:
            await message.channel.send(f"lower. ({_data["games"]["higherlower"]["remaining_attempts"]} attempt remaining!)")
        else:    
            prize: int = HIGHER_LOWER_PRIZES[_data["games"]["higherlower"]["remaining_attempts"]]

            if _data["games"]["higherlower"]["remaining_attempts"] == 5:
                await message.channel.send("You got it first try!! :D")
                _data["stats"]["higherlower"]["first_attempt_wins"] += 1
            else:
                await message.channel.send(f"You got it! :D. (Finished with {_data["games"]["higherlower"]["remaining_attempts"]} attempts remaining!)")
            await message.channel.send(f"You have been awarded {prize} voidglow!")
            _data["balance"] += prize
            _data["stats"]["voidglow"]["earned"] += prize
            _data["stats"]["higherlower"]["total_winnings"] += prize
            _data["stats"]["higherlower"]["games_won"] += 1
            _data["stats"]["higherlower"]["current_streak"] += 1
            _data["stats"]["higherlower"]["longest_streak"] = max(_data["stats"]["higherlower"]["longest_streak"], _data["stats"]["higherlower"]["current_streak"])
            _data.pop("games")

        if "games" in _data and _data["games"]["higherlower"]["remaining_attempts"] <= 0:
            await message.channel.send(f"<@{_user_id}> You ran out of attempts! The answer was: {_data["games"]["higherlower"]["answer"]}!")
            _data.pop("games")
            _data["stats"]["higherlower"]["games_lost"] += 1
            _data["stats"]["higherlower"]["current_streak"] = 0
    with open(_filepath, "w") as file:
        if "games" in _data:
            _data["games"]["higherlower"]["processing"] = False
        json.dump(_data, file, indent=4)

class MyClient(discord.Client):
    async def process_message(self, message):
        if message.author == self.user:
            return
        if message.guild is None:
            return
        if message.content == "":
            return
        
        _user_id: str = str(message.author.id)
        _filepath: str = get_user_file_path(message.author)
        _data: dict = get_user_data(message.author)
        _data = update_user_data(_data, str(message.guild.id))
        with open(_filepath, "w") as file:
            json.dump(_data, file, indent=4)

        async def reply(text: str):
            await message.channel.send(f"<@{_user_id}>\n{text}")
      
        if "cat" in message.content.lower():
            await message.add_reaction("🐱")
        
        if ":3" in message.content.lower():
            await message.channel.send(":3")
        
        if "games" in _data:
            if "higherlower" in _data["games"]:
                if _data["games"]["higherlower"].get("processing", False):
                    await reply("please slow down!")
                else:
                    await process_higherlower(message.author, message)

            elif "hangman" in _data["games"]:
                if _data["games"]["hangman"].get("processing", False):
                    await reply("please slow down!")
                else:
                    await process_hangman(message.author, message)

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
    await interaction.response.send_message(f"I rate {thing} a {str(random.randint(0, 10))}/10!")


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
async def eightball(interaction:discord.Interaction, prompt:str):
    response = get_eightball_response()
    if response is None:
        await interaction.response.send_message("There was a problem fetching 8ball responses! Please report this issue if it continues.", ephemeral=True)
        return
    else:
        await interaction.response.send_message(f'**Prompt**: "{prompt}"\n\n**Response**: "{response}"')


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


@commands.command(
        name="balance",
        description="Get your current voidglow balance."
)
async def balance(interaction:discord.Interaction, user:Optional[discord.User], show_to_others:Literal["yes", "no"] = "yes"):
    if user is None:
        user = interaction.user
    target_data = get_user_data(user)
    if show_to_others == "yes":
        await interaction.response.send_message(f"{user.name}'s balance is {target_data["balance"]} voidglow.")
    else:
        await interaction.response.send_message(f"{user.name}'s balance is {target_data["balance"]} voidglow.", ephemeral=True)


@commands.command(
        name="coinflip",
        description="Flip a coin, optionally predict the outcome and bet voidglow."
)
async def coinflip(interaction:discord.Interaction, prediction:Optional[Literal["heads", "tails"]], bet_amount:Optional[int]):
    local_random = random.Random(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    result = local_random.choice(['heads', 'tails'])
    if bet_amount is not None and prediction is None:
        await interaction.response.send_message("If you want to bet voidglow, you must select your prediction!", ephemeral=True)
        return
    if prediction is None:
        await interaction.response.send_message(f"Flipping a coin... It's {result}!")
        return
    _data = get_user_data(interaction.user)
    _filepath = get_user_file_path(interaction.user)
    if bet_amount is not None:
        if bet_amount > _data["balance"]:
            await interaction.response.send_message(f"You don't have enough voidglow to make that bet! Your current balance is {str(_data["balance"])} voidglow.", ephemeral=True)
            return
        if bet_amount <= 0:
            await interaction.response.send_message("Please enter a positive number.", ephemeral=True)
            return
        if prediction == result:
            await interaction.response.send_message(f"<@{interaction.user.id}> You chose {prediction} and the coin landed on {result}. You win! :tada:\n\nYou won {bet_amount} voidglow! Your new balance is {_data['balance'] + bet_amount} voidglow.")
            modify_balance(_data, bet_amount, BALANCE_MODIFIER.earned)
            _data["stats"]["coinflip"]["total_winnings"] += bet_amount
            _data["stats"]["coinflip"]["correct_predictions"] += 1
            _data["stats"]["coinflip"]["current_streak"] += 1
            _data["stats"]["coinflip"]["longest_streak"] = max(_data["stats"]["coinflip"]["current_streak"], _data["stats"]["coinflip"]["longest_streak"])
            _data["stats"]["coinflip"]["biggest_winning_bet"] = max(_data["stats"]["coinflip"]["biggest_winning_bet"], bet_amount)
        else:
            await interaction.response.send_message(f"<@{interaction.user.id}> You chose {prediction} but the coin landed on {result}. You lose!\n\nYou lost {bet_amount} voidglow! Your new balance is {_data['balance'] - bet_amount} voidglow.")
            modify_balance(_data, bet_amount, BALANCE_MODIFIER.lost)
            _data["stats"]["coinflip"]["total_losings"] += bet_amount
            _data["stats"]["coinflip"]["incorrect_predictions"] += 1
            _data["stats"]["coinflip"]["current_streak"] = 0
            _data["stats"]["coinflip"]["biggest_losing_bet"] = max(_data["stats"]["coinflip"]["biggest_losing_bet"], bet_amount)
        _data["stats"]["coinflip"]["total_betted"] += bet_amount
    else:
        if prediction == result:
            await interaction.response.send_message(f"<@{interaction.user.id}> You chose {prediction} and the coin landed on {result}. You win! :tada:")
            _data["stats"]["coinflip"]["correct_predictions"] += 1
        else:
            await interaction.response.send_message(f"<@{interaction.user.id}> You chose {prediction} but the coin landed on {result}. You lose!")
            _data["stats"]["coinflip"]["incorrect_predictions"] += 1
    _data["stats"]["coinflip"]["games_played"] += 1
    await update_badges(_data, interaction)
    with open(_filepath, "w") as file:
        json.dump(_data, file, indent=4)


@commands.command(
        name="shop",
        description="Display items in the shop that can be purchased with voidglow."
)
async def shop(interaction:discord.Interaction):
    itemlist: str = ""
    for id, cost in SHOP.items():
        if id not in BADGES:
            print(f"Error: {id} not found in badges.json!")
            continue
        itemlist += f"- {BADGES[id]["title"]} ({cost} voidglow): {BADGES[id]["description"]}\n"
    await interaction.response.send_message(f"Here are the current items:\n{itemlist}\nBuy items with !buy [item name]", ephemeral=True)


@commands.command(
    name="buy",
    description="Purchase an item from the shop."
)
async def buy(interaction:discord.Interaction, item:str):
    requested_item_name = item.replace(" ", "").replace("_", "").strip().lower()
    if requested_item_name not in SHOP:
        await interaction.response.send_message("That item could not be found!", ephemeral=True)
        return
    if requested_item_name not in BADGES:
        await interaction.response.send_message("There was a problem fetching this badge's data. Please contact Vorti if this continues.", ephemeral=True)
        return
    _data = get_user_data(interaction.user)
    if requested_item_name in _data["badges"]:
        await interaction.response.send_message("You already have this item!", ephemeral=True)
        return
    cost = SHOP[requested_item_name]
    if _data["balance"] < cost:
        await interaction.response.send_message("You do not have enough voidglow for this item!", ephemeral=True)
        return
    success = await grant_badge(_data, requested_item_name)
    if not success:
        await interaction.response.send_message("There was an error purchasing this badge. Please ensure you entered the name correctly!", ephemeral=True)
        return
    _data["balance"] -= SHOP[requested_item_name]
    await interaction.response.send_message(f"purchased the {BADGES[requested_item_name]["title"]} badge for {cost} voidglow!")
    _data["stats"]["voidglow"]["spent"] += cost
    _filepath = get_user_file_path(interaction.user)
    with open(_filepath, "w") as file:
        json.dump(_data, file, indent=4)


@commands.command(
        name="badges",
        description="List your currently-owned badges."
)
async def badges(interaction:discord.Interaction, user:Optional[discord.User], show_to_others:Literal["yes", "no"] = "yes"):
    if user is None:
        user = interaction.user
    _data = get_user_data(user)
    if _data["badges"] == {} and user == interaction.user:
        if show_to_others == "yes":
            await interaction.response.send_message("you do not have any badges!")
        else:
            await interaction.response.send_message("you do not have any badges!", ephemeral=True)
        return
    elif _data["badges"] == {}:
        if show_to_others == "yes":
            await interaction.response.send_message(f"{user.name} does not have any badges!")
        else:
            await interaction.response.send_message(f"{user.name} does not have any badges!", ephemeral=True)
        return
    final_message: str = f"{user.name}'s badges:"
    for badge_name in _data["badges"]:
        final_message += f"\n{BADGES[badge_name]["title"]}: {BADGES[badge_name]["description"]}"
    if show_to_others == "yes":
        await interaction.response.send_message(final_message)
    else:
        await interaction.response.send_message(final_message, ephemeral=True)


@commands.command(
        name="streak",
        description="Get your current daily streak."
)
async def streak(interaction:discord.Interaction, user:Optional[discord.User], show_to_others:Optional[bool] = False):
    show_to_others = not show_to_others
    today = str(datetime.now().strftime("%Y-%m-%d"))
    yesterday = (datetime.now() - timedelta(days = 1)).strftime("%Y-%m-%d")
    if user is None:
        user = interaction.user
    _data = get_user_data(user)
    if _data["last_daily"] != today and _data["last_daily"] != yesterday:
        if user == interaction.user:
            await interaction.response.send_message("You do not currently have a daily streak! Start claiming daily rewards with !daily to begin a new streak!", ephemeral=show_to_others)
            return
        else:
            await interaction.response.send_message(f"{user.name} does not currently have a daily streak!", ephemeral=show_to_others)
            return
    elif _data["last_daily"] != today:
        if user == interaction.user:
            await interaction.response.send_message(f"your current daily streak is: {_data["daily_streak"]}!\n(Note: You have not yet claimed today's daily reward! Use !daily to get it!)", ephemeral=show_to_others)
            return
        else:
            await interaction.response.send_message(f"{user.name}'s current daily streak is: {_data["daily_streak"]}!\n(Note: This user have not yet claimed today's daily reward!)", ephemeral=show_to_others)
            return
    else:
        if user == interaction.user:
            await interaction.response.send_message(f"your current daily streak is: {_data["daily_streak"]}!", ephemeral=show_to_others)
            return
        else:
            await interaction.response.send_message(f"{user.name}'s current daily streak is: {_data["daily_streak"]}!", ephemeral=show_to_others)
            return


@commands.command(
        name="transfer",
        description="Send some of your voidglow to someone else."
)
async def transfer(interaction:discord.Interaction, user:discord.User, amount:int):
    if user.id == interaction.user.id:
        await interaction.response.send_message("You cannot transfer voidglow to yourself!", ephemeral=True)
        return
    if user.id == 1388908602932203520:
        await interaction.response.send_message("No thank you :3")
        return
    if user.bot or user.system:
        await interaction.response.send_message("You cannot send voidglow to bots or system accounts.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("Invalid transfer amount! Please enter a positive number.", ephemeral=True)
        return
    _sender_data = get_user_data(interaction.user)
    if _sender_data["balance"] < amount:
        await interaction.response.send_message(f"Insufficient voidglow! Your balance is {_sender_data["balance"]}!")
        return
    _recipient_data = get_user_data(user)
    _sender_data["balance"] -= amount
    _sender_data["stats"]["voidglow"]["given"] += amount
    _sender_file = get_user_file_path(interaction.user)
    _recipient_file = get_user_file_path(user)
    with open(_sender_file, "w") as file:
        json.dump(_sender_data, file, indent=4)
    _recipient_data["balance"] += amount
    _recipient_data["stats"]["voidglow"]["received"] += amount
    with open(_recipient_file, "w") as file:
        json.dump(_recipient_data, file, indent=4)
    await interaction.response.send_message(
        f"{_sender_data['latest_known_name']} sent {amount} voidglow to {_recipient_data['latest_known_name']}!\n"
        f"<@{interaction.user.id}>'s balance: {_sender_data['balance']}!\n"
        f"<@{user.id}>'s balance: {_recipient_data['balance']}!"
    )


@commands.command(
        name="leaderboard",
        description="Displays the leaderboard for either the current guild or globally"
)
async def leaderboard(interaction:discord.Interaction, global_mode:Optional[bool] = False, include_0_voidglow_entries:Optional[bool] = False):
    _userlist = []
    for _entry in os.listdir("userdata/"):
        _data = {}
        with open(f"userdata/{_entry}") as _file:
            _data = json.load(_file)
        if _data["latest_known_name"] == "none":
            print("No name detected. Skipping entry...")
            continue
        if not include_0_voidglow_entries and _data["balance"] == 0:
            print("No balance detected and include_0_voidglow_entries not True. Skipping entry...")
            continue
        if not global_mode:
            if str(interaction.guild_id) in _data["associated_guilds"]:
                _userlist.append(_data)
        else:
            _userlist.append(_data)
    sorted_userlist = sorted(_userlist, key=lambda x: x["balance"], reverse=True)
    if global_mode:
        final_message = "Global Leaderboard:\n"
    else:
        final_message = f"{interaction.guild.name} leaderboard:\n"
    for user in sorted_userlist:
        final_message += f"- {user["latest_known_name"]}: {user["balance"]} voidglow.\n"
    await interaction.response.send_message(final_message)


@commands.command(
        name="stats",
        description="Display a user's tracked statistics."
)
async def stats(interaction:discord.Interaction, user:Optional[discord.User]):
    if user is None:
        user = interaction.user
    _data = get_user_data(user)
    final_message = f"{user.name}'s stats are:"
    for category, category_data in _data["stats"].items():
        final_message += f"\n**__{category}__**:"
        for subcategory, subcategory_data in category_data.items():
            final_message += f"\n- {subcategory.replace("_", " ").title()}: {subcategory_data}"
    await interaction.response.send_message(final_message)


@commands.command(
        name="listbadges",
        description="Lists all the badges that currently exist."
)
async def listbadges(interaction:discord.Interaction):
    final_message:str = "All Badges:\n"
    for _, badgedata in BADGES.items():
        final_message += f"- {badgedata["title"]}: {badgedata["description"]}\n"
    await interaction.response.send_message(final_message, ephemeral=True)


@commands.command(
        name="modvoidglow",
        description="Add or remove voidglow from a user's balance (Admin Only)"
)
async def modvoidglow(interaction:discord.Interaction, user:discord.User, amount:int):
    if interaction.user.id != 1377945939859341373:
        await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
        return
    _recipient_filepath = get_user_file_path(user)
    _recipient_data = get_user_data(user)
    _recipient_data["balance"] += amount
    _recipient_data["stats"]["voidglow"]["granted"] += amount
    with open(_recipient_filepath, "w") as file:
        json.dump(_recipient_data, file, indent=4)
    if amount > 0:
        await interaction.response.send_message(f"Added {amount} to {user.name}'s balance. (New balance: {_recipient_data['balance']})")
    elif amount < 0:
        await interaction.response.send_message(f"Removed {amount} from {user.name}'s balance. (New balance: {_recipient_data['balance']})")
    else:
        await interaction.response.send_message(f"Did absolutely fuck all to {user.name}'s balance.")


@commands.command(
        name="grantbadge",
        description="Grant a badge to a user (Admin Only)"
)
async def grantbadge(interaction:discord.Interaction, user:discord.User, badge_name:str):
    if interaction.user.id != 1377945939859341373:
        await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
        return
    if badge_name not in BADGES:
        await interaction.response.send_message("That badge does not exist!", ephemeral=True)
        return
    _recipient_data = get_user_data(user)
    if badge_name in _recipient_data["badges"]:
        await interaction.response.send_message(f"{user.name} already has the {badge_name} badge!", ephemeral=True)
        return
    success = await grant_badge(_recipient_data, badge_name)
    if success is None:
        await interaction.response.send_message("There was an error purchasing this badge. Please ensure you entered the name correctly!", ephemeral=True)
        return
    _recipient_filepath = get_user_file_path(user)
    with open(_recipient_filepath, "w") as file:
        json.dump(_recipient_data, file, indent=4)
    await interaction.response.send_message(f"{user.name} has been granted the {badge_name} badge!")

@commands.command(
        name="revokebadge",
        description="Revoke a badge from a user (Admin Only)"
)
async def revokebadge(interaction:discord.Interaction, user:discord.User, badge_name:str):
    if interaction.user.id != 1377945939859341373:
        await interaction.response.send_message("You do not have permission to use that command.", ephemeral=True)
        return
    if badge_name not in BADGES:
        await interaction.response.send_message("That badge does not exist!", ephemeral=True)
        return
    _recipient_data = get_user_data(user)
    if badge_name not in _recipient_data["badges"]:
        await interaction.response.send_message(f"{user.name} does not have the {badge_name} badge!", ephemeral=True)
        return
    success = await revoke_badge(_recipient_data, badge_name)
    if success is None:
        await interaction.response.send_message("There was an error revoking this badge. Please ensure you entered the name correctly!", ephemeral=True)
        return
    _recipient_filepath = get_user_file_path(user)
    with open(_recipient_filepath, "w") as file:
        json.dump(_recipient_data, file, indent=4)
    await interaction.response.send_message(f"{user.name} has had the {badge_name} badge revoked!")


@commands.command(
        name="higherlower",
        description="Play a game of higher or lower to win voidglow!"
)
async def higherlower(interaction:discord.Interaction):
    _data = get_user_data(interaction.user)
    if "games" in _data:
        await interaction.response.send_message("You have a game in progress! Type !cancel to end the game.", ephemeral=True)
        return
    randomnumber = random.randint(1,100)
    _data["games"] = {"higherlower": {"answer": randomnumber, "remaining_attempts": 5}}
    _data["stats"]["higherlower"]["games_played"] += 1
    with open(get_user_file_path(interaction.user), "w") as file:
        json.dump(_data, file, indent=4)
    await interaction.response.send_message("I have chosen a random number between 1 and 100. You have 5 attempts.")


@commands.command(
        name="hangman",
        description="Play a game of hangman to win voidglow!"
)
async def hangman(interaction:discord.Interaction):
    _data = get_user_data(interaction.user)
    if "games" in _data:
        await interaction.response.send_message("You have a game in progress! Type !cancel to end the game.", ephemeral=True)
        return
    randomword = get_hangman_word()
    if randomword is None:
        await interaction.response.send_message("There was an error fetching the word list. Please report this issue to Vorti.", ephemeral=True)
        return
    blanked_answer: str = "-" * len(randomword)
    _data["games"] = {"hangman": {"answer": randomword, "remaining_attempts": 7, "progress": blanked_answer, "first_guess": True, "absent_letters": []}}
    _data["stats"]["hangman"]["games_played"] += 1
    with open(get_user_file_path(interaction.user), "w") as file:
        json.dump(_data, file, indent=4)
    await interaction.response.send_message(f"I have chosen a word, try to guess the word or any letters the word contains.\nYou have 7 lives and will lose one for each wrong guess.\nprogress: {blanked_answer}")


@commands.command(
        name="cancel",
        description="Cancel your current game in progress."
)
async def cancel(interaction:discord.Interaction):
    _data = get_user_data(interaction.user)
    if "games" not in _data:
        await interaction.response.send_message("You do not have any games active!", ephemeral=True)
        return
    _data.pop("games")
    with open(get_user_file_path(interaction.user), "w") as file:
        json.dump(_data, file, indent=4)
    await interaction.response.send_message("the game was successfully cancelled.", ephemeral=True)

@client.event
async def on_ready():
    print("Syncing commands...")
    await commands.sync()
    print("Commands synced!")

client.run(TOKEN)