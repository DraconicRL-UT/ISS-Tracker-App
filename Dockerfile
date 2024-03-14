FROM ubuntu:20.04
#FROM python:3.9

#RUN mkdir /app
#WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 \
		       python3-pip

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt
RUN pip install pytest==8.0.0
RUN pip install --user requests
RUN pip install --user flask
RUN pip install --user xmltodict
RUN pip install --user astropy
RUN pip install --user geopy

COPY iss_tracker.py /code/iss_tracker.py

COPY test_iss_tracker.py /code/test_iss_tracker.py

RUN chmod +rx /code/test_iss_tracker.py
RUN chmod +rx /code/iss_tracker.py

ENV PATH="/code:$PATH"

#ENTRYPOINT ["python"]
CMD ["iss_tracker.py"]

