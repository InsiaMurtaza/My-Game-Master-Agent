import os
import asyncio
from agents import Runner, set_tracing_disabled
from openai import AsyncOpenAI
from dotenv import load_dotenv
from game_agents import narratoragent

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("GEMINI_BASE_URL")
MODEL = "gemini-2.0-flash"

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(api_key= gemini_api_key,base_url= base_url)



async def main():
    print("Welcome to the Game Master Agent. Let's begin the adventure!")
    current_agent = narratoragent
    # Initial context for the game. 'explore' is a sensible default for the narrator.
    while True:
        user_start_input = input("\nType 'start' to begin your adventure, or 'quit' to exit: ").lower()
        try:
            if user_start_input == "quit":
                print("AI Agent: Goodbye! Thanks for playing.")
                break
            elif user_start_input == "start":
                print("\nAI Agent: The NarratorAgent begins the story...")
                # The 'input' to the Runner is the initial context.
                # The Runner will manage the handoffs automatically based on agent instructions.
                result = await Runner.run(current_agent, input=user_start_input)
                print(f"\nAI Agent: {result.final_output}")
        except Exception as e:
            print(f"An error occurred during the game turn: {e}")
            print("AI Agent: I apologize, an error occurred. Let's try to reset or you can quit.")
            
        

if __name__ == "__main__":
  asyncio.run(main())
