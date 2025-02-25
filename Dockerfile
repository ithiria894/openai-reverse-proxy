FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN echo "tzdata tzdata/Areas UTC" > /etc/timezone && \
    echo "tzdata tzdata/Zones/UTC" > /etc/timezone && \
    apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nginx \
    mitmproxy \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install torch==2.3.0 transformers==4.49.0 numpy==1.26.4 mitmproxy requests python-dotenv accelerate>=0.26.0

WORKDIR /app

COPY mitOpenWGuardianhap.py /app/mitOpenWGuardianhap.py
COPY 2openaiRequest.py /app/2openaiRequest.py
COPY nginx_default /etc/nginx/sites-available/default
COPY /etc/nginx/ssl/nginx.crt /etc/nginx/ssl/nginx.crt
COPY /etc/nginx/ssl/nginx.key /etc/nginx/ssl/nginx.key
# COPY mitmproxy.crt /app/mitmproxy.crt
# COPY mitmproxy.key /app/mitmproxy.key
COPY .env /app/.env

RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

EXPOSE 443 8080 8081

CMD ["bash"]