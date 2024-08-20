# 
FROM python:3.10

# 
RUN mkdir /code


WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN pip install --no-cache-dir itsdangerous
# 
COPY . /code/.

RUN chmod a+x docker/*.sh

# 
CMD ["fastapi", "run", "google_sheets/oauth.py", "--port", "80"]
