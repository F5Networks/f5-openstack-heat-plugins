FROM ubuntu:14.04

# Install prerequisites
RUN apt-get -y dist-upgrade
RUN apt-get -y update
RUN apt-get -y install python
RUN apt-get -y install heat-engine
RUN apt-get -y install python-pip
RUN apt-get -y install build-essential
RUN apt-get -y install libssl-dev
RUN apt-get -y install libffi-dev
RUN apt-get -y install python-dev
RUN apt-get -y install git
RUN apt-get -y install vim
RUN pip install pytest
RUN pip install pytest-cov
RUN pip install hacking
RUN pip install cryptography
RUN pip install funcsigs

# Add the private key to be used to clone private repos on github.com
# add your ssh-key for github to the build: ADD ~/.ssh/github_priv_key /root/.ssh/
ADD github_rsa_4096 /root/.ssh/
RUN ssh-agent bash -c 'ssh-add /root/.ssh/github_rsa_4096; ssh-keyscan -H github.com >> ~/.ssh/known_hosts; git clone -b feature.add_unittesting_framework git@github.com:pjbreaux/f5-openstack-heat-plugins.git /root/f5-openstack-heat-plugins; pip install git+ssh://git@github.com/F5Networks/f5-icontrol-rest-python@v0.1.0; git clone -b develop git@github.com:pjbreaux/f5-common-python.git /root/f5-common-python'

# Install requirements from f5-common-python
RUN pip install -r /root/f5-common-python/requirements.txt

# Clone openstack heat engine and install requirements for heat engine
RUN git clone https://github.com/openstack/heat.git /root/heat
RUN cd /root/heat && git checkout stable/kilo
RUN pip install -r /root/heat/requirements.txt

# Setup test enviroment
WORKDIR /root
ENV PYTHONPATH /root/heat:/root/f5-common-python:/root/f5-openstack-heat-plugins
