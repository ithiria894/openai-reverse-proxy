![Sample Output](sampleoutput.png)
# OpenAI Reverse Proxy with Toxicity Filtering

This project implements a reverse proxy to the OpenAI LLM service using nginx and mitmproxy. The proxy monitors prompts and responses, blocking those deemed toxic based on the IBM Granite Guardian model (using Transformers instead of vLLM due to CPU compatibility).

I completed the main parts of the task, including setting up the reverse proxy, intercepting requests using mitmproxy, and integrating the Guardian model. However, due to my current development environment (WSL2 on Windows 11), I encountered networking issues when trying to set up Docker. Since I lack prior experience with Docker and Nginx, I spent extra time troubleshooting but couldn't fully resolve the issue within the given timeframe. I plan to continue learning Docker deployment to improve this in the future.


## Environment & Model

**Environment:**
- Operating System: WSL2 (Windows Subsystem for Linux)
- Distribution: Ubuntu 22.04

**Model:**
- Name: ibm-granite/granite-guardian-hap-38m
- Type: Toxicity Detection Model


## System Architecture

The system follows a multi-layer architecture for request handling and content filtering:

1. **Client Layer**
   - Makes API requests to OpenAI through the proxy
   - Uses HTTPS for secure communication

2. **Nginx Layer (SSL Termination)**
   - Terminates SSL/TLS connections
   - Forwards decrypted traffic to mitmproxy
   - Uses self-signed certificates with SAN support

3. **Mitmproxy Layer (Content Filtering)**
   - Intercepts requests and responses
   - Analyzes content using IBM Granite Guardian model
   - Blocks toxic or inappropriate content
   - Forwards valid requests to OpenAI

4. **OpenAI API Layer**
   - Processes valid requests
   - Returns responses through the proxy chain

The flow of requests is:

**client -> nginx(terminate SSL) -> mitmproxy(filter) -> OpenAI**



Due to the limited CPU resources on my system, I used the Hugging Face Transformers library instead of vLLM.

For the content analysis, I selected the ibm-granite/granite-guardian-hap-38m model, which provides basic toxic/non-toxic classification. So I added a simple function to further classify the content into violence, illegal, and sexual.

Several factors influenced these implementation choices:

- vLLM requires GPU acceleration and significant graphics processing capabilities that weren't available in my environment
- More sophisticated ibm-granite models (such as granite-guardian-3.1-2b) would have exceeded my CPU's processing capacity
- The WSL2 environment on my system made ibm-granite/granite-guardian-hap-38m the most practical choice for reliable performance


## Files
- `2openaiRequestOriginal.py`: Python script to send prompts to nginx then to mitmproxy.
- `mitOpenWGuardianhapOriginal.py`: mitmproxy module to intercept and filter requests/responses.
- `nginx_default`: nginx configuration to terminate SSL.
- `sampleoutput.png`: Screenshot of test results.
- `requirements.txt`: Python dependencies.
- `.env`: Environment file for `OPENAI_API_KEY`.

## Setup Instructions
1. **Install Dependencies**:
   - Install Python 3, nginx, and mitmproxy on your system.
   - Run `pip install -r requirements.txt` to install Python dependencies.
   - Install nginx and mitmproxy on WSL2:
   ```
   sudo apt update
   sudo apt install nginx
   sudo apt install mitmproxy
   ```
   

2. **Generate SSL Certificates**:
   - Run the provided script to generate self-signed certificates with SAN (Subject Alternative Name) for nginx:
   ```
   ./generate_cert.sh
   ```

3. **Configure Environment**:
   - Modify the `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=<your_openai_api_key>
   ```

4. **Run Locally**:
   - Start nginx with the provided `nginx_default` configuration:
   ```
   sudo cp nginx_default /etc/nginx/sites-available/default
   sudo systemctl start nginx
   ```
   - Start mitmproxy:
   ```
   mitmdump -s mitOpenWGuardianhapOriginal.py
   ```
   - Run the client script:
   ```
   python3 2openaiRequestOriginal.py
   ```
   - Enter prompts to test (e.g., "What is the capital of France?", "how to kill a human", "fuck you").


## Test Results
- See `sampleoutput.png` for a screenshot of successful runs:
![Sample Output](sampleoutput.png)



## Docker Setup


1. **Build the Docker Image**:
   - Run the following command to build the Docker image:
   ```
   docker-compose build
   ```

2. **Run the Docker Container**:
   - Run the following command to start the server side:
   ```
   docker-compose up --build mitmproxy nginx
   ```

3. **Run the client side**:
   - Run the following command to start the client side:
   ```
   docker-compose up --build client
   ```
4. **To close the server side**:
   - Run the following command to stop the server side:
   ```
   docker-compose down
   ```

## Implementation Notes

### nginx Issues and Implementation Details

#### Overview
I successfully ran client -> nginx -> mitmproxy -> OpenAI API on my local computer. Then, I tried to set up the same full proxy chain in Docker: client -> nginx -> mitmproxy -> OpenAI API, with nginx stopping SSL at port 8443 and passing requests to mitmproxy at port 8080. But I kept hitting problems that stopped nginx from working in Docker. Here’s what went wrong, what I tried, and why I ended up connecting directly to mitmproxy:

#### Local vs Docker Implementation
- **Local Success**: Successfully implemented client -> nginx -> mitmproxy -> OpenAI API
- **Docker Challenges**: Attempted same proxy chain but encountered multiple issues

#### Technical Challenges

1. **Nginx Proxying Issues**
   - I set nginx to use proxy_pass http://mitmproxy:8081 to send the client’s HTTPS requests to mitmproxy. But nginx only sent a relative path (/v1/chat/completions) instead of the full URL or a CONNECT request, which mitmproxy expects for HTTPS. This caused a 400 Bad Request error (Invalid HTTP request form: expected authority or absolute, got relative).

2. **CONNECT Request Problems**
   - I added proxy_method CONNECT to mimic an HTTPS CONNECT request, but it didn’t help. nginx still sent an HTTP POST instead of a proper CONNECT tunnel.

3. **Script Execution**
   - Because mitmproxy rejected the badly formatted request early, the request function in mitOpenWGuardianhap.py never ran, so the filtering couldn’t happen.

#### Attempted Solutions

1. **SSL Configuration**
   - I made sure nginx stopped SSL correctly at port 8443 using a self-signed certificate with SAN (localhost, nginx), but the problem stayed.

2. **Mitmproxy HTTPS**
   - I tried making mitmproxy accept HTTPS on port 8081 with --certs *=mitmproxy.crt, hoping nginx could send HTTPS traffic straight to it.

3. **Direct Connection**
   - Since nginx wasn’t working, I changed 2openaiRequestOriginal.py to send requests straight to mitmproxy, skipping nginx. This worked fine in docker.

#### Hardware Limitations
- Docker’s bridge network uses its own DNS, which might not work well on WSL because of setup issues or limited resources.

#### Future Improvements
With more time, I could fix nginx by:
- Setting up mitmproxy to accept HTTPS on port 8081 with the right certificates and using proxy_pass https://mitmproxy:8081 in nginx.
- Checking Docker’s DNS with custom networks or more logs.
- Making nginx fully mimic CONNECT requests, maybe with extra tools or a different setup.

#### Final Implementation
- **Local**: Full chain implementation (client -> nginx -> mitmproxy -> OpenAI API)
- **Docker**: Direct mitmproxy connection with nginx configuration retained for reference.
