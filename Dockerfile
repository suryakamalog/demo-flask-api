FROM python:latest
COPY ./requirements.txt /flask-tutorial/requirements.txt

WORKDIR /flask-tutorial/

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
CMD ["tail", "-f", "/dev/null"]