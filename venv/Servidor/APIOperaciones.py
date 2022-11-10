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




