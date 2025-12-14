# create_sounds.py
import pygame
import numpy as np
import os

def create_all_sounds():
    """Create all placeholder sound files"""
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    if not os.path.exists('sounds'):
        os.makedirs('sounds')
    
    # Sound definitions
    sounds = [
        ('chatbug_hit', 400, 0.2, 'square', 0.4),
        ('notifbug_hit', 600, 0.3, 'square', 0.5),
        ('popupbug_hit', 300, 0.4, 'sine', 0.4),
        ('floworb_collect', 800, 0.3, 'sine', 0.3),
        ('level_complete', [800, 1000, 1200], 1.0, 'sine', 0.5),
        ('game_over', 200, 1.0, 'sawtooth', 0.5),
        ('level_start', 600, 0.5, 'sine', 0.4),
        ('answer_correct', 1000, 0.5, 'sine', 0.4),
        ('answer_wrong', 300, 0.4, 'square', 0.4),
        ('button_click', 500, 0.1, 'square', 0.3),
        ('menu_select', 600, 0.15, 'sine', 0.3),
        ('hover', 700, 0.1, 'sine', 0.2),
    ]
    
    for name, freq, duration, wave_type, volume in sounds:
        create_sound_file(name, freq, duration, wave_type, volume)
    
    print("All placeholder sounds created in 'sounds/' folder!")

def create_sound_file(name, frequency, duration, wave_type='sine', volume=0.3):
    """Create and save a sound file"""
    sample_rate = 22050
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
    
    # Convert to int16
    sound_array = np.int16(wave * 32767)
    
    # Save as WAV file
    import wave
    with wave.open(f'sounds/{name}.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(sound_array.tobytes())
    
    print(f"Created: sounds/{name}.wav")

if __name__ == "__main__":
    create_all_sounds()