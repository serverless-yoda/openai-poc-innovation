import json
import random
import requests


DB_FILENAME = 'messages-db.json'

def get_messages(item_count):
    learn_instruction = {"role": "system", 
                       "content": "You are a Finance Manager and your name is Rachel, the user is called Manny. Keep responses under 15 words. "}
 
    messages = []
    options = random.uniform(0,1)
    if options < 0.2:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have funny humour and sarcastic response."
    elif options < 0.5:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to ETL,PowerBI,OTA,Dynamic Finance 365 and Databricks. "
    else:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have tip on solving issues related to ETL, PowerBI, OTA, Dynamic Finance 365 and Databricks. "

    messages.append(learn_instruction)

    try:
        with open(DB_FILENAME) as user_file:
            data = json.load(user_file)
      
        # Append last 5 rows of data
        if data:
            if len(data) < item_count:
                for item in data:
                    messages.append(item)
        else:
            for item in data[-5:]:
                messages.append(item)
    except:
        pass

    return messages


def save_messages(request_message, response_message):
    messages = get_messages(5)[1:]

    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    messages.append(user_message)
    messages.append(assistant_message)

    # update messages
    with open(DB_FILENAME, "w") as f:
        json.dump(messages, f)


def reset_messages():
    open(DB_FILENAME, "w")


def text_to_speech(message, key):  
    body = {
            "text": message,
            "voice_settings": {
                "stability": 0,
                "similarity_boost": 0
                }
            }

    
    voice_shaun = "mTSvIrm2hmcnOvb21nW2"
    voice_rachel = "21m00Tcm4TlvDq8ikWAM"
    voice_antoni = "ErXwobaYiN019PkySvjV"
  
  
    options = random.uniform(0,1)
    if options < 0.2:
         voice = voice_antoni
    elif options < 0.5:
         voice = voice_shaun     
    else:
        voice = voice_rachel
  
    print(f'text_to_speech:{voice}')

    # Construct request headers and url
    headers = { "xi-api-key": key, "Content-Type": "application/json", "accept": "audio/mpeg" }
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?optimize_streaming_latency=0"

    try:
        response = requests.post(endpoint, json=body, headers=headers)
    except Exception as e:
        print(f'text to speech error:{response}')
        return


    if response.status_code == 200:
        print(f'text to speech:{response.content}')     
        return response.content
    else:
        print(f'text to speech:{response}')             
        return