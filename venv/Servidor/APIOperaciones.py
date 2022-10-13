import requests
import json
import Servidor.DBOperaciones as db
import psycopg2

# -----------------------Conexion-----------------------------
def getUrl(url):
    return 'http://localhost:9000/api/'+url+'&p=1&ps=500'

#url_projects='http://localhost:9000/api/projects/search?projects=log4j&p=1&ps=500'
#conexion(getUrl('projects/search?projects=log4j'))

def conexion(url):
    response = requests.get(url, auth=('admin', 'adminn'))
    if response.status_code == 200:  # procede si se establece la conexion
        json = JSON(response)
        return json
    else:
        print('Conexion fallida! Intente nuevamente.')


def JSON(response):
    response_json = json.loads(response.text)  # guarda en una variable el contenido de la api que estamos consumiendo
    return response_json


# ----------------------------------------------------
def getLastAnalysisSQ(projectKey):
    try:
        project = getProjectSQ(projectKey)
        #print(response)
        lastAnalysis = project['lastAnalysisDate']
        #print(lastAnalysis)
    except (Exception, requests.RequestException) as error:
        print('Consulta fallida! Intente nuevamente.', error)
    else:
        return lastAnalysis

def getProjectSQ(projectKey):
    try:
        response = conexion(getUrl('projects/search?projects=' + projectKey))
        project = response['components'][0]
    except (Exception, requests.RequestException) as error:
        print('Consulta fallida! Intente nuevamente.', error)
    else:
        return project


def getComponentsSQ(projectKey):
    try:
        response = conexion(getUrl('components/tree?component=' + projectKey))
        components = response['components']
    except (Exception, requests.RequestException) as error:
        print('Consulta fallida! Intente nuevamente.', error)
    else:
        return components


def getMetricsSQ():
    try:
        response = conexion(getUrl('metrics/search?'))
        metrics = response['metrics']
    except (Exception, requests.RequestException) as error:
        print('Consulta fallida! Intente nuevamente.', error)
    else:
        return metrics


def getMeasureSQ(projectKey,metric,qualifier):
    try:
        response = conexion(getUrl('measures/component?component='+projectKey+'&qualifier='+qualifier+'&metricKeys='+metric))
        measure = response['component']['measures'][0]['value']
    except:
        pass
    else:
        return measure


def fechaHoraSQ(lastAnalysis):
    sep = lastAnalysis.split('T')
    fechahora = sep[0] + ' ' + sep[1].split('-')[0]
    return fechahora

def insertProjectSQ(projectKey,fechahora):
    if db.projectExists(projectKey):
        db.updateProject(projectKey,fechahora,'sq')
    else:
        key = getProjectSQ(projectKey)
        db.insertProject(key['key'],projectKey,fechahora,'sq')


def insertComponentSQ(projectKey):
    try:
        con = db.getConexion()
        cur = db.cursor(con)
        components = getComponentsSQ(projectKey)
        cur.execute("select * from projects where name like %s", (projectKey,))  # datos del proyecto guardado en projects
        id_project = cur.fetchone()  # agarra el primero
        for c in components:
            if db.componentExists((c)['path']):
                pass
            else:
                db.insertComponent((id_project[0],(c)['qualifier'],(c)['path'],(c)['key']))
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert components", error)
    else:
        print("List of components inserted successfully into table")
    finally:
        db.closeCon(cur, con)



def insertMetricSQ():
    #revisar despues por valores repetidos
    metrics = getMetricsSQ()
    for m in metrics:
        try:
            db.insertMetric(((m)['name'], (m)['description'], (m)['domain'], 'SonarQube', (m)['key']))
        except:
            db.insertMetric(((m)['name'], (m)['name'], (m)['domain'], 'SonarQube', (m)['key']))



def insertProjectMeasuresSQ(projectKey):
    # Increase the maximum number of rows to display the entire DataFrame
    try:
        con = db.getConexion()
        cur = db.cursor(con)
        cur.execute("select * from projects where name like %s",(projectKey,))  # datos del proyecto guardado en projects
        id_project = cur.fetchone()  # agarra el primero
        cur.execute("Select id_metric,key from metrics where tool like 'SonarQube'")  # todas los ids y nombres de metricas guardadas en metrics
        metricsbd = cur.fetchall()
        for metric in metricsbd:  # por cada metrica
            try:
                value = getMeasureSQ(projectKey,metric[1],'TRK')
            except:
                pass
            else:
                db.insertProjectMeasures((metric[0], id_project[0], value))
            pass
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert project measures", error)
    else:
        print("List of project measures inserted successfully into table")
    finally:
        db.closeCon(cur, con)


def insertComponentMeasuresSQ(projectKey):
    # Increase the maximum number of rows to display the entire DataFrame
    try:
        con = db.getConexion()
        cur = db.cursor(con)
        cur.execute("select * from projects where name like %s", (projectKey,))  # datos del proyecto guardado en projects
        id_project = cur.fetchone()  # agarra el primero
        cur.execute("Select id_metric,key from metrics where tool like 'SonarQube'")
        metrics = cur.fetchall()  # todas los ids y nombres de metricas guardadas en metrics
        cur.execute("select id_component,key,qualifier from components where id_project = %s",(id_project[0],))
        components = cur.fetchall()
        for component in components:
            for metric in metrics:  # por cada metrica
                try:
                    value = getMeasureSQ(projectKey,metric[1],component[2])
                except:
                    pass
                else:
                    db.insertComponentMeasures(metric[0], component[0], value)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert component measures", error)
    else:
        print("List of metrics inserted successfully into table")
    finally:
        db.closeCon(cur, con)


def ListaProv(response_json):  # func de lista de provincia
    provl = list()  # creamos la lista para almacenar las provincias
    for i in response_json:  # recorremos el diccionario

        if len(provl) == 0:  # verifica si hay elementos en la lista de provincias
            provl.append((i)['province'])  # carga el primer elemento
            continue
        else:
            if (i)['province'] in provl:  # evalua si la provincia ya se encuentra en la lista
                continue  # sigue recorriendo el json
            else:
                provl.append((i)['province'])  # si la provincia no se encuentra en la lista,
                continue
    return provl


def ListaLoc(prov, response_json):  # func de lista de localidades
    n = 0  # contador para para señalizar el indice de cada localidad
    locl = list()  # se crea la lista para almacenar las localidades
    for i in response_json:
        if (i)['province'] == prov:  # si la provincia en el json  es igual a la que se pasa por parametro (prov)
            locl.append((i)['name'])  # se guarda en la lista la localidad
        else:
            continue
    return locl


def MostrarLista(lista):
    n = 0  # contador para señalizar el indice de cada provincia/localidad
    for i in lista:  # recorre la lista
        print(n, ' ', lista[n])  # lista con las provincias/localidades que se pueden llegar a usar
        n = n + 1
        continue


# -----------------------Extraccion de atributos de interes-----------------------------
def Clima(prov, loc, response_json):
    for i in response_json:
        if (i)['province'] == prov and (i)['name'] == loc:
            h = (i)['weather']['humidity']  # humedad
            velv = (i)['weather']['wind_speed']  # velocidad del viento
            t = (i)['weather']['temp']  # temperatura
        else:
            continue
    print('\n\nProvincia: ', prov, '\nLocalidad: ', loc, '\nHumedad: ', h, '\nVelocidad del Viento: ', velv,
          '\nTemperatura: ', t)
    return h, velv, t
