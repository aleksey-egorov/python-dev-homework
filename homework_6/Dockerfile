# our base image
FROM centos

MAINTAINER Aleksey Egorov

RUN yum -y -q install epel-release
RUN yum -y -q install python36
RUN yum -y -q install httpd-tools

# specify the port number the container should expose
EXPOSE 8080

WORKDIR /home/work

COPY ./* /home/work/


# run the application
ENTRYPOINT ["sh", "start_httpd.sh"]
