FROM python:2

ADD gc-scraper.py /

RUN pip install mechanize
RUN pip install beautifulsoup4

CMD [ "python", "./gc-scraper.py" ]