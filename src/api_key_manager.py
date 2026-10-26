"""
API Key Rotation Manager for Groq
Automatically switches to next API key when rate limit hit
"""

import os
from groq import Groq
import time


class APIKeyManager:
    """Manages multiple API keys with automatic rotation on rate limits"""
    
    def __init__(self, api_keys=None):
        """
        Initialize with list of API keys
        
        Args:
            api_keys: List of API keys. If None, reads from .env
        """
        api_keys=[
                  ]
        if api_keys is None:
            # Read from .env file
            api_keys = self._load_keys_from_env()
        
        self.api_keys = api_keys
        self.current_key_index = 0
        self.clients = [Groq(api_key=key) for key in api_keys]
        
        print(f"✓ Loaded {len(self.api_keys)} API keys")
    
    def _load_keys_from_env(self):
        """Load API keys from .env file"""
        keys = []
        
        # Try to load multiple keys from .env
        # Format: GROQ_API_KEY_1, GROQ_API_KEY_2, etc.
        for i in range(1, 11):  # Support up to 10 keys
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if key:
                keys.append(key)
        
        # Also try single key
        single_key = os.getenv("GROQ_API_KEY")
        if single_key and single_key not in keys:
            keys.insert(0, single_key)
        
        if not keys:
            raise ValueError("No API keys found! Add GROQ_API_KEY or GROQ_API_KEY_1, GROQ_API_KEY_2, etc. to .env")
        
        return keys
    
    def get_client(self):
        """Get current active Groq client"""
        return self.clients[self.current_key_index]
    
    def rotate_key(self):
        """Switch to next API key"""
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        print(f"\n⚠️  Rotating API key: Key {old_index + 1} → Key {self.current_key_index + 1}")
        
        # Return True if we cycled through all keys
        return old_index >= self.current_key_index
    
    def call_with_retry(self, model, messages, temperature=0.7, max_tokens=2000, max_retries=None):
        """
        Call API with automatic key rotation on rate limits
        
        Args:
            model: Model name
            messages: Chat messages
            temperature: Temperature
            max_tokens: Max tokens
            max_retries: Max retries (default: number of keys)
            
        Returns:
            API response
        """
        if max_retries is None:
            max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                client = self.get_client()
                
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if rate limit error
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    print(f"⚠️  Rate limit hit on key {self.current_key_index + 1}")
                    
                    # Rotate to next key
                    cycled = self.rotate_key()
                    
                    if cycled and attempt == len(self.api_keys) - 1:
                        # We've tried all keys
                        print("\n❌ All API keys exhausted!")
                        print("Please wait 10-15 minutes or add more API keys to .env")
                        raise
                    
                    # Small delay before retry
                    time.sleep(1)
                    continue
                else:
                    # Not a rate limit error, raise immediately
                    raise
        
        raise Exception("Max retries exceeded")


# TEST
if __name__ == "__main__":
    print("="*70)
    print("TESTING API KEY ROTATION")
    print("="*70)
    
    try:
        manager = APIKeyManager()
        
        print(f"\nTesting with {len(manager.api_keys)} keys...")
        
        # Test call
        response = manager.call_with_retry(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "user", "content": "Say 'API key rotation working!'"}
            ],
            max_tokens=50
        )
        
        print("\n✓ API call successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")