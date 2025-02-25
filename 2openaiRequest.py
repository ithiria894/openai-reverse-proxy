#2openaiRequest.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")


if not api_key:
    raise ValueError("OPENAI_API_KEY not found.")


headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Host": "api.openai.com"  # Target Host
}

# user_prompt = input("Please enter your pepe: ")
user_prompt = "Where is the capital of France?"
data = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are a useful helper."},
        {"role": "user", "content": user_prompt}
    ]
}



# Sending POST request to NGINX
# response = requests.post(
#     url="https://localhost/v1/chat/completions",  
#     headers=headers,
#     json=data,
#     verify=False  # for test
#     # verify="/etc/nginx/ssl/nginx.crt"
# )
proxies = {
    'http': 'http://mitmproxy:8080',
    'https': 'http://mitmproxy:8080'
}
# For Docker

try:
    response = requests.post(
        # url="https://nginx:8443/v1/chat/completions",  
        # url="https://localhost:8443/v1/chat/completions",
        # url="https://mitmproxy:8081/v1/chat/completions",
        # url="http://localhost:8080/v1/chat/completions",
        url="https://api.openai.com/v1/chat/completions",
        proxies=proxies,
        headers=headers,
        json=data,
        # verify="/app/nginx.crt"  
        verify=False,
        timeout=10
    )
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:

        completion = response.json()
        print(completion["choices"][0]["message"]["content"])
    else:
        # print(f"Response Fail: {response.status_code}")
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

