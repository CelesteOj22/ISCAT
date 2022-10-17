import subprocess
import os
import pandas as pd
import Servidor.DBOperaciones as db
import Servidor.APIOperaciones as api
from subprocess import check_output
from sonarQube import SonarQube
from sourceMeter import SourceMeter
import pathlib
dir="D:/sonar/scripts/proyecto"
#dir="D:/JuanCarr"
sonar = SonarQube("bin")
source= SourceMeter("SMResults")
#subprocess.Popen("cd D:/sonar/scripts",shell=True)

directorio = pathlib.Path(dir)
print("Comenzando el analisis de "+str(len(os.listdir(dir)))+" proyectos")#+"\n"+"La carpeta de proyectos se encuentra en: "+dir+"\n"


for proyecto in directorio.iterdir():
    sonar.analizar('D:/sonar/sonar-scanner-4.7.0.2747-windows/bin/sonar-scanner.bat',proyecto.__str__())
    #print(proyecto.__str__())
    source.analizar('D:\sonar\SourceMeter-10.0.0-x64-Windows\Java\SourceMeterJava.exe',proyecto.__str__())



"""
#source.analizar('D:\sonar\SourceMeter-10.0.0-x64-Windows\Java\SourceMeterJava.exe','D:\sonar\scripts\proyecto\\aoi-2.5.1')
# D:\sonar\scripts\proyecto\aoi-2.5.1\SMResults\aoi-2.5.1\java\fecha
#db.guardarValores('D:\sonar\scripts\proyecto\\aoi-2.5.1', 'aoi-2.5.1')


path= "D:\sonar\scripts\proyecto\cobertura-1.9\SMResults\cobertura-1.9\java\\2022-08-22-17-54-59"
try:
    for file in os.listdir(path):
        # print(file)
        f = os.path.join(path, file)
        if os.path.isfile(f) and file.endswith('Interface.csv'):
            df = pd.read_csv(f, delimiter=',')
            df.set_index('Path')
            print(df.query('Name=CoverageData'))
except:
    pass"""

