FROM debian:10

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    make \
    procps \
    sudo \
    vim

RUN addgroup --gid 1000 vscode \
    && adduser --uid 1000 --gid 1000 --disabled-password --gecos vscode vscode \
    && adduser vscode sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/sudo

RUN DEBIAN_FRONTED=noninteractive apt-get install -y \
    git \
    python3 \
    python3-psutil \
    python3-venv \
    python3-wheel \
    python3-dev \
    build-essential \
    libpq-dev
    
# create venv folder 
RUN mkdir /opt/venv \
    && chown 1000:1000 /opt/venv

USER 1000

RUN python3 -m venv --system-site-packages /opt/venv

ENV PATH=/opt/venv/bin:$PATH \
    VIRTUAL_ENV=/opt/venv

RUN pip install \
    black \
    flake8 \
    ipdb \
    pycodestyle \
    pytest \
    python-dotenv \
    psycopg2-binary \
    markupsafe==2.0.1
