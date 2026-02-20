import asyncio
import websockets
import json
import logging
from .webrtc.signaling import WebRTCSignaling
from .stt.speech_to_text import SpeechToText
from .tts.text_to_speech import TextToSpeech
from .viseme.viseme_generator import VisemeGenerator
from .lipsync.lip_sync_engine import LipSyncEngine
from .avatar.avatar_renderer import AvatarRenderer
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAvatarSystem:
    def __init__(self):
        self.signaling = WebRTCSignaling()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.viseme_gen = VisemeGenerator()
        self.lipsync = LipSyncEngine()
        self.renderer = AvatarRenderer()
        
    async def process_audio_to_video(self, audio_data):
        """Main pipeline: Audio -> Text -> Speech -> Viseme -> LipSync -> Video"""
        try:
            # Step 1: Speech to Text
            logger.info("Converting speech to text...")
            text = await self.stt.convert_audio_to_text(audio_data)
            
            if not text:
                logger.error("No text recognized")
                return None
                
            # Step 2: Send text to external LLM (not our responsibility)
            # The client will handle sending to LLM and getting response
            # We'll receive the response text from client
            
            # Step 3: Text to Speech (when we get response from client)
            # This will be called separately when client sends LLM response
            
            return text
            
        except Exception as e:
            logger.error(f"Error in pipeline: {e}")
            return None
            
    async def generate_avatar_response(self, text_response):
        """Generate avatar video from text response"""
        try:
            # Step 3: Text to Speech with timings
            logger.info("Generating speech from text...")
            audio_data, timings = await self.tts.generate_with_timings(text_response)
            
            if not audio_data:
                return None
                
            # Step 4: Generate visemes from text
            logger.info("Generating visemes...")
            viseme_sequence = self.viseme_gen.text_to_visemes(text_response, timings)
            
            # Step 5: Apply lip sync
            logger.info("Applying lip sync...")
            frames = self.lipsync.apply_lip_sync(viseme_sequence)
            
            # Step 6: Render video
            logger.info("Rendering final video...")
            video_path = self.renderer.render_video(frames, audio_data)
            
            return video_path
            
        except Exception as e:
            logger.error(f"Error generating avatar response: {e}")
            return None
            
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'audio':
                    # Process incoming audio
                    audio_data = bytes(data['audio'])
                    text = await self.process_audio_to_video(audio_data)
                    
                    # Send recognized text to client
                    await websocket.send(json.dumps({
                        'type': 'text',
                        'text': text
                    }))
                    
                elif data['type'] == 'llm_response':
                    # Generate avatar video from LLM response
                    video_path = await self.generate_avatar_response(data['text'])
                    
                    # Send video path or video data back
                    if video_path:
                        with open(video_path, 'rb') as f:
                            video_data = f.read()
                            
                        await websocket.send(json.dumps({
                            'type': 'video',
                            'video': list(video_data),
                            'path': video_path
                        }))
                        
                elif data['type'] == 'webrtc':
                    # Handle WebRTC signaling
                    await self.signaling.handle_signaling(websocket, data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in websocket handler: {e}")

async def main():
    """Main entry point"""
    system = AIAvatarSystem()
    
    async with websockets.serve(
        system.handle_websocket,
        Config.HOST,
        Config.PORT
    ):
        logger.info(f"AI Avatar System running on ws://{Config.HOST}:{Config.PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())