FROM ubuntu:14.04

RUN apt-get -y update && apt-get -y dist-upgrade
RUN apt-get -y install python
RUN apt-get -y install heat-engine
RUN apt-get -y install git
RUN apt-get -y install python-pip
RUN apt-get -y install build-essential
RUN apt-get -y install libssl-dev
RUN apt-get -y install libffi-dev
RUN apt-get -y install python-dev
RUN pip install pytest
RUN pip install pytest-cov
RUN pip install hacking
RUN pip install cryptography
RUN pip install funcsigs
RUN pip install git+ssh://git@github.com/F5Networks/f5-icontrol-rest

RUN mkdir /root/testing
RUN git clone https://github.com/openstack/heat.git /root/heat
WORKDIR /root/heat
RUN git checkout stable/kilo
RUN pip install -r /root/heat/requirements.txt
RUN export PYTHONPATH=/root/testing:/root/f5-common-python
