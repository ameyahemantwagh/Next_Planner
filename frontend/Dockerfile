FROM node:18-bullseye-slim

WORKDIR /usr/src/app

# install dependencies at build time
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps || npm install

# copy source
COPY . /usr/src/app

EXPOSE ${FRONTEND_PORT}

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "${FRONTEND_PORT}"]