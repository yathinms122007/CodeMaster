import os
from dotenv import load_dotenv
from groq import Groq
from database import (
    init_db,
    save_message,
    get_recent_messages,
    add_improvement_note,
    get_improvement_notes
)

# 1. Load secret variables and initialize the SQLite database
load_dotenv()
init_db()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found! Check your .env file.")

client = Groq(api_key=api_key)

def build_system_prompt():
    """Builds the system prompt and attaches any saved improvement notes from the DB."""
    base_prompt = (
        "You are a helpful AI assistant helping a 2nd-year engineering student "
        "learn software development, coding, and placement preparation."
    )
    notes = get_improvement_notes()
    if notes:
        rules = "\n".join(f"- {n}" for n in notes)
        base_prompt += f"\n\nIMPORTANT - Follow these user preferences learned from past chats:\n{rules}"
    return {"role": "system", "content": base_prompt}

print("Chatbot with SQLite Database is ready!")
print("Commands: Type 'exit' to quit, or '/improve <rule>' to teach the bot how to answer better.\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue

    if user_input.lower() in ["exit", "bye", "end"]:
        print("AI : Goodbye! Your chat is safely saved in chat_history.db.")
        break

    # Special command to teach/improve the chatbot
    if user_input.lower().startswith("/improve "):
        rule = user_input[9:].strip()
        add_improvement_note(rule)
        print(f"✅ Saved improvement rule to database: '{rule}'\n")
        continue

    # Save user message to SQLite database
    save_message("user", user_input)

    # Load system prompt (with improvements) + recent chat history from database
    messages = [build_system_prompt()] + get_recent_messages(limit=10)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )
    reply = response.choices[0].message.content
    print("\nAI :", reply, "\n")

    # Save AI reply to SQLite database
    save_message("assistant", reply)