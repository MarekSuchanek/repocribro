FROM python:3.6

WORKDIR /repocribro

# Install dependencies (caching)
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install package
COPY . /repocribro
RUN pip install .

ENV REPOCRIBRO_CONFIG_FILE=/repocribro/config.cfg

# Install plugins
RUN pip install mysqlclient repocribro-file repocribro-badges repocribro-pages

ENTRYPOINT ["repocribro"]
