import requests


def send_message(api_key, to, message, parse="HTML"):
    return requests.post(f"https://api.telegram.org/bot{api_key}/sendMessage", 
                  json={"chat_id": to, 
                        "text": message, 
                        "parse_mode": parse})