# our base image
FROM centos

MAINTAINER Aleksey Egorov

#ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN yum -y -q install epel-release
RUN yum -y -q install python36
RUN yum -y -q install httpd-tools

# specify the port number the container should expose
EXPOSE 8080

WORKDIR /home/work

COPY httpd.py /home/work/
COPY httptest.py /home/work/
COPY start_httpd.sh /home/work/
COPY test.sh /home/work/
COPY htdocs/ /home/work/htdocs/

# run the application
ENTRYPOINT ["sh", "start_httpd.sh"]
