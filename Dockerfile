#Imagen madre
FROM python:3.11-slim

#Configuraciones para pode ver logs de manera correcta
ENV PYTHONBUFFERED=1

#ENV PYTHONUTF8=1 LANG=C.UTF-8 LC_ALL=C.UTF-8


#Directorio de trabajo (donde vamos a pararnos)
WORKDIR /app

#COPIAR ARCHIVO DE DEPENDIENCIAS
COPY requirements.txt .

#INSTALA LAS DEPENDIENCIA VIA pip
RUN pip install --no-cache-dir -r requirements.txt

#COPIAMOS CÓDIGO FUENTE DEL PROYECTO DENTRO DE LA IMAGEN
COPY . . 