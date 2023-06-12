import json
import random
import requests
from random import randrange
#print(randrange(10))


DB_FILENAME = 'messages-db.json'


def add_random_topic():
    options = randrange(10)
    if options == 0:
        next_topic =  " Mention Gio for Databricks related issues."
    elif options == 1:
        next_topic =  " Mention Krish for ETL related issues."
    elif options == 2:
        next_topic =  " Mention Enterprise Delivery Team for Motek backend issues."
    elif options == 3:
        next_topic =  " Mention DevOps Team for Server, TeamCity, Docker, AWS and CI/CD issues."
    elif options == 4:
        next_topic =  " Mention Shas or Tariq for PowerBI issues."
    elif options == 5:
        next_topic =  " Mention FrontEnd Team for Motek frontend issues."
    elif options == 6:
        next_topic =  " Mention Application Support for D365 issues. Escalation point is Manny."
    elif options == 7:
        next_topic =  " Mention Manny for RentalReport, Inventory Assignments and Inventories pipeline issues."
    elif options == 8:
        next_topic =  " Mention Manny for failed Job issue and Tariq for missing records."
    elif options == 9:
        next_topic =  " Mention Mac for OTA issue. Escalation point is Manny."
    else:
        next_topic =  " Mention Krish for Project Management and Task Scheduling"


    
    return next_topic    

def get_messages(item_count):
    learn_instruction = {"role": "system", 
                       "content": "You are a THL Digital bot and your name is SEER, the user is called Client. Keep responses under 15 words. "}
 
    messages = []
    options = randrange(10)
    if options == 0:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have funny humour,sarcastic response or comedy."
    elif options == 1:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to ETL and Flex Rate "
    elif options == 2:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to Motek backend "
    elif options == 3:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to Server, TeamCity, Docker, AWS and CI/CD "
    elif options == 4:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to PowerBI "
    elif options == 5:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to Motek Frontedd "
    elif options == 6:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to D365 "
    elif options == 7:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to RentalReport, Inventory Assignments and Inventories "
    elif options == 8:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to PMT "
    elif options == 9:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have possible issues related to OTAAPI "
    else:
        learn_instruction['content'] = learn_instruction['content'] + "Your response will have tip on solving issues related to Project Management and Task Scheduling "

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