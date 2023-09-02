FROM python:3

RUN apt-get -y update && apt-get -y install \
	screen \
	vim

COPY . /project
WORKDIR /project

RUN pip3 install -r requirements.txt \
    && pip3 install .

CMD /bin/bash
