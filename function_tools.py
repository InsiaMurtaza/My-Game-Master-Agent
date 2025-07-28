import random
from agents import function_tool

@function_tool
def run_narrator(player_choice)->str:
    options = ["explore","hunt","escape"]
    print(options)
    player_choice = input("What would you choose?")
    if player_choice == "explore" or "hunt" or "escape":
        return f"The player chooses to {player_choice}"

@function_tool
def run_monster()->str:
    player_roll= random.randint(1,6)
    monster_roll = random.randint(1,6)
    if player_roll > monster_roll:
        return f"Combat begins! You roll {player_roll}, monster rolls {monster_roll}. You win!"
    else:
        return f"Combat begins! You roll {player_roll}, monster rolls {monster_roll}. You lose!"

@function_tool
def run_item()->str:
    inventory = []
    # print(f"DEBUG: Type of inventory in run_item: {type(inventory)}") 
    loot = random.choice(["Healing Potion", "Silver Sword", "Magic Scroll"])
    inventory.append(loot)
    return f"You received: {loot}. Inventory now: {inventory}"


