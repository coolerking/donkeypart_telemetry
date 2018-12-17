FROM python:3.6.7-alpine

# for development use
ENV NODE_ENV=development

# Proxy Configuration
#ENV HTTP_PROXY=http://proxy.server.fqdn:8080/
#ENV HTTPS_PROXY=http://proxy.server.fqdn:8080/

RUN pip install paho-mqtt && pip install express
WORKDIR /app

RUN cd /app

CMD python test_pub.py
# communicate within compose only