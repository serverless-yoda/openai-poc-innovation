from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import whisper
import queue
import os
import threading
import torch
import re
from gtts import gTTS
import openai
import click
import numpy as np
# import requests
import configparser


def init_api():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(),'pipeline.conf')    
    config.read(config_path)
    key = config.get('AZUREAPPS.OPENAI','secret_key')
    openai.api_key = key


@click.command()
@click.option("--model", default="base", help="Model to use", type=click.Choice(["tiny","base", "small","medium","large"]))   
@click.option("--english", default=False, help="Whether to use English model",is_flag=True, type=bool)
@click.option("--energy", default=300, help="Energy level for mic to detect", type=int)
@click.option("--pause", default=0.8, help="Pause time before entry ends", type=float)
@click.option("--dynamic_energy", default=False,is_flag=True, help="Flag to enable dynamic engergy", type=bool)
@click.option("--wake_word", default="hey computer", help="Wake word to listen for",type=str)
@click.option("--verbose", default=True, help="Whether to print verbose output",is_flag=True, type=bool)

def main(model, english, energy, pause, dynamic_energy, wake_word, verbose):
    # there are no english models for large
    if model != "large" and english:
        model = model + ".en"
    
    audio_model = whisper.load_model(model)
    audio_queue = queue.Queue()
    result_queue = queue.Queue()
    
    threading.Thread(target=record_audio, args=(audio_queue, energy, pause, dynamic_energy,)).start()
    threading.Thread(target=transcribe_forever, args=(audio_queue, result_queue, audio_model, english, wake_word, verbose,)).start()
    threading.Thread(target=reply, args=(result_queue,)).start()

    while True:
        print(result_queue.get())


def record_audio(audio_queue, energy, pause, dynamic_energy):
    #load the speech recognizer and set the initial energy threshold and pause threshold
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Listening...")
        i = 0
        while True:
           
            #get and save audio to wav file
            audio = r.listen(source)
            # Whisper expects a torch tensor of floats.
            # https://github.com/openai/whisper/blob/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d/whisper/audio.py#L49
            # https://github.com/openai/whisper/blob/9f70a352f9f8630ab3aa0d06af5cb95\32bd8c21d/whisper/audio.py#L112
            
            torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
            audio_data = torch_audio
            audio_queue.put_nowait(audio_data)
            i += 1



def transcribe_forever(audio_queue, result_queue, audio_model, english, wake_word, verbose):
    while True:
        audio_data = audio_queue.get()
        if english:
            result = audio_model.transcribe(audio_data,language='english')
        else:
            result = audio_model.transcribe(audio_data)

        
        predicted_text = result["text"]
       

        if predicted_text.strip().lower().startswith(wake_word.strip().lower()):
          
            pattern = re.compile(re.escape(wake_word), re.IGNORECASE)
            predicted_text = pattern.sub("", predicted_text).strip()
            punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
            predicted_text.translate({ord(i): None for i in punc})
            if verbose:
                print("You said the wake word.. Processing {}...".format(predicted_text))
                result_queue.put_nowait(predicted_text)
            else:
                if verbose:
                    print("You did not say the wake word.. Ignoring")


def reply(result_queue):
    while True:
        result = result_queue.get()
        print("here" + result)
        data = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=result,
                    temperature=0,
                    max_tokens=150,
                )
        answer = data["choices"][0]["text"]
        mp3_obj = gTTS(text=answer, lang="en", slow=False)
        mp3_obj.save("reply.mp3")
        reply_audio = AudioSegment.from_mp3("reply.mp3")
        play(reply_audio)
        os.remove("reply.mp3")                    
                

init_api()
main()                