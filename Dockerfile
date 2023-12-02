FROM public.ecr.aws/lambda/python:3.11

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN yum update -y 
RUN yum install libglvnd-glx -y

RUN pip install matplotlib 
RUN pip install flask 
RUN pip install pillow 
RUN pip install h5py
RUN pip install boto3

COPY . ./
COPY config.json /tmp/
COPY final /tmp/final

EXPOSE 8080
# 
RUN echo $(ls -la ~/.aws/)

WORKDIR /tmp


CMD ["lambda.lambda_handler"]