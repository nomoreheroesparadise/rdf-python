FROM python:3.6-alpine

RUN apk update && apk upgrade && pip install -U pip
RUN apk add --update alpine-sdk make gcc python3-dev python-dev libxslt-dev libxml2-dev libc-dev openssl-dev libffi-dev zlib-dev py-pip \
    && rm -rf /var/cache/apk/*

WORKDIR /usr/src/appd

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

CMD [ "python", "./run.py" ]