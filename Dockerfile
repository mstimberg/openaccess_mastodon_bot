FROM python:3.10
WORKDIR /bot
COPY . /bot
RUN pip install .
CMD ["python", "-m", "oabot"]
