import logging
import openai
import os
import configparser
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function sending a request to OpenAPI')

    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(),'pipeline.conf')    
    config.read(config_path)
    key = config.get('OPENAI','secret_key')
    
    # get secret key from config
    openai.api_key = key

    # get model parameters
    req_body = req.get_json()
    prompt = req_body.get('prompt')
    model  = req_body.get('model')
    max_tokens = req_body.get('max_tokens')
    temperature = req_body.get('temperature')
    
    # execute
    output = openai.Completion.create(        
        model=model,
        prompt = prompt,
        max_tokens = max_tokens,
        temperature = temperature
    )

    # return result
    result = output['choices'][0]['text']
    
    return func.HttpResponse(
             result,
             status_code=200
        )
