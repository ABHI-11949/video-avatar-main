import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import json
import os
from ..config import Config
import logging

logger = logging.getLogger(__name__)

class LipSyncEngine:
    def __init__(self, avatar_path=Config.AVATAR_PATH):
        self.avatar_path = avatar_path
        self.avatar = self.load_avatar()
        
        # Define mouth regions for different visemes
        self.mouth_shapes = {
            'viseme_silence': {'width': 30, 'height': 5, 'x_offset': 0, 'y_offset': 0},
            'viseme_aa': {'width': 40, 'height': 15, 'x_offset': 0, 'y_offset': 0},
            'viseme_ii': {'width': 25, 'height': 20, 'x_offset': 5, 'y_offset': -2},
            'viseme_uu': {'width': 35, 'height': 10, 'x_offset': 0, 'y_offset': 5},
            'viseme_e': {'width': 35, 'height': 8, 'x_offset': 0, 'y_offset': -3},
            'viseme_o': {'width': 30, 'height': 12, 'x_offset': 0, 'y_offset': 2},
            'viseme_k': {'width': 32, 'height': 8, 'x_offset': -2, 'y_offset': 0},
            'viseme_g': {'width': 34, 'height': 9, 'x_offset': 1, 'y_offset': 1},
            'viseme_ch': {'width': 28, 'height': 7, 'x_offset': 0, 'y_offset': -1},
            'viseme_j': {'width': 30, 'height': 8, 'x_offset': 0, 'y_offset': 0},
            'viseme_t': {'width': 25, 'height': 6, 'x_offset': 3, 'y_offset': 0},
            'viseme_d': {'width': 27, 'height': 7, 'x_offset': -2, 'y_offset': 0},
            'viseme_n': {'width': 26, 'height': 6, 'x_offset': 0, 'y_offset': 0},
            'viseme_m': {'width': 28, 'height': 7, 'x_offset': 0, 'y_offset': 0},
            'viseme_p': {'width': 30, 'height': 5, 'x_offset': 0, 'y_offset': 2},
            'viseme_b': {'width': 32, 'height': 6, 'x_offset': 0, 'y_offset': 1},
            'viseme_y': {'width': 28, 'height': 8, 'x_offset': -1, 'y_offset': -1},
            'viseme_r': {'width': 25, 'height': 7, 'x_offset': 0, 'y_offset': 0},
            'viseme_l': {'width': 24, 'height': 6, 'x_offset': 2, 'y_offset': 0},
            'viseme_v': {'width': 30, 'height': 7, 'x_offset': -2, 'y_offset': 0},
            'viseme_s': {'width': 22, 'height': 5, 'x_offset': 0, 'y_offset': 1},
            'viseme_h': {'width': 28, 'height': 8, 'x_offset': 0, 'y_offset': 0}
        }
        
    def load_avatar(self):
        """Load avatar image"""
        if os.path.exists(self.avatar_path):
            avatar = cv2.imread(self.avatar_path)
            if avatar is not None:
                return cv2.cvtColor(avatar, cv2.COLOR_BGR2RGB)
        
        # Create default avatar if not exists
        return self.create_default_avatar()
        
    def create_default_avatar(self):
        """Create a default avatar image"""
        # Create a simple face
        img = Image.new('RGB', (512, 512), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw face outline
        draw.ellipse([100, 50, 412, 462], outline='black', width=3)
        
        # Draw eyes
        draw.ellipse([180, 150, 230, 200], fill='white', outline='black')
        draw.ellipse([282, 150, 332, 200], fill='white', outline='black')
        draw.ellipse([200, 170, 210, 180], fill='black')
        draw.ellipse([302, 170, 312, 180], fill='black')
        
        # Draw mouth area (will be animated)
        draw.ellipse([206, 300, 306, 350], fill='red', outline='black')
        
        return np.array(img)
        
    def apply_lip_sync(self, viseme_sequence, fps=Config.VIDEO_FPS):
        """Apply lip sync animation based on viseme sequence"""
        try:
            frames = []
            
            # Calculate total duration
            if viseme_sequence:
                total_duration = max(v['end'] for v in viseme_sequence)
            else:
                total_duration = 5  # Default 5 seconds
                
            num_frames = int(total_duration * fps)
            
            for frame_num in range(num_frames):
                current_time = frame_num / fps
                
                # Find active viseme at current time
                active_viseme = self.find_active_viseme(viseme_sequence, current_time)
                
                # Generate frame with current mouth shape
                frame = self.generate_frame(active_viseme)
                frames.append(frame)
                
            logger.info(f"Generated {len(frames)} frames for lip sync")
            return frames
            
        except Exception as e:
            logger.error(f"Error in lip sync: {e}")
            return []
            
    def find_active_viseme(self, viseme_sequence, current_time):
        """Find active viseme at given time"""
        for viseme in viseme_sequence:
            if viseme['start'] <= current_time <= viseme['end']:
                return viseme
        return {'viseme': 'viseme_silence', 'blend': 0}
        
    def generate_frame(self, viseme_info):
        """Generate a single frame with mouth shape"""
        try:
            frame = self.avatar.copy()
            
            # Get mouth shape parameters
            viseme_name = viseme_info['viseme']
            mouth_params = self.mouth_shapes.get(viseme_name, self.mouth_shapes['viseme_silence'])
            
            # Define mouth region (assuming face is centered)
            mouth_center = (256, 325)  # Adjust based on avatar
            blend = viseme_info.get('blend', 0)
            
            # Draw mouth shape
            img = Image.fromarray(frame)
            draw = ImageDraw.Draw(img)
            
            # Apply shape with blending
            width = int(mouth_params['width'] * (1 + blend * 0.2))
            height = int(mouth_params['height'] * (1 + blend * 0.2))
            x_offset = mouth_params['x_offset']
            y_offset = mouth_params['y_offset']
            
            x1 = mouth_center[0] - width // 2 + x_offset
            y1 = mouth_center[1] - height // 2 + y_offset
            x2 = mouth_center[0] + width // 2 + x_offset
            y2 = mouth_center[1] + height // 2 + y_offset
            
            # Draw mouth with some gradient
            for i in range(3):
                alpha = 1 - i * 0.3
                offset = i * 2
                draw.ellipse(
                    [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                    fill=(int(255 * alpha), int(100 * alpha), int(100 * alpha))
                )
                
            # Apply slight blur for smoothness
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
            
            return np.array(img)
            
        except Exception as e:
            logger.error(f"Error generating frame: {e}")
            return self.avatar