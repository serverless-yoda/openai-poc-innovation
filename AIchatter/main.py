from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import os
import re
from gtts import gTTS
import openai
import click
import configparser

from conversations import get_messages, save_messages, reset_messages,text_to_speech,add_random_topic

config = configparser.ConfigParser()
config_path = os.path.join(os.getcwd(),'pipeline.conf')    
config.read(config_path)
OPENAI_KEY = config.get('AZUREAPPS.OPENAI','secret_key')
ELEVENLAB_KEY = config.get('11ELEVENLABS','secret_key')

def init_api():
    reset_messages()    
    openai.api_key = OPENAI_KEY


@click.command()
@click.option("--energy", default=300, help="Energy level for mic to detect", type=int)
@click.option("--pause", default=0.8, help="Pause time before entry ends", type=float)
@click.option("--dynamic_energy", default=False,is_flag=True, help="Flag to enable dynamic engergy", type=bool)
def main(energy, pause, dynamic_energy):    
    r = sr.Recognizer()
    record_audio( energy, pause, dynamic_energy,r)


def record_audio( energy, pause, dynamic_energy,r):
    # load speech recognizer
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        while True:           
            print('YOU...')
            audio = r.listen(source)

            transcribe = r.recognize_whisper_api(audio, api_key=OPENAI_KEY)
            
            messages = get_messages(5)
            user_message = {"role": "user", "content": transcribe + add_random_topic()}
            messages.append(user_message)
            
           
            response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages
            )
            message_text = response["choices"][0]["message"]["content"]
            print(f"AI Reply: {message_text}")
            

            mp3_obj = gTTS(text=message_text, lang="en", slow=False)
            mp3_obj.save("reply.mp3")
            reply_audio = AudioSegment.from_mp3("reply.mp3")
            play(reply_audio)
            os.remove("reply.mp3")                    
            save_messages(transcribe, message_text)                
            


init_api()
main()                