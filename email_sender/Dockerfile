FROM public.ecr.aws/lambda/python:3.9 as base


COPY index.py ${LAMBDA_TASK_ROOT}
COPY properties.py ${LAMBDA_TASK_ROOT}
COPY utils.py ${LAMBDA_TASK_ROOT}

#copy requirements to app
COPY requirements.txt .

RUN /var/lang/bin/python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "index.transmit_email" ]