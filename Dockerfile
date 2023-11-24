FROM continuumio/miniconda3:latest

RUN conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

COPY env.yml .

RUN apt-get update && apt-get install libgl1 -y
RUN conda env create --prefix ./parkvic -f ./env.yml
RUN conda install -c conda-forge opencv -y
RUN conda install matplotlib -y
RUN conda install flask -y

COPY . /parkvic/WasteCounter

WORKDIR /parkvic/WasteCounter

RUN ls

SHELL ["conda", "run", "-n", "parkvic", "/bin/bash", "-c"]

EXPOSE 8080

CMD ["ls","python", "window_app.py"]