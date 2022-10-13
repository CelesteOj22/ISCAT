import psycopg2
import pandas as pd
import numpy as np
import csv
import os
import pathlib
#class Conn:
#    def __init__ (self):
#        self._conexionSonar
#        self._conexionPrueba
#        self.cur


#    def connect(self):
#        self._conexionPrueba = psycopg2.connect(database="scat_prueba", user="postgres", password="1234")
        # creamos el cursor con el objeto conexion
#        self.cur = conexionPrueba.cursor()

#    def execute(self):
#        self.cur.execute(comando)

#    def close(self):
        # Cerramos la conexión
#        self._conexionPrueba.close()

#    def print(self,campo):#plantear mejor
#        for campo in cur.fetchall():
#            print(campo)


#conexionSonar = psycopg2.connect(database="Sonar", user="postgres", password="1234")
conexionPrueba = psycopg2.connect(database="scat_prueba", user="postgres", password="1234")
cur = conexionPrueba.cursor()

#Ejecutamos una consulta
#cur.execute("SELECT name, description FROM metrics")
i=0
dir='D:/sonar/scripts/proyecto/aoi-2.5.1/SMResults/aoi-2.5.1/java/2022-08-22-17-26-32'
directorio = pathlib.Path(dir)
#Increase the maximum number of rows to display the entire DataFrame
pd.options.display.max_rows = 9999
for file in os.listdir(dir):
    #print(file)
    f = os.path.join(dir, file)
    if os.path.isfile(f) and file.endswith('Component.csv'):
        df=pd.read_csv(f,delimiter=',')
        cur.execute("select * from projects where name like 'aoi-2.5.1'")
        id_project=cur.fetchone()
        cur.execute("Select id_metric,name from metrics")
        for metric in cur.fetchall():
            print(metric)
            try:
                value = df.loc[0,metric[1]]
            except:
                print("Ha ocurrido un error gila")
            else:
                cur.execute("Insert into project_measures(id_metric,id_project,value) values ("+str(metric[0])+","+str(id_project[0])+","+str(value)+")")
                conexionPrueba.commit()
                count = cur.rowcount
                print(count, "Record inserted successfully into mobile table")

    #except (Exception, psycopg2.Error) as error:
    #print("Failed to insert record into mobile table", error)
        #print(df.loc[0])#print(df.loc[0, ''])

#cur.execute(";")




#Recorremos los resultados y los mostramos
#for name, description in cur.fetchall() :
#    print("\n name:"+str(name)+"\t description:" +str(description))
cur.close()
conexionPrueba.close()



