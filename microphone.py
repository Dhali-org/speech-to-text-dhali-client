import io
import json
import wave
import pyaudio
import requests

from io import BytesIO                                                 
from dhali.module import Module                                                    
from dhali.payment_claim_generator import (                                        
    get_xrpl_wallet,                                                               
    get_xrpl_payment_claim,                                                        
)           

# import logging

# import http.client
# http.client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

print("Preparing payment infrastructure...")

asset_uuid = "d82952124-c156-4b16-963c-9bc8b2509b2c"                                        
some_wallet = get_xrpl_wallet()                                                
                                                                               
DHALI_PUBLIC_ADDRESS="rstbSTpPcyxMsiXwkBxS9tFTrg2JsDNxWk"                      
some_payment_claim = get_xrpl_payment_claim(some_wallet.seed, DHALI_PUBLIC_ADDRESS, "100000000", some_wallet.sequence, "200000000")

# Settings
filename = 'recording.wav'
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 16000  # Record at 44100 samples per second

def get_microphone_input_for(seconds):

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    # Store data in chunks for 3 seconds
    frames = []
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()

    buf = io.BytesIO()

    wf = wave.open(buf, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    buf.seek(0)

    headers = {"Payment-Claim": json.dumps(some_payment_claim)}
    files = {"input": buf}
    response = requests.put(f"https://dhali-prod-run-dauenf0n.uc.gateway.dev/{asset_uuid}/run", headers=headers, files=files)


    # response = test_module.run(output, some_payment_claim)


    # return wf
    # response = requests.post(api_url, files={'file': f})
    return response.json()["result"]

if __name__ == "__main__":
    print(get_microphone_input_for(3))