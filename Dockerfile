FROM osgeo/gdal

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt update && apt install -y python3-pip libspatialindex-dev

RUN pip3 install -r requirements.txt

COPY ./src/main.py ./src/main.py

# CMD [ "python", "./src/main.py" ]