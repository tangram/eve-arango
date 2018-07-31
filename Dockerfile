FROM python:3.6

WORKDIR /app
ADD . /app

RUN pip install .
RUN pip install pylint pytest pytest-cov

CMD sleep 5 && \
    pylint -E eve_arango && \
    pytest -svv --cov=eve_arango
