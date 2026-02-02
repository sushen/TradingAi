import wave
import struct
import math

filename = "beep.wav"
framerate = 44100
duration = 0.15   # seconds
frequency = 1000  # Hz
amplitude = 16000

wav = wave.open(filename, "w")
wav.setparams((1, 2, framerate, 0, "NONE", "not compressed"))

for i in range(int(duration * framerate)):
    value = int(amplitude * math.sin(2 * math.pi * frequency * i / framerate))
    wav.writeframes(struct.pack('<h', value))

wav.close()
print("beep.wav created")
