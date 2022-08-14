FROM public.ecr.aws/lambda/python:3.9 as stage
# Copy function code

RUN yum update -y \
    && yum -y install gcc make \
    && rm -rf /var/lib/apt/lists/*s

RUN yum install wget -y
RUN yum install -y unzip

# Find the version of latest stable build of chromium from below
# https://omahaproxy.appspot.com/
# Then follow the instructions here in below URL
# to download old builds of Chrome/Chromium that are stable
# Current stable version of Chromium
ENV CHROMIUM_VERSION=1002910

COPY install_browser.sh /tmp/
RUN /usr/bin/bash /tmp/install_browser.sh


FROM public.ecr.aws/lambda/python:3.9 as base

COPY chrome-deps.txt /tmp/
RUN yum install -y $(cat /tmp/chrome-deps.txt)

COPY index.py ${LAMBDA_TASK_ROOT}
COPY connector.py ${LAMBDA_TASK_ROOT}
COPY connection_scraper.py ${LAMBDA_TASK_ROOT}
COPY scraper.py ${LAMBDA_TASK_ROOT}
COPY utils.py ${LAMBDA_TASK_ROOT}

#copy requirements to app
COPY requirements.txt .

RUN /var/lang/bin/python3.9 -m pip install --upgrade pip
#RUN  pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
RUN python3.9 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY --from=stage /opt/chrome /opt/chrome
COPY --from=stage /opt/chromedriver /opt/chromedriver

CMD [ "index.scrape_conns" ]