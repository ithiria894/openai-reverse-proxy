import json
from mitmproxy import http
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import re
from datetime import datetime

model_name = "ibm-granite/granite-guardian-hap-38m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, device_map="cpu")

TOXICITY_THRESHOLD = 0.5

def check_content(text):
    violence = bool(re.search(r"(kill|hurt|attack|violence|blood|death)", text, re.I))
    illegal = bool(re.search(r"(how to.*(hack|steal|drug|crime|illegal))", text, re.I))
    sexual = bool(re.search(r"(sex|porn|nude|fuck)", text, re.I))
    return violence, illegal, sexual

def evaluate_text(prompt):
    inputs = tokenizer(prompt, padding=True, truncation=True, return_tensors="pt").to("cpu")
    with torch.no_grad():
        logits = model(**inputs).logits
        toxicity_score = torch.softmax(logits, dim=1)[:, 1].item()

    violence, illegal, sexual = check_content(prompt)

    if toxicity_score > TOXICITY_THRESHOLD or any([violence, illegal, sexual]):
        if violence:
            reason = "description of violent acts"
        elif illegal:
            reason = "inquiries on how to perform an illegal activity"
        elif sexual:
            reason = "sexual content"
        else:
            reason = "the prompt is considered toxic"
        return reason, toxicity_score
    return None, toxicity_score

def request(flow: http.HTTPFlow) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Request Method: {flow.request.method}")
    print(f"[{timestamp}] Request URL: {flow.request.url}")
    print(f"[{timestamp}] Request Host: {flow.request.host}")
    print(f"[{timestamp}] Request Headers: {flow.request.headers}")
    print(f"[{timestamp}] Request Body: {flow.request.content}")

    # 檢查是否為 JSON POST 請求
    if flow.request.method == "POST" and "application/json" in flow.request.headers.get("Content-Type", ""):
        try:
            data = json.loads(flow.request.content.decode('utf-8'))
            if "messages" in data:
                prompt = data["messages"][-1]["content"]
                print(f"[{timestamp}] Prompt: {prompt}")
                
                reason, toxicity_score = evaluate_text(prompt)
                if toxicity_score > 0.5 or reason:
                    block_reason = reason if reason else "the prompt is considered toxic"
                    flow.response = http.Response.make(
                        403,
                        f"The prompt was blocked because it contained {block_reason}".encode(),
                        {"Content-Type": "text/plain"}
                    )
                    print(f"[{timestamp}] Request Blocked\n  Prompt: {prompt}\n  Reason: {block_reason}\n  Toxicity Score: {toxicity_score:.2f}")
                    return
                print(f"[{timestamp}] Request Passed\n  Prompt: {prompt}")
        except Exception as e:
            print(f"[{timestamp}] Error parsing JSON: {e}")
            return

def response(flow: http.HTTPFlow) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response_text = flow.response.get_text() or ""
    print(f"[{timestamp}] Response: {response_text}")

    reason, toxicity_score = evaluate_text(response_text)
    if toxicity_score > 0.5 or reason:
        block_reason = reason if reason else "the response is considered toxic"
        flow.response = http.Response.make(
            403,
            f"The response was blocked because it contained {block_reason}".encode(),
            {"Content-Type": "text/plain"}
        )
        print(f"[{timestamp}] Response Blocked\n  Original Response: {response_text}\n  Reason: {block_reason}\n  Toxicity Score: {toxicity_score:.2f}")
    else:
        print(f"[{timestamp}] Response Passed\n  Response: {response_text}\n  Toxicity Score: {toxicity_score:.2f}")
    print(f"[{timestamp}] Response Details\n  Status Code: {flow.response.status_code}\n  Headers: {flow.response.headers}")