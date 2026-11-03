"""
Ollama Service Module for 'Reasoning Is All You Need'
Communicates with local Ollama instance running llama3.2:1b.
No external APIs, cloud LLMs, or API keys are used.
"""

import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:1b"

_ollama_status_cache = {"last_check": 0.0, "is_running": False}

def is_ollama_running(cache_ttl: float = 3.0) -> bool:
    """
    Check if the local Ollama server is accessible with short caching to keep UI ultra responsive.
    """
    now = time.time()
    if now - _ollama_status_cache["last_check"] < cache_ttl:
        return _ollama_status_cache["is_running"]
        
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=0.6)
        is_running = (response.status_code == 200)
    except requests.RequestException:
        is_running = False
        
    _ollama_status_cache["last_check"] = now
    _ollama_status_cache["is_running"] = is_running
    return is_running

_models_cache = {"last_check": 0.0, "models": []}

def get_installed_models(cache_ttl: float = 5.0) -> list:
    """
    Return list of installed local Ollama models with caching.
    """
    now = time.time()
    if now - _models_cache["last_check"] < cache_ttl:
        return _models_cache["models"]
        
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=0.8)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            models_list = [m.get("name", "") for m in models_data]
            _models_cache["last_check"] = now
            _models_cache["models"] = models_list
            return models_list
        return []
    except Exception:
        return []

def is_model_available(model_name: str = DEFAULT_MODEL) -> bool:
    """
    Check if the specified model is pulled in local Ollama.
    """
    models = get_installed_models()
    for name in models:
        if model_name in name or name in model_name:
            return True
    return False

def generate_response(prompt: str, system_prompt: str = None, model: str = DEFAULT_MODEL, temperature: float = 0.2, max_tokens: int = 250) -> dict:
    """
    Send prompt to local Ollama server and return text response.
    """
    if not is_ollama_running() or not is_model_available(model):
        return {
            "success": False,
            "response": "",
            "model": model,
            "error": "Ollama is not running or model is not installed. Please start Ollama and run 'ollama pull llama3.2:1b'."
        }

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=12.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", "").strip(),
                "model": model,
                "error": None
            }
        else:
            return {
                "success": False,
                "response": "",
                "model": model,
                "error": f"Ollama returned HTTP {response.status_code}: {response.text}"
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "response": "",
            "model": model,
            "error": "Ollama request timed out."
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "response": "",
            "model": model,
            "error": f"Error connecting to Ollama: {str(e)}"
        }
