# config.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()  # Loads from .env if present

# Make sure you set this in environment or .env file
# OPENAI_API_KEY=your_key_here

def get_llm(model_name: str = "gpt-3.5-turbo", temperature: float = 0.2):
    """
    Returns a ChatOpenAI LLM instance.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Please set it in environment or .env file.")
    return ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=api_key)

def get_embeddings(model_name: str = "text-embedding-3-small"):
    """
    Returns an OpenAIEmbeddings instance.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Please set it in environment or .env file.")
    return OpenAIEmbeddings(model=model_name, openai_api_key=api_key)
