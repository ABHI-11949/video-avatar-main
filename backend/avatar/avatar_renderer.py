import cv2
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip
import os
from ..config import Config
import logging
import uuid

logger = logging.getLogger(__name__)

class AvatarRenderer:
    def __init__(self, output_path=Config.OUTPUT_PATH):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        
    def render_video(self, frames, audio_data, fps=Config.VIDEO_FPS):
        """Render frames with audio to video file"""
        try:
            # Generate unique filename
            video_id = str(uuid.uuid4())
            video_path = f"{self.output_path}/{video_id}.mp4"
            audio_path = f"{self.output_path}/{video_id}_audio.mp3"
            
            # Save audio temporarily
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
                
            # Create video from frames
            if frames:
                # Convert frames to RGB if needed
                rgb_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if len(frame.shape) == 3 else frame 
                            for frame in frames]
                
                # Create video clip
                clip = ImageSequenceClip(rgb_frames, fps=fps)
                
                # Add audio
                audio_clip = AudioFileClip(audio_path)
                final_clip = clip.set_audio(audio_clip)
                
                # Write video file
                final_clip.write_videofile(
                    video_path,
                    codec=Config.VIDEO_CODEC,
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                # Clean up temporary audio
                os.remove(audio_path)
                
                logger.info(f"Video rendered successfully: {video_path}")
                return video_path
                
            else:
                logger.error("No frames to render")
                return None
                
        except Exception as e:
            logger.error(f"Error rendering video: {e}")
            # Clean up temp files if they exist
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return None
            
    def render_realtime_stream(self, frame_generator, audio_generator):
        """Render real-time stream (for WebRTC)"""
        # This would stream frames directly to WebRTC
        # Implementation depends on streaming protocol
        
        for frame in frame_generator:
            # Encode frame and send via WebRTC
            yield frame
            
    def save_video(self, video_path):
        """Save and return video file path"""
        if os.path.exists(video_path):
            return video_path
        return None