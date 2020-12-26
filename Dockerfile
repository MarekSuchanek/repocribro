FROM python:3.6

WORKDIR /repocribro

# Install dependencies (caching)
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install package
COPY . /repocribro
RUN pip install .

# Install plugins
RUN pip install repocribro-file repocribro-badges repocribro-pages

ENTRYPOINT ["repocribro"]
