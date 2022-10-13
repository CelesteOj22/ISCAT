import psycopg2
import pandas as pd
import numpy as np
import csv
import os
import pathlib
import numpy
import json
import Servidor.APIOperaciones as api
from psycopg2.extensions import register_adapter, AsIs

#Conexion a base de datos scat_prueba
def getConexion():
    try:
        conexionPrueba = psycopg2.connect(database="scat_prueba", user="postgres", password="1234")
        return conexionPrueba
    except (Exception, psycopg2.Error) as error:
        print("Failed to conect to the database", error)


def cursor(conexionPrueba):
    cur = conexionPrueba.cursor()
    return cur


def closeCon(cur, conexionPrueba):
    if conexionPrueba:
        cur.close()
        conexionPrueba.close()
        # print("PostgreSQL connection is closed")


def commit(conexionPrueba):
    conexionPrueba.commit()


# selects
def getAllProjects():
    try:
        con = getConexion()
        cur = cursor(con)
        cur.execute("SELECT * FROM PROJECTS")
        return cur.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Failed to bring all projects", error)
    finally:
        closeCon(cur, con)


def getProject(projectKey):
    try:
        con = getConexion()
        cur = cursor(con)
        cur.execute("SELECT * FROM PROJECTS where name like %s",(projectKey,))
        return cur.fetchone()
    except (Exception, psycopg2.Error) as error:
        print("Failed to bring project", error)
    finally:
        closeCon(cur, con)


def projectExists(projectKey):
    try:
        con = getConexion()
        cur = cursor(con)
        cur.execute("SELECT * FROM PROJECTS where name like %s",(projectKey,))
        if cur.fetchone():
            return True
        else:
            return False
    except (Exception, psycopg2.Error) as error:
        print("Fail", error)
    finally:
        closeCon(cur, con)


def componentExists(path):
    try:
        con = getConexion()
        cur = cursor(con)
        cur.execute("SELECT * FROM components where path like %s",(path,))
        if cur.fetchone():
            return True
        else:
            return False
    except (Exception, psycopg2.Error) as error:
        print("Fail", error)
    finally:
        closeCon(cur, con)


# Updates
def updateProject(projectKey,lastAnalysis, tool):
    try:
        con = getConexion()
        cur = cursor(con)
        if tool == 'sm':
            cur.execute("UPDATE projects SET lastAnalysissm = timestamp %s WHERE name like %s",(lastAnalysis,projectKey))
        else:
            cur.execute("UPDATE projects SET lastAnalysissq = timestamp %s WHERE name like %s",(lastAnalysis,projectKey))

        commit(con)
    except (Exception, psycopg2.Error) as error:
        print("Failed to update project", error)
    else:
        print("Project updated successfully")
    finally:
        closeCon(cur, con)


# Inserts
def insertProject(key, name: str, lastAnalysis,tool):
    try:
        con = getConexion()
        cur = cursor(con)
        if tool == 'sm':
            cur.execute("INSERT INTO projects(name,lastAnalysissm) values (%s,timestamp %s)",
                    (name, lastAnalysis))
        else:
            cur.execute("INSERT INTO projects(key,name,lastAnalysissq) values (%s,%s,timestamp %s)",
                        (key, name, lastAnalysis))
        commit(con)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert project", error)
    else:
        print("Project inserted successfully into table")
    finally:
        closeCon(cur, con)


def insertMetric(metrics):  # lista
    try:
        con = getConexion()
        cur = cursor(con)
        cur.execute("INSERT INTO metrics(name,description,domain,tool,key) values (%s,%s,%s,%s,%s)", metrics)
        commit(con)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert metrics", error)
    else:
        print("List of metrics inserted successfully into table")
    finally:
        closeCon(cur, con)


def insertComponent(components):  # lista
    try:
        register_adapter(numpy.float64, addapt_numpy_float64)
        register_adapter(numpy.int64, addapt_numpy_int64)
        con = getConexion()
        cur = cursor(con)
        #si es con tool puedo sacar el insert de key para sm
        cur.execute("INSERT INTO components(id_project,qualifier,path,key) values (%s,%s,%s,%s)", components)
        commit(con)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert component", error)
    finally:
        closeCon(cur, con)


def insertComponentMeasures(id_metric, id_component, value):
    try:
        register_adapter(numpy.float64, addapt_numpy_float64)
        register_adapter(numpy.int64, addapt_numpy_int64)
        con = getConexion()
        cur = cursor(con)
        cur.execute("INSERT INTO component_measures(id_metric,id_component,value) values (%s,%s,%s)", (str(id_metric), str(id_component), str(value)))
        commit(con)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert component measures", error)
    finally:
        closeCon(cur, con)


def insertProjectMeasures(project_measures):
    try:
        register_adapter(numpy.float64, addapt_numpy_float64)
        register_adapter(numpy.int64, addapt_numpy_int64)
        con = getConexion()
        cur = cursor(con)
        cur.execute("INSERT INTO project_measures(id_metric,id_project,value) values (%s,%s,%s)", project_measures)
        commit(con)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert project measures", error)
    finally:
        closeCon(cur, con)

def fechaHora(lastAnalysis):
    sep = lastAnalysis.split('-')
    fecha = sep[0] + '-' + sep[1] + '-' + sep[2]
    hora = sep[3] + ':' + sep[4] + ':' + sep[5]
    return fecha + ' ' + hora

def fechaHoraSQ(lastAnalysis):
    sep = lastAnalysis.split('T')
    return sep[0]+' '+sep[1]

def guardarValoresSM(projectName, projectKey):
    # metricas a nivel de proyecto
    lastAnalysis = getLastAnalysisSM(projectName, projectKey)
    fechahora = fechaHora(lastAnalysis)
    insertProject(None,projectKey, fechahora,'sm')
    path = projectName + "\\SMResults\\" + projectKey + "\\java\\" + lastAnalysis
    insertProjectMeasuresSM(path, projectKey)
    # metricas a nivel de componente
    insertComponentSM(path, projectKey)
    insertComponentMeasuresSM(path, projectKey)

def guardarValoresSQ(projectKey):
    print('empiezaaa guardar')
    lastAnalysis = api.getLastAnalysisSQ(projectKey)
    print('lastAnalisys vieja')
    fechahora = fechaHoraSQ(lastAnalysis)
    print(fechahora)
    api.insertProjectSQ(projectKey,fechahora)
    print('insert viejaaa')
    api.insertProjectMeasuresSQ(projectKey)
    print('project measures viejaaa')
    api.insertComponentSQ(projectKey)
    print('component viejaaa')
    api.insertComponentMeasuresSQ(projectKey)

#SonarQube


#SourceMeter
def getLastAnalysisSM(projectName: str, projectKey: str):
    # D:\sonar\scripts\proyecto\aoi-2.5.1\SMResults\aoi-2.5.1\java\fecha
    path = projectName + "\\SMResults\\" + projectKey + "\\java"
    cant = len(os.listdir(path))
    folders = os.listdir(path)
    lastAnalysis = folders[cant - 1]
    return lastAnalysis

def insertProjectMeasuresSM(path, projectKey):
    # Increase the maximum number of rows to display the entire DataFrame
    try:
        con = getConexion()
        cur = cursor(con)
        pd.options.display.max_rows = 9999
        dir = os.listdir(path)
        for file in dir:
            # print(file)
            f = os.path.join(path, file)
            if os.path.isfile(f) and file.endswith('Component.csv'):
                df = pd.read_csv(f, delimiter=',')
                cur.execute("select * from projects where name like %s", (projectKey,))  # datos del proyecto guardado en projects
                id_project = cur.fetchone()  # agarra el primero
                cur.execute("Select id_metric,name from metrics")  # todas los ids y nombres de metricas guardadas en metrics
                metrics = cur.fetchall()
                for metric in metrics:  # por cada metrica
                    try:
                        value = df.loc[0, metric[1]]  # lee en el archivo component el valor para la metrica actual.
                    except:
                        pass
                    else:
                        insertProjectMeasures((metric[0], id_project[0], value))
            # insertar un break para cuando encuentre component.csv
            else:
                pass
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert project measures", error)
    else:
        print("List of project measures inserted successfully into table")
    finally:
        closeCon(cur, con)

def insertComponentMeasuresSM(path, projectKey):
    # Increase the maximum number of rows to display the entire DataFrame
    try:
        con = getConexion()
        cur = cursor(con)
        pd.options.display.max_rows = 9999
        dir = os.listdir(path)
        for file in dir:
            # print(file)
            f = os.path.join(path, file)
            if os.path.isfile(f) and (file.endswith('-Class.csv') or file.endswith('-File.csv') or file.endswith('-Package.csv')):  # or file.endswith('Method.csv') or file.endswith('Interface.csv')
                df = pd.read_csv(f, delimiter=',')
                cur.execute("select * from projects where name like %s", (projectKey,))  # datos del proyecto guardado en projects
                id_project = cur.fetchone()  # agarra el primero
                cur.execute("Select id_metric,name from metrics where tool = SourceMeter")
                metrics = cur.fetchall()  # todas los ids y nombres de metricas guardadas en metrics
                if file.endswith('-File.csv'):
                    df.set_index('LongName', inplace=True)
                    cur.execute("select id_component,path from components where id_project = %s and qualifier like 'FIL'", (id_project[0],))  # componentes para el proyecto especifico
                elif file.endswith('-Class.csv'):
                    df.set_index('Path', inplace=True)
                    cur.execute("select id_component,path from class where id_project = %s and qualifier like 'Class'", (id_project[0],))
                components = cur.fetchall()
                for component in components:
                    for metric in metrics:  # por cada metrica
                        try:
                            # print(component[1]+' '+metric[1])
                            value = df.loc[component[1], metric[1]]  # lee en el archivo component el valor para la metrica actual
                        except:
                            pass
                        else:
                            insertComponentMeasures(metric[0], component[0], value)
                df.reset_index()
            else:
                pass
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert component measures", error)
    else:
        print("List of metrics inserted successfully into table")
    finally:
        closeCon(cur, con)

def insertComponentSM(path, projectKey):
    # Increase the maximum number of rows to display the entire DataFrame
    pd.options.display.max_rows = 9999
    try:
        con = getConexion()
        cur = cursor(con)
        dir = os.listdir(path)
        for file in dir:
            # print(file)
            f = os.path.join(path, file)
            if os.path.isfile(f) and (file.endswith('-Class.csv') or file.endswith('-File.csv')):
                #qualifier = getQualifierSM(str(file))
                df = pd.read_csv(f, delimiter=',')
                #este execute puede ir afuera del for para hacerlo una sola vez
                cur.execute("select * from projects where name like %s",
                            (projectKey,))  # datos del proyecto guardado en projects
                id_project = cur.fetchone()  # agarra el primero
                i = 0
                while i < len(df):  # recorre los elementos del df y va guardando cada component
                    if file.endswith('-File.csv'):
                        insertComponent((id_project[0], 'FIL', df.loc[i, 'LongName'],None))
                    else:
                        #insert classssssss
                        insertComponent((id_project[0], 'Class', df.loc[i, 'Path'],None))
                    i += 1
            else:
                pass
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert components", error)
    else:
        print("List of components inserted successfully into table")
    finally:
        closeCon(cur, con)


def getQualifierSM(file: str):
    sep1 = file.split('-')
    sep2 = sep1[len(sep1) - 1].split('.')
    qualifier = sep2[0]
    return qualifier





#addapt numpy
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


"""
    #postgres_insert_query =  INSERT INTO mobile (ID, MODEL, PRICE) VALUES (%s,%s,%s)
    #record_to_insert = (5, 'One Plus 6', 950)
    #cursor.execute(postgres_insert_query, record_to_insert)

    #connection.commit()
    #count = cursor.rowcount
    #print(count, "Record inserted successfully into mobile table")




#    def print(self,campo):#plantear mejor
#        for campo in cur.fetchall():
#            print(campo)


#conexionSonar = psycopg2.connect(database="Sonar", user="postgres", password="1234")
conexionPrueba = psycopg2.connect(database="scat_prueba", user="postgres", password="1234")
cur = conexionPrueba.cursor()


"""
