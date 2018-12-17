FROM node:8.14.0-alpine

# for development use
ENV NODE_ENV=development

# Proxy Configuration
#RUN npm -g config set proxy http://proxy.server.fqdn:8080 && \
#    npm -g config set https-proxy http://proxy.server.fqdn:8080 && \
#    npm -g config set registry http://registry.npmjs.org/

WORKDIR /app

RUN cd /app && npm install

CMD node app.js
EXPOSE 3000
