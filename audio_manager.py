# audio_manager.py
import pygame
import os
import numpy as np

class AudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_volume = 0.3
        self.sfx_volume = 0.7
        self.load_sounds()
    
    def load_sounds(self):
        """Load semua efek suara"""
        sound_files = {
            # Bug interactions
            'chatbug_hit': 'sounds/chatbug_hit.wav',
            'notifbug_hit': 'sounds/notifbug_hit.wav',
            'popupbug_hit': 'sounds/popupbug_hit.wav',
            
            # Positive interactions
            'floworb_collect': 'sounds/floworb_collect.wav',
            'level_complete': 'sounds/level_complete.wav',
            'level_start': 'sounds/level_start.wav',
            
            # Game state
            'game_over': 'sounds/game_over.wav',
            
            # Question feedback
            'answer_correct': 'sounds/answer_correct.wav',
            'answer_wrong': 'sounds/answer_wrong.wav',
            
            # UI sounds
            'button_click': 'sounds/button_click.wav',
            'menu_select': 'sounds/menu_select.wav',
            'hover': 'sounds/hover.wav',
            
            'music_background': 'sounds/background_music.mp3'
        }
        
        # Buat folder sounds jika belum ada
        if not os.path.exists('sounds'):
            os.makedirs('sounds')
            print("Folder 'sounds' created. Please add your sound files!")
        
        # Load sounds
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.sfx_volume)
                else:
                    # Create placeholder sound
                    self.create_placeholder_sound(name)
                    print(f"Created placeholder sound: {name}")
            except Exception as e:
                print(f"Error loading {path}: {e}")
                self.create_placeholder_sound(name)
    
    def create_placeholder_sound(self, name):
        """Create simple placeholder sound"""
        sample_rate = 22050
        
        # Tentukan parameter berdasarkan jenis suara
        if 'hit' in name:
            # Bug hit sounds
            if 'chat' in name:
                frequency = 400
                duration = 0.2
                wave_type = 'square'
            elif 'notif' in name:
                frequency = 600
                duration = 0.3
                wave_type = 'square'
            elif 'popup' in name:
                frequency = 300
                duration = 0.4
                wave_type = 'sine'
            volume = 0.4
        elif 'collect' in name:
            # Positive collection
            frequency = 800
            duration = 0.3
            wave_type = 'sine'
            volume = 0.3
        elif 'correct' in name:
            # Correct answer
            frequency = 1000
            duration = 0.5
            wave_type = 'sine'
            volume = 0.4
        elif 'wrong' in name:
            # Wrong answer
            frequency = 300
            duration = 0.4
            wave_type = 'square'
            volume = 0.4
        elif 'game_over' in name:
            # Game over
            frequency = 200
            duration = 1.0
            wave_type = 'sawtooth'
            volume = 0.5
        elif 'complete' in name:
            # Level complete
            frequency = [800, 1000, 1200]
            duration = 1.0
            wave_type = 'sine'
            volume = 0.5
        elif 'start' in name:
            # Level start
            frequency = 600
            duration = 0.5
            wave_type = 'sine'
            volume = 0.4
        elif 'click' in name:
            # Button click
            frequency = 500
            duration = 0.1
            wave_type = 'square'
            volume = 0.3
        elif 'select' in name:
            # Menu select
            frequency = 600
            duration = 0.15
            wave_type = 'sine'
            volume = 0.3
        elif 'hover' in name:
            # Hover sound
            frequency = 700
            duration = 0.1
            wave_type = 'sine'
            volume = 0.2
        else:
            # Default
            frequency = 500
            duration = 0.2
            wave_type = 'sine'
            volume = 0.3
        
        # Generate simple sound
        samples = np.arange(int(duration * sample_rate))
        
        if isinstance(frequency, list):
            # Chord sound
            wave = np.zeros_like(samples, dtype=np.float32)
            for freq in frequency:
                wave += np.sin(2 * np.pi * freq * samples / sample_rate)
            wave = wave / len(frequency)
        elif wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * samples / sample_rate)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * samples / sample_rate))
        elif wave_type == 'sawtooth':
            wave = 2 * (samples * frequency / sample_rate % 1) - 1
        
        # Apply envelope
        attack = int(0.1 * len(wave))
        decay = int(0.3 * len(wave))
        release = int(0.2 * len(wave))
        
        envelope = np.ones_like(wave)
        if attack > 0:
            envelope[:attack] = np.linspace(0, 1, attack)
        if decay > 0:
            envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
        if release > 0:
            envelope[-release:] = np.linspace(envelope[-release-1], 0, release)
        
        wave = wave * envelope * volume
        
        # Convert to pygame sound
        sound_array = np.int16(wave * 32767)
        sound = pygame.sndarray.make_sound(sound_array.reshape(-1, 1))
        
        self.sounds[name] = sound
        self.sounds[name].set_volume(self.sfx_volume)
    
    def play(self, sound_name, volume_mult=1.0):
        """Play a sound effect"""
        if sound_name in self.sounds:
            current_volume = self.sfx_volume * volume_mult
            self.sounds[sound_name].set_volume(min(1.0, current_volume))
            self.sounds[sound_name].play()
    
    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def play_music(self, filepath, loops=-1):
        """Play background music"""
        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
        else:
            print(f"Music file not found: {filepath}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()