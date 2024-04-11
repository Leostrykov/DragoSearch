import flask
from flask import request, jsonify
import requests
import json
from data.giga_token import get_giga_token

blueprint = flask.Blueprint(
    'giga_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/gigachat', methods=['POST'])
def giga_chat():
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": request.json["message"] + '\nОтвет пиши на русском языке',
            }
        ],
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {get_giga_token()}'
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return response.json()
