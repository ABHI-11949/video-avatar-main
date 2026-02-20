import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server Config
    HOST = os.getenv('HOST', 'localhost')
    PORT = int(os.getenv('PORT', 8765))
    
    # Paths
    AVATAR_PATH = os.getenv('AVATAR_PATH', 'avatars/default_avatar.png')
    OUTPUT_PATH = os.getenv('OUTPUT_PATH', 'outputs/')
    
    # TTS Config
    TTS_LANGUAGE = os.getenv('TTS_LANGUAGE', 'hi')  # Hindi
    TTS_TLD = os.getenv('TTS_TLD', 'co.in')  # India domain for Google TTS
    
    # STT Config
    STT_LANGUAGE = os.getenv('STT_LANGUAGE', 'hi-IN')
    
    # Video Config
    VIDEO_FPS = int(os.getenv('VIDEO_FPS', 30))
    VIDEO_CODEC = os.getenv('VIDEO_CODEC', 'libx264')
    
    # Create directories if not exists
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs('avatars', exist_ok=True)