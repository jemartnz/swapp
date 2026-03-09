FROM node:24-alpine AS builder

WORKDIR /app

COPY front/package.json front/package-lock.json* ./
RUN npm install

COPY front/ ./
RUN npm run build

FROM nginx:alpine

COPY docker/prod/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
