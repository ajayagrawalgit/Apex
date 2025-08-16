from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    model=LiteLlm(
        model="openai/Llama-3.2-1B-Instruct-GGUF/Llama-3.2-1B-Instruct-Q8_0.gguf",  # Add 'openai/' prefix
        api_base="http://192.168.30.1:6969/v1",  # LM Studio OpenAI-compatible API URL
        api_key="none",
        litellm_provider="openai"  # Explicit provider
    ),
    name="Mickey",
    instruction="Your name is Mickey. Just be friendly. If user asks for your name, reply with your name."
)
