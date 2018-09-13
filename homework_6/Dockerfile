# our base image
FROM nginx

MAINTAINER Aleksey Egorov

RUN yum -y -q install epel-release
RUN yum -y -q install python36
#RUN yum -y -q install httpd-tools
#RUN yum -y -q install nginx

# specify the port number the container should expose
EXPOSE 8080

WORKDIR /home/work

COPY common /home/work/
COPY hasker /home/work/
COPY index /home/work/
COPY media /home/work/
COPY question /home/work/
COPY static /home/work/
COPY templates /home/work/
COPY manage.py /home/work/
COPY uwsgi_params /home/work/


# run the application
#ENTRYPOINT ["sh", "start_httpd.sh"]
