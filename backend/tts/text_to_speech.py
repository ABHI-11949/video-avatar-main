from gtts import gTTS
import io
import asyncio
import hashlib
import os
from ..config import Config
import logging

logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self, language=Config.TTS_LANGUAGE, tld=Config.TTS_TLD):
        self.language = language
        self.tld = tld
        self.cache_dir = "cache/tts"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    async def generate_speech(self, text):
        """Convert text to speech audio"""
        try:
            # Generate cache key
            cache_key = hashlib.md5(f"{text}_{self.language}".encode()).hexdigest()
            cache_path = f"{self.cache_dir}/{cache_key}.mp3"
            
            # Check cache
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    audio_data = f.read()
                return audio_data
                
            # Generate speech
            tts = gTTS(text=text, lang=self.language, tld=self.tld, slow=False)
            
            # Save to bytes
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            audio_data = audio_bytes.read()
            
            # Cache the audio
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
                
            logger.info(f"Generated speech for text: {text[:50]}...")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error in text to speech: {e}")
            return None
            
    async def generate_with_timings(self, text):
        """Generate speech with word timings for viseme sync"""
        try:
            # Generate audio
            audio_data = await self.generate_speech(text)
            
            if not audio_data:
                return None, None
                
            # Calculate approximate word timings (simplified)
            words = text.split()
            word_duration = len(audio_data) / (len(words) * 16000)  # Rough estimate
            
            timings = []
            current_time = 0
            
            for word in words:
                timings.append({
                    'word': word,
                    'start': current_time,
                    'end': current_time + word_duration
                })
                current_time += word_duration
                
            return audio_data, timings
            
        except Exception as e:
            logger.error(f"Error generating speech with timings: {e}")
            return None, None