FROM python:3.11-bookworm as builder

WORKDIR /app

COPY requirements_docs.txt .
RUN pip3 install -r requirements_docs.txt

COPY . .
RUN mkdocs build

FROM node:20-alpine

RUN npm install -g serve

WORKDIR /app
COPY --from=builder /app/site ./
RUN pwd
RUN ls -l

EXPOSE 9000
CMD ["serve","-l","tcp://0.0.0.0:9000"]
