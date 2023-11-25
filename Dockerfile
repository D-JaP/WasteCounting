FROM python:3.11.6

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY env.yml .

# RUN yum update -y 
# RUN yum install libglvnd-glx -y
RUN apt-get update -y 
RUN apt-get install libgl1 -y
RUN pip install matplotlib 
RUN pip install flask 
RUN pip install pillow 
RUN pip install h5py

COPY . /parkvic/WasteCounter

WORKDIR /parkvic/WasteCounter

EXPOSE 8080

CMD ["python", "web_app.py"]