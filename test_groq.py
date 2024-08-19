import os
import sys
import subprocess
import venv
from pathlib import Path
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

load_dotenv()

config_list = [
    {
        "model": "llama3-8b-8192",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "api_type": "groq",
    }
]

# Setting up the code executor
workdir = Path("coding")
workdir.mkdir(exist_ok=True)
venv_path = workdir / "venv"

# Create the venv only if it doesn't exist
if not venv_path.exists():
    print("Creating new virtual environment...")
    venv.create(venv_path, with_pip=True)

# Activate the virtual environment

activate_script = venv_path / "bin" / "activate"
activation_command = f"source {activate_script}"
subprocess.run(activation_command, shell=True)

# Update sys.path
#sys.path.insert(0, str(venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"))

def install_packages(packages):
    if isinstance(packages, str):
        packages = [packages]
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    return f"Successfully installed: {', '.join(packages)}"

code_executor = LocalCommandLineCodeExecutor(work_dir=workdir)#, venv_path=venv_path)

system_message = """You are a helpful AI assistant who writes code and the user executes it.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) for the user to execute.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If you need to install packages, use the install_packages function. For example: install_packages(["numpy", "pandas"])
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
IMPORTANT: Wait for the user to execute your code and then you can reply with the word "FINISH". DO NOT OUTPUT "FINISH" after your code block."""

user_proxy_agent = UserProxyAgent(
    name="User",
    code_execution_config={"executor": code_executor},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda msg: "FINISH" in msg.get("content"),
    function_map={"install_packages": install_packages}
)

assistant_agent = AssistantAgent(
    name="Groq Assistant",
    system_message=system_message,
    llm_config={"config_list": config_list},
)

chat_result = user_proxy_agent.initiate_chat(
    assistant_agent,
    message="Provide code to count the number of prime numbers from 1 to 10000.",
)

# Print the chat result
print("Chat Result:")
print(chat_result)

