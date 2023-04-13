FROM python:3.7-slim
RUN apt-get update
RUN apt install gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 -y
RUN apt install libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 -y
RUN apt install libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 -y
RUN apt install libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 -y
RUN apt install ca-certificates fonts-liberation libnss3 lsb-release xdg-utils wget libcairo-gobject2 -y
RUN apt install libxinerama1 libgtk2.0-0 libpangoft2-1.0-0 libthai0 libpixman-1-0 libxcb-render0 -y
RUN apt install libharfbuzz0b libdatrie1 libgraphite2-3 libgbm1 -y
#RUN apt install -y whois
RUN pip install --upgrade pip
RUN pip uninstall httpx
RUN pip install httpx==0.13.3
#RUN pip install aio-pika pika lxml
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY ./run.py /app/run.py
COPY ./setup_requirements.py /app/setup_requirements.py
COPY ./settings.py /app/settings.py
COPY ./core /app/core
COPY ./modules /app/modules
COPY ./scrapers /app/scrapers
CMD python run.py