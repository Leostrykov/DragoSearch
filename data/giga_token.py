import requests
import os
from dotenv import load_dotenv


def get_giga_token():
    # Загружаем ключи из .env, т.к glitch скрывает эти ключи от пользователей
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload='scope=GIGACHAT_API_PERS'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
      'RqUID': os.getenv('GIGA_CLIENT_ID'),
      'Authorization': f'Basic {os.getenv("GIGA_CLIENT_SECRET")}',
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False).json()

    return response['access_token']