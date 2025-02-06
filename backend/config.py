from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Player Configuration - matches frontend src/config/ai.ts
AI_PLAYERS: List[Dict[str, str]] = [
    {'id': 'gpt4', 'name': 'GPT-4', 'api_type': 'openai', 'model': 'gpt-4'},
    {'id': 'claude2', 'name': 'Claude 2', 'api_type': 'anthropic', 'model': 'claude-2'},
    {'id': 'gemini', 'name': 'Gemini Pro', 'api_type': 'google', 'model': 'gemini-pro'},
    {'id': 'perplexity', 'name': 'Perplexity', 'api_type': 'perplexity', 'model': 'deepseek-coder-33b-instruct'}
]

# API Configuration
API_KEYS = {
    'openai': os.getenv('OPENAI_API_KEY'),
    'anthropic': os.getenv('ANTHROPIC_API_KEY'),
    'google': os.getenv('GOOGLE_API_KEY'),
    'perplexity': os.getenv('PERPLEXITY_API_KEY')
}

def get_ai_config(player_id: str) -> Dict[str, str]:
    """Get AI configuration by player ID."""
    for player in AI_PLAYERS:
        if player['id'] == player_id:
            return {
                'api_type': player['api_type'],
                'api_key': API_KEYS[player['api_type']],
                'model': player['model']
            }
    raise ValueError(f"Unknown AI player ID: {player_id}")

def validate_api_keys() -> bool:
    """Validate that all required API keys are present."""
    missing_keys = [api_type for api_type, key in API_KEYS.items() if not key]
    if missing_keys:
        print(f"Warning: Missing API keys for: {', '.join(missing_keys)}")
        return False
    return True

# Validate API keys on module load
if not validate_api_keys():
    print("Warning: Some API keys are missing. Check your .env file.")
