import io
import json
import wave
import pyaudio
import requests

import numpy as np
                                           
from dhali.module import Module                                                    
from dhali.payment_claim_generator import (                                        
    get_xrpl_wallet,                                                               
    get_xrpl_payment_claim,                                                        
)           

print("Preparing payment infrastructure...")

asset_uuid = "d82952124-c156-4b16-963c-9bc8b2509b2c"
test_module = Module(asset_uuid)                                       
some_wallet = get_xrpl_wallet()                                                
                                                                               
DHALI_PUBLIC_ADDRESS="rstbSTpPcyxMsiXwkBxS9tFTrg2JsDNxWk"                      
some_payment_claim = get_xrpl_payment_claim(some_wallet.seed, DHALI_PUBLIC_ADDRESS, "100000000", some_wallet.sequence, "200000000")

# Settings
filename = 'recording.wav'
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 16000  # Record at 44100 samples per second

def is_loud(input_data, threshold):
    # Convert byte data to numpy array
    numpydata = np.fromstring(input_data, dtype=np.int16).astype( dtype=np.int32)
    
    # Calculate RMS (root mean square) which is a common way to measure "loudness"
    rms = np.sqrt(np.mean(numpydata**2))
    
    # Check if the RMS is above the threshold
    if rms > threshold:
        return True
    else:
        return False

def get_microphone_input_for(seconds):

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    # Store data in chunks for 3 seconds
    frames = []
    loud = False
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
        if is_loud(data, 1500):
            loud = True

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()

    if not loud:
        return loud, "."

    buf = io.BytesIO()

    wf = wave.open(buf, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    buf.seek(0)

    response = test_module.run(buf, some_payment_claim)

    return loud, response.json()["result"]

if __name__ == "__main__":
    print(get_microphone_input_for(3))