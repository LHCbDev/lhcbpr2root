FROM centos:latest
LABEL description=ROOT

#RUN mkdir /home/cern && cd /home/cern


RUN yum -y install epel-release
RUN yum -y install gcc-c++ && \
    yum -y install bzip2 git vim
RUN yum -y install libXpm libSM libXext libXft libpng libjpeg && \
    yum clean all
RUN yum -y install python-pip

ENV DISPLAY unix:0
ENV PROFRC /etc/profile.d/thisdocker.sh
ENV CODE /code
ENV PREFIX /usr/local
ENV FLASK_PORT 80
ENV FLASK_HOST 0.0.0.0
ENV ROOTSYS $PREFIX/root

ADD https://root.cern.ch/download/root_v6.06.00.Linux-centos7-x86_64-gcc4.8.tar.gz /var/tmp/root.tar.gz
RUN tar xzf /var/tmp/root.tar.gz -C $PREFIX && rm /var/tmp/root.tar.gz


ADD / $CODE
WORKDIR $CODE
RUN pip install -r requirements.txt

EXPOSE $FLASK_PORT
VOLUME ["$CODE/data"]
CMD ["./scripts/bootstrap"]
