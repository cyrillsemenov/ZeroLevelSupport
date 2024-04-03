FROM python:3.10-slim

WORKDIR /usr/src/webapp

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/webapp/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/webapp/entrypoint.sh
RUN chmod +x /usr/src/webapp/entrypoint.sh

COPY . /usr/src/webapp/

HEALTHCHECK --interval=10m --timeout=5s \
    CMD curl -f http://localhost/ || exit 1

RUN addgroup --system webapp && adduser --system --group webapp
USER webapp

ENTRYPOINT ["/usr/src/webapp/entrypoint.sh"]
