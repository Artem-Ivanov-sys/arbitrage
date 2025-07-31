FROM python:3.13.1-slim

WORKDIR /api

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "sh", "./entrypoint.sh" ]