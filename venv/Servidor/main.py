
import subprocess
import os
import pathlib
from sonarQube import SonarQube
from sourceMeter import SourceMeter
import pandas as pd
import Servidor.DBOperaciones as db
import Servidor.APIOperaciones as api
from subprocess import check_output
from datetime import datetime
import time
from datetime import timedelta

dir="D:/sonar/scripts/proyecto"
#dir="D:/JuanCarr"
sonar = SonarQube("bin")
source= SourceMeter("SMResults")
#subprocess.Popen("cd D:/sonar/scripts",shell=True)


#print("Integrated SCAT")
#print("\nSeleccione la herramienta con la que desea llevar a cabo el analisis de sus proyectos:\n1- Sonar Qube\n2- SourceMeter\n3- Ambas")
#herramienta = input()
#dir = str(input("Ingrese a continuación el directorio donde se encuentran sus proyectos a analizar: "))


directorio = pathlib.Path(dir)
print("Comenzando el analisis de "+str(len(os.listdir(dir)))+" proyectos")#+"\n"+"La carpeta de proyectos se encuentra en: "+dir+"\n"

timesonarIni = datetime.now().time()
print(timesonarIni)
for proyecto in directorio.iterdir():
    sonar.analizar('D:/sonar/sonar-scanner-4.7.0.2747-windows/bin/sonar-scanner.bat',proyecto.__str__())

timesonarFin = datetime.now().time()
print(timesonarFin)


def restar_hora(hora1, hora2):
    formato = "%H:%M:%S.%f"
    h1 = datetime.strptime(hora1, formato)
    h2 = datetime.strptime(hora2, formato)
    resultado = h1 - h2
    return str(resultado)

horasSQ= restar_hora(timesonarFin.__str__(),timesonarIni.__str__())
print("sonar:")
print(horasSQ)


print("\n\nEl analisis con Sonar Qube comenzó a las: "+timesonarIni.__str__())
print("Tiempo total de analisis de lote con Sonar Qube: "+ horasSQ)

timesourceIni = datetime.now().time()
for proyecto in directorio.iterdir():
    source.analizar('D:\sonar\SourceMeter-10.0.0-x64-Windows\Java\SourceMeterJava.exe',proyecto.__str__())
    #print(proyecto.__str__())

timesourceFin = datetime.now().time()
horasSM= restar_hora(timesourceFin.__str__(),timesourceIni.__str__())
print("source:")
print(horasSM)


print("\n\nEl analisis con SourceMeter comenzó a las: "+timesourceIni.__str__())
print("Tiempo total de analisis de lote con SourceMeter: "+ horasSM)

print("\n\nResumen de tiempo de analisis:")
print("Tiempo total de analisis de lote con Sonar Qube: "+ horasSQ)
print("Tiempo total de analisis de lote con SourceMeter: "+ horasSM)
