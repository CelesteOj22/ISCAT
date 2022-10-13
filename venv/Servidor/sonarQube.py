from IHerramienta import *
import subprocess #para mandarle comandos a la consola
from subprocess import check_output
from datetime import datetime
import Servidor.DBOperaciones as db


class SonarQube(IHerramienta):
    def __init__ (self, binaries: str, host="http://localhost:9000"):
        self._sources="."
        self._hosturl= host
        #self._login=login
        self._binaries=binaries

#sonar= sonarQube("D:\sonar\sonar-scanner-4.7.0.2747-windows\bin\scanner.bat","proyecto",".","http://localhost:9000","6d047c32f875ad34e45a6c712cde319c0b9074cd","build/bin",carpeta proyecto)

    def analizar(self,scanner, projectName):
        sep = projectName.split(sep='\\')
        projectKey= sep[4]
        comando = 'cd '+projectName+' && '+scanner+' -Dsonar.projectKey='+projectKey+' -Dsonar.sources='+self._sources+' -Dsonar.host.url='+self._hosturl+' -Dsonar.java.binaries='+self._binaries
        #check_output(comando, shell=True)

        try:
            #print("\nAnalisis con SonarQube-8.9.8 \nIniciando analisis del proyecto: " + projectkey)
            stdout = subprocess.run(comando, stdout=subprocess.PIPE, universal_newlines=True, check=True, text=True,shell=True).stdout
            if 'EXECUTION SUCCESS' in stdout:
                print("El proyecto " + projectKey + " ha sido analizado con exito!")
        except:
            print("Ha ocurrido un error durante el analisis del proyecto "+projectKey)
        else:
            db.guardarValoresSQ(projectKey)


        #time = str(datetime.now().time())
        #time = time.replace(":",".")
        #log = open("D:/sonar/scripts/Logs/Log-"+str(datetime.now().date())+"-"+time+".txt","w")
        #str1 = repr(stdout)
        #log.write(str1 + "\n")
        #log.close()






