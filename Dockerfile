FROM python:3.6
MAINTAINER Marek Suchanek "suchama4@fit.cvut.cz"
COPY . /repocribro
WORKDIR /repocribro
RUN python setup.py install
ENTRYPOINT ["repocribro"]
