# Get base image of python
FROM python:3.8

RUN apt-get install -y wget

#Adding trsuting keys to apt
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

#Add Google Chrome
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

#Update apt
RUN apt-get -y update

#Install google chrome
RUN apt-get install -y google-chrome-stable

#Download google chrome driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

#Download unzipper
RUN apt-get install -yqq unzip

#Unzip file
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Copy only the necessary files for the scraper
COPY Web_Scraper.py .

COPY requirements.txt .

COPY Dockerfile .

#Install all the dependencies 
RUN pip install -r requirements.txt

#Run the scraper 
CMD ["python", "Web_Scraper.py"]