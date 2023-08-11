import io
import json
import wave
import pyaudio
import requests
import sys
import logging

import numpy as np

from dhali.module import Module

LOGGING_FILE = "stderr.log"
logging.basicConfig(filename=LOGGING_FILE)

print("Preparing payment infrastructure. This may take a minute...")

asset_uuid = "d82952124-c156-4b16-963c-9bc8b2509b2c"
test_module = Module(asset_uuid)


class MicrophoneListener:
    def __init__(self, payment_claim):
        # Settings
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = self.determine_sample_rate()
        self.payment_claim = payment_claim

        # Determine the sample rate:
        for fs_test_value in (16000, 44100, 48000):
            logging.info(f"'global initialisation': trying sample rate of {self.fs}.")
            try:
                stream = p.open(format=self.sample_format,
                                channels=self.channels,
                                rate=fs_test_value,
                                frames_per_buffer=self.chunk,
                                input=True)
            except Exception as e:
                continue
            logging.info(f"'global initialisation': fs value of {self.fs} selected.")
            self.fs = fs_test_value
            break

        if self.fs is None:
            logging.error("'global initialisation': Unable to find valid sampling rate. Exiting")
            sys.exit(-1)

    def is_loud(self, input_data, threshold):
        # Convert byte data to numpy array
        numpydata = np.fromstring(input_data, dtype=np.int16).astype( dtype=np.int32)

        # Calculate RMS (root mean square) which is a common way to measure "loudness"
        rms = np.sqrt(np.mean(numpydata**2))

        # Check if the RMS is above the threshold
        if rms > threshold:
            return True
        else:
            return False

    def determine_sample_rate(self):
        p = pyaudio.PyAudio()  # Initialize a temporary PyAudio instance
        fs = None  # Will be determined in the loop below
        for fs_test_value in (16000, 44100, 48000):
            logging.info(f"'determine_sample_rate': trying sample rate of {fs_test_value}.")
            try:
                stream = p.open(format=self.sample_format,
                                channels=self.channels,
                                rate=fs_test_value,
                                frames_per_buffer=self.chunk,
                                input=True)
                stream.close()  # Close the stream as soon as we're done with it
            except Exception as e:
                continue
            logging.info(f"'determine_sample_rate': fs value of {fs_test_value} selected.")
            fs = fs_test_value
            break
        p.terminate()  # Terminate the temporary PyAudio instance
        if fs is None:
            logging.error("'determine_sample_rate': Unable to find valid sampling rate. Exiting")
            sys.exit(-1)
        return fs

    def get_microphone_input_for(self, seconds, detect_is_loud):
        detect_is_loud["is_recording"] = True 
        p = pyaudio.PyAudio()  # Initialize a temporary PyAudio instance
        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                        input=True)

        # Store data in chunks for 3 seconds
        frames = []
        loud = False
        count = 0
        previous_frame_is_loud = False
        current_frame_is_loud = False
        while True:
            count += 1
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)
            previous_frame_is_loud = current_frame_is_loud
            current_frame_is_loud = self.is_loud(data, 500)

            if self.is_loud(data, 500):
                loud = True
                detect_is_loud["is_loud"] = True
            if count > int(self.fs / self.chunk * seconds) and not current_frame_is_loud and not previous_frame_is_loud:
                break
            if count > int(self.fs / self.chunk * (seconds+4)):
                break
        detect_is_loud["is_recording"] = False        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Terminate the PortAudio interface
        p.terminate()

        # Condition on `loud`, not `detect_is_loud` to ensure thread safety
        if not loud:
            detect_is_loud["is_loud"] = False
            return "."

        buf = io.BytesIO()

        wf = wave.open(buf, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        buf.seek(0)

        response = test_module.run(buf, self.payment_claim)

        return response.json()["result"]

if __name__ == "__main__":
    print(get_microphone_input_for(3))
