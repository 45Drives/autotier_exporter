FROM python:3.9-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY autotier_exporter.py /usr/src/app

EXPOSE 9450

ENTRYPOINT [ "python3", "-u", "./autotier_exporter.py" ]
CMD [ "--port", "9450" ]
