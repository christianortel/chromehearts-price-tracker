FROM node:20-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY apps/web/package.json /app/apps/web/package.json
RUN cd /app/apps/web && npm install

COPY . /app

WORKDIR /app/apps/web
CMD ["npm", "run", "dev"]

