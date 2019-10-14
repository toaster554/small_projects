import io
import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import soundfile as sf

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--duration', default = 5)

args = parser.parse_args()

def get_speech(client, duration = 5, sample_rate = 16000, channels = 1):
    recording = sd.rec(duration * sample_rate, samplerate = sample_rate,
                       channels = channels, dtype = 'float64')
    print("Recording Speech...")
    sd.wait()
    print("Speech recording complete")

    # write file as .wav format
    sf.write('temp.wav', recording, sample_rate)

    # Loads the audio into memory
    with io.open('temp.wav', 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content = content)

    config = types.RecognitionConfig(
        encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = sample_rate,
        language_code = 'en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    
    text = ''
    # print transcript
    for result in response.results:
        #print('Transcript: {}'.format(result.alternatives[0].transcript)
        text += result.alternatives[0].transcript

    # echo what is said
    print(f'You said: {text}')

    return text

def main():
    # MAKE SURE THAT THE API SERVICE IS ENABLED!!
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service.json"

    # length of recording in seconds
    duration = args.duration
    
    # Instantiates a client
    client = speech.SpeechClient()
    
    print('Say "done" to exit')

    text = get_speech(client. duration)

    while text != 'done':
        text = get_speech(client)

if __name__ == "__main__":
    main()