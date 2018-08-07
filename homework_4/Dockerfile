# our base image
FROM centos

MAINTAINER Aleksey Egorov

#ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN yum -y -q install epel-release
RUN yum -y -q install python36
RUN yum -y install python36-setuptools
RUN easy_install-3.6 pip
RUN pip3 install redis
RUN pip3 install requests

# specify the port number the container should expose
EXPOSE 8080

WORKDIR /home/work

COPY api.py /home/work/
COPY constants.py /home/work/
COPY scoring.py /home/work/
COPY store.py /home/work/
COPY store_cfg.py /home/work/
COPY test.py /home/work/
COPY tests/* /home/work/tests/

# run the application
ENTRYPOINT ["python3.6", "/home/work/api.py", "--port=8080"]
