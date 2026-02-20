import json
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VisemeGenerator:
    def __init__(self):
        # Viseme mapping for Hindi/English
        self.viseme_map = {
            # Vowels
            'a': 'viseme_aa', 'aa': 'viseme_aa',
            'i': 'viseme_ii', 'ii': 'viseme_ii',
            'u': 'viseme_uu', 'uu': 'viseme_uu',
            'e': 'viseme_e', 'ee': 'viseme_e',
            'o': 'viseme_o', 'oo': 'viseme_o',
            
            # Consonants
            'k': 'viseme_k', 'kh': 'viseme_k',
            'g': 'viseme_g', 'gh': 'viseme_g',
            'c': 'viseme_ch', 'ch': 'viseme_ch',
            'j': 'viseme_j', 'jh': 'viseme_j',
            't': 'viseme_t', 'th': 'viseme_t',
            'd': 'viseme_d', 'dh': 'viseme_d',
            'n': 'viseme_n', 'm': 'viseme_m',
            'p': 'viseme_p', 'ph': 'viseme_p',
            'b': 'viseme_b', 'bh': 'viseme_b',
            'y': 'viseme_y', 'r': 'viseme_r',
            'l': 'viseme_l', 'v': 'viseme_v',
            's': 'viseme_s', 'sh': 'viseme_s',
            'h': 'viseme_h',
            
            # Silence/rest
            ' ': 'viseme_silence',
            '.': 'viseme_silence',
            ',': 'viseme_silence',
            '?': 'viseme_silence',
            '!': 'viseme_silence'
        }
        
    def text_to_visemes(self, text, timings):
        """Convert text to viseme sequence with timings"""
        try:
            viseme_sequence = []
            
            for timing in timings:
                word = timing['word'].lower()
                word_duration = timing['end'] - timing['start']
                
                # Process each character in word
                char_duration = word_duration / len(word)
                
                for i, char in enumerate(word):
                    char_time = timing['start'] + (i * char_duration)
                    viseme = self.viseme_map.get(char, 'viseme_silence')
                    
                    viseme_sequence.append({
                        'viseme': viseme,
                        'start': char_time,
                        'end': char_time + char_duration,
                        'blend': 0.1  # Blend factor for smooth transition
                    })
                    
            return viseme_sequence
            
        except Exception as e:
            logger.error(f"Error generating visemes: {e}")
            return []
            
    def get_phonemes_from_audio(self, audio_data, sample_rate=16000):
        """Extract phonemes from audio (simplified version)"""
        # This is a simplified version
        # In production, use a proper phoneme recognition model
        
        duration = len(audio_data) / sample_rate
        num_phonemes = int(duration * 10)  # Assume ~10 phonemes per second
        
        phonemes = []
        for i in range(num_phonemes):
            start_time = i * 0.1
            end_time = min((i + 1) * 0.1, duration)
            
            # Simplified phoneme detection
            phoneme = {
                'phoneme': 'sil' if i % 3 == 0 else 'aa',
                'start': start_time,
                'end': end_time,
                'confidence': 0.8
            }
            phonemes.append(phoneme)
            
        return phonemes