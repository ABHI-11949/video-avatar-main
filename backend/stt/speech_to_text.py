import speech_recognition as sr
import asyncio
import io
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class SpeechToText:
    def __init__(self, language='hi-IN'):
        self.recognizer = sr.Recognizer()
        self.language = language
        
    async def convert_audio_to_text(self, audio_data):
        """Convert audio bytes to text"""
        try:
            # Convert audio bytes to AudioSegment
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
            
            # Convert to WAV for speech recognition
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Use speech recognition
            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)
                
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized text: {text}")
            
            return text
            
        except sr.UnknownValueError:
            logger.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in speech to text: {e}")
            return None
            
    async def process_audio_stream(self, audio_generator):
        """Process continuous audio stream"""
        async for audio_chunk in audio_generator:
            text = await self.convert_audio_to_text(audio_chunk)
            if text:
                yield text