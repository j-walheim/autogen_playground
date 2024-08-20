import os
from dotenv import load_dotenv
from autogen import ConversableAgent

load_dotenv()
config_list = [
    {
        "model": "llama3-8b-8192",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "api_type": "groq",
    }
]

assistant = ConversableAgent(
    "assistant",
    system_message="You are a helpful AI assistant.",
    llm_config={
        "config_list": config_list
    },
    human_input_mode="NEVER",  # Never ask for human input.
)

# Initialize conversation history
conversation_history = []

# Function to send a message and get a response
def send_message(message):
    conversation_history.append({"role": "user", "content": message})
    res = assistant.generate_reply(messages=conversation_history)
    response = res["content"]
    # Ensure the response is a non-empty string
    if not isinstance(response, str) or not response.strip():
        response = "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"
    
    conversation_history.append({"role": "assistant", "content": response})
    return response


# First message
first_question = "What is the capital of France?"
print("User:", first_question)
print("Assistant:", send_message(first_question))

# Second message
second_question = "What's a famous landmark there?"
print("\nUser:", second_question)
print("Assistant:", send_message(second_question))

# You can continue adding more messages as needed
