# To run unit tests with this docker file, one can use the following command:
#   docker run <image> py.test -lv /root/f5-openstack-heat-plugins/f5_heat/resources/test --cov=/root/f5-openstack-heat-plugins/f5_heat/resources
FROM ubuntu:14.04

# Install prerequisites
RUN apt-get update -y 
RUN apt-get -y dist-upgrade
RUN apt-get -y install heat-engine
RUN apt-get -y install python-pip
RUN apt-get -y install build-essential
RUN apt-get -y install libssl-dev
RUN apt-get -y install libffi-dev
RUN apt-get -y install python-dev

# Clone openstack heat engine and install requirements for heat engine
RUN git clone -b stable/kilo https://github.com/openstack/heat.git /root/heat
RUN pip install -r /root/heat/requirements.txt

# Clone f5-common-python repo
RUN git clone -b feature.iapp_parser_json_like https://github.com/pjbreaux/f5-common-python-1.git /root/f5-common-python
RUN pip install -r /root/f5-common-python/requirements.txt

# Add the private key to be used to clone private repos on github.com
# add your ssh-key for github to the build: ADD ~/.ssh/github_priv_key /root/.ssh/
ADD github_rsa_4096 /root/.ssh/
# Modify the git clones below to pull the specific branches you wish to test
RUN ssh-agent bash -c 'ssh-add /root/.ssh/github_rsa_4096; ssh-keyscan -H github.com >> ~/.ssh/known_hosts; git clone -b feature.full_template_upload git@github.com:pjbreaux/f5-openstack-heat-plugins.git /root/f5-openstack-heat-plugins;' 

# Setup test enviroment
WORKDIR /root
ENV PYTHONPATH /root/heat:/root/f5-common-python:/root/f5-openstack-heat-plugins
ENV PYTHONDONTWRITEBYTECODE=True
