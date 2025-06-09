FROM cypress/included:13.6.6

WORKDIR /app

COPY . .

RUN npm install

CMD [ "npm", "run-p", "start", "test" ]