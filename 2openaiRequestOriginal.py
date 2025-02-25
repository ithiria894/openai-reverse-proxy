#2openaiRequestOriginal.py
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

user_prompt = input("Please enter your prompt: ")
data = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are a useful helper."},
        {"role": "user", "content": user_prompt}
    ]
}



# Sending POST request to NGINX
response = requests.post(
    # url="https://localhost/v1/chat/completions",
    url="https://localhost:443/v1/chat/completions", 
    # url="https://localhost:8080/v1/chat/completions", 
    headers=headers,
    json=data,
    # verify=False  # for test
    verify="/etc/nginx/ssl/nginx.crt"
)

#For Docker
# response = requests.post(
#     # url="https://nginx:443/v1/chat/completions",  
#     url="https://localhost:8443/v1/chat/completions",
#     headers=headers,
#     json=data,
#     # verify="/app/nginx.crt"  
#     verify=False
# )

if response.status_code == 200:

    completion = response.json()
    print(completion["choices"][0]["message"]["content"])
else:
    # print(f"Response Fail: {response.status_code}")
    print(response.text)