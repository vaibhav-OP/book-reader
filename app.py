import io
import os
import wave
import soundfile as sf
import sounddevice as sd
from piper import PiperVoice
import threading
import queue
from colorama import Style, init

init(autoreset=True)    
voice = PiperVoice.load("./en_US-lessac-medium.onnx")

with open("text.txt", "r", encoding="utf-8") as f:
    chunks = f.read().splitlines()

audio_queue = queue.Queue()

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def synthesize_chunks():
    for i, chunk in enumerate(chunks):
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            voice.synthesize_wav(chunk, wav_file)
        buffer.seek(0)
        audio_queue.put((i, buffer))
    audio_queue.put(None)

def play_chunks():
    while True:
        item = audio_queue.get()
        if item is None:
            break
        i, buffer = item
        
        clear_console()
        line_prev = chunks[i-1] if i > 0 else ""
        line_next = chunks[i+1] if i < len(chunks) - 1 else ""
        
        if line_prev != "":
            print(Style.DIM + f"{line_prev}")
        print(Style.BRIGHT + f"{chunks[i]}")
        if line_next != "":
            print(Style.DIM + f"{line_next}")
        
        data, samplerate = sf.read(buffer, dtype='int16')
        sd.play(data, samplerate)
        sd.wait()

producer_thread = threading.Thread(target=synthesize_chunks, daemon=True)
consumer_thread = threading.Thread(target=play_chunks, daemon=True)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()
