import os
import asyncio
import random
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("GEMINI_BASE_URL")
MODEL = "gemini-2.0-flash"

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(api_key= gemini_api_key,base_url= base_url)

@function_tool
def roll_dice(sides:int=20)->int:
    return random.randint(1,sides)

@function_tool
def generate_event() -> str:
    events = [
        "You encounter a group of goblins!",
        "You find a hidden treasure chest.",
        "A mysterious fog rolls in...",
        "You discover an ancient scroll.",
        "A trap is triggered beneath your feet!",
    ]
    return random.choice(events)

@function_tool
def run_narrator(context):
    player_choice = context.get("player_choice", "explore")
    event = generate_event()
    return f"The player chooses to {player_choice}. {event}"

@function_tool
def run_monster(context):
    player_roll = roll_dice()
    monster_roll = roll_dice()
    if player_roll > monster_roll:
        return f"Combat begins! You roll {player_roll}, monster rolls {monster_roll}. You win!"
    else:
        return f"Combat begins! You roll {player_roll}, monster rolls {monster_roll}. You lose!"

@function_tool
def run_item(context):
    # inventory = context.get("inventory")
    # if not isinstance(inventory, list):
    #     inventory = [] 
    inventory:list = context.get("inventory", [])
    print(f"DEBUG: Type of inventory in run_item: {type(inventory)}") 
    loot = random.choice(["Healing Potion", "Silver Sword", "Magic Scroll"])
    inventory.append(loot)
    return f"You received: {loot}. Inventory now: {inventory}"

itemagent = Agent(name="ItemAgent",
                  instructions="You are the **ItemAgent**, responsible for managing the player's inventory and rewards. "
        "Upon receiving control, your task is to **distribute loot or add items to the inventory** "
        "by using the `run_item` tool. You will inform the player what they have received "
        "and their current inventory. After fulfilling your task, the current turn or round concludes.",
                  model=OpenAIChatCompletionsModel(model=MODEL,openai_client=client),
                  tools=[run_item]
                  )
monsteragent = Agent(name="MonsterAgent", 
                     instructions="You are the **MonsterAgent**, in charge of combat encounters. "
        "When you receive control, your immediate task is to **initiate a combat sequence** "
        "by using the `run_monster` tool to determine the outcome of the battle. "
        "Once the combat result is determined, regardless of win or loss, "
        "you **must hand off control to the ItemAgent** to manage any rewards or consequences.",
                     model=OpenAIChatCompletionsModel(model=MODEL, openai_client=client),
                     tools=[run_monster],
                     handoffs=[itemagent])

narratoragent = Agent(name="NarratorAgent", 
                      instructions="You are the **NarratorAgent**, the storyteller of this adventure."
        "Your first task is to **generate an initial event** for the player using the `run_narrator` tool. "
        "After successfully generating an event and describing the player's choice, "
        "you **must immediately hand off control to the MonsterAgent** to handle any potential encounters.",
                      model=OpenAIChatCompletionsModel(model=MODEL,openai_client=client),
                      tools=[run_narrator],
                      handoffs=[monsteragent])

async def main():
    print("Welcome to the Game Master Agent. Let's begin the adventure!")
    current_agent = narratoragent
    # Initial context for the game. 'explore' is a sensible default for the narrator.
    context = {"player_choice": "explore"} 
    while True:
        user_start_input = input("\nType 'start' to begin your adventure, or 'quit' to exit: ").lower()
        if user_start_input == "quit":
            print("AI Agent: Goodbye! Thanks for playing.")
            break
        elif user_start_input == "start":
            print("\nAI Agent: Tthe NarratorAgent begins the story...")
            try:
                # The 'input' to the Runner is the initial context.
                # The Runner will manage the handoffs automatically based on agent instructions.
                result = await Runner.run(current_agent, input=context)
                print(f"\nAI Agent: {result.final_output}")
            except Exception as e:
                    print(f"An error occurred during the game turn: {e}")
                    print("AI Agent: I apologize, an error occurred. Let's try to reset or you can quit.")
        else:
            print("AI Agent: Invalid input. Please type 'start' or 'quit'.")
        

if __name__ == "__main__":
  asyncio.run(main())
