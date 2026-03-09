FROM node:24-alpine

WORKDIR /app

COPY front/package.json front/package-lock.json* ./
RUN npm install

COPY front/ ./

EXPOSE 3000
