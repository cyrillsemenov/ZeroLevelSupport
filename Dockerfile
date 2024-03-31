FROM python:3.10-slim

WORKDIR /usr/src/webapp

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/webapp/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/webapp/entrypoint.sh
RUN chmod +x /usr/src/webapp/entrypoint.sh

# copy project
COPY . /usr/src/webapp/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/webapp/entrypoint.sh"]

# # Define the command to run your app using gunicorn
# # Adjust the command according to how you start your Django project
# CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
