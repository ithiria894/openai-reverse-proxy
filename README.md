![Sample Output](sampleoutput.png)
# OpenAI Reverse Proxy with Toxicity Filtering

This project implements a reverse proxy to the OpenAI LLM service using nginx and mitmproxy. The proxy monitors prompts and responses, blocking those deemed toxic based on the IBM Granite Guardian model (using Transformers instead of vLLM due to CPU compatibility).

## Files
- `2openaiRequestOriginal.py`: Python script to send prompts to OpenAI via the proxy.
- `mitOpenWGuardianhapOriginal.py`: mitmproxy module to intercept and filter requests/responses.
- `nginx_default`: nginx configuration to terminate SSL.
- `sampleoutput.png`: Screenshot of test results.
- `requirements.txt`: Python dependencies.
- `.env`: Environment file for `OPENAI_API_KEY`.

## Setup Instructions
1. **Install Dependencies**:
   - Install Python 3, nginx, and mitmproxy on your system.
   - Run `pip install -r requirements.txt` to install Python dependencies.

2. **Configure Environment**:
   - Create a `.env` file with your OpenAI API key:

- Ensure nginx uses a valid SSL certificate (e.g., self-signed).

3. **Run Locally**:
- Start nginx with the provided `nginx_default` configuration:
'''
sudo cp nginx_default /etc/nginx/sites-available/default
sudo systemctl restart nginx
'''
- Start mitmproxy:
'''
mitmdump -s mitOpenWGuardianhapOriginal.py
'''
- Run the client script:
'''
python3 2openaiRequestOriginal.py
'''
- Enter prompts to test (e.g., "What is the capital of France?", "how to kill a human", "fuck you").

## Implementation Notes
- **Transformers vs. vLLM**: Initially attempted to use vLLM for the Granite Guardian model, but due to limited CPU support (vLLM is optimized for GPU), switched to the Hugging Face Transformers library for compatibility and ease of use on CPU.
- **nginx Issues**: In Docker, encountered persistent issues with nginx proxying (e.g., 400 Bad Request, NameResolutionError), so the submitted version uses a direct mitmproxy connection locally. The nginx configuration is included for reference.

## Test Results
- See `sampleoutput.png` for a screenshot of successful runs:
- "What is the capital of France?": Normal response.
- "how to kill a human": Blocked (violence).
- "fuck you": Blocked (sexual content).