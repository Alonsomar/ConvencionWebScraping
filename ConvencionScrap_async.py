# -*- coding: utf-8 -*-
"""

@author: Alonso Valdés
https://github.com/Alonsomar

"""

import pandas as pd
import grequests #Importar antes de requests
import requests

import json

from bs4 import BeautifulSoup
from time import time
from datetime import datetime

#%%%
# Búsqueda de todas las sesiones de la web
t0 = time()

url_sesiones = 'https://sala.cconstituyente.cl/doGet.asmx/getSesiones'

busqueda = requests.get(url_sesiones)
sesiones = json.loads(busqueda.text)['data']

sesiones_id = []
for sesion in sesiones:
    sesiones_id.append(sesion['Id'])
    
#%%
# Funciones con parámetros de búsqueda y para hacer requests async
def ses_params(s_id_list):
    return [{'prmSesionId': s_id} for s_id in  s_id_list]

def vot_params(v_id_list):
    return [{'prmVotacionId': v_id} for v_id in  v_id_list]

def get_data(link, params_list):
    reqs = [grequests.get(link, params=par) for par in params_list]
    par_name = next(iter(params_list[0]))
    resp = dict(zip([d[par_name] for d in params_list], grequests.map(reqs)))
    return resp

#%%%
# Búsqueda de todas las asistencias por sesión
url_asist = 'https://sala.cconstituyente.cl/views/AsistenciaPorSesion.aspx'

def parse_asistencias(resp):
    data_asistencias = []
    for i, (ses_id, r) in enumerate(resp.items()):
        tabla_asistencias = BeautifulSoup(r.text, 'html.parser').find_all(class_ ="table table-hover tabla-asistencia")
        for tr in tabla_asistencias[1].find_all('tr'):
            values = [td.text.strip() for td in tr.find_all('td') if td.text.strip()]
            values.insert(0, ses_id)
            data_asistencias.append(values)
    return data_asistencias

resp = get_data(url_asist, ses_params(sesiones_id))
data_asistencias = parse_asistencias(resp)

#%%%
# Búsqueda de todas las votaciones por sesión
url_vota = 'https://sala.cconstituyente.cl/doGet.asmx/getVotacionesPorSesion'

def parse_votaciones(resp):
    votaciones = []
    for i, (ses_id, r) in enumerate(resp.items()):
        vot_extend = json.loads(r.text)['data']
        vot_extend = [dict(item, **{'IdSesion':ses_id}) for item in vot_extend]
        votaciones.extend(vot_extend)
    return votaciones

resp = get_data(url_vota, ses_params(sesiones_id))
votaciones = parse_votaciones(resp)

votaciones_id = []
for votacion in votaciones:
    votaciones_id.append(votacion['Id'])

#%%%
# Búsqueda de detalle de las votaciones
url_detail = 'https://sala.cconstituyente.cl/views/VotacionDetalle.aspx'

def parse_resultado(resp):    
    detalle_vota = []
    orden_resultado = ['Favor', 'Contra', 'Abstención', 'Dispensados']
    for i, (vot_id, r) in enumerate(resp.items()):
        tabla_votacion = BeautifulSoup(r.text, 'html.parser').find(class_ ='col-lg-12 votacion-detalle')
        det_vot = tabla_votacion.find_all(class_= 'row')
        for num, orden in enumerate(orden_resultado):
            for div in det_vot[num*2 +1 ].find_all('div'):
                values = [vot_id, orden, div.text.strip()]
                detalle_vota.append(values)

resp = get_data(url_detail, vot_params(votaciones_id))
detalle_vota = parse_resultado(resp)

print(f'Downloading took {time()-t0:2.2f} seconds')

#%%
# Genera DataFrames para guardarlos en formato csv
sesiones_col = ['IdSesion', 'Numero', 'Nombre', 'DiscucionPresupuesto', 'FechaTexto', 'Tipo',
       'FechaInicio', 'FechaTermino', 'Estado', 'BoletinId', 'SintesisId',
       'ActaId']
asistencias_col = ['IdSesion', 'Convencional', 'HoraIngreso', 'Asistencia', 'Observaciones']
votaciones_col = ['IdVotacion', 'Descripcion', 'Materia', 'Articulo', 'Tramite', 'Fecha',
       'Sesion', 'TotalSI', 'TotalNO', 'TotalAbstencion', 'TotalDispensado',
       'Resultado', 'Votos', 'IdSesion']
det_vot_col = ['IdVotacion', 'Voto', 'Nombre']

dat_sesiones = pd.DataFrame(sesiones)
dat_sesiones.columns = sesiones_col
dat_asistencias = pd.DataFrame(data_asistencias, columns= asistencias_col)
dat_votaciones = pd.DataFrame(votaciones)
dat_votaciones.columns = votaciones_col
dat_votaciones_detalle = pd.DataFrame(detalle_vota, columns= det_vot_col)

#%%
#Cambio en el formato de fecha milisec-Javascript a string
dat_sesiones['FechaInicio'] = [datetime.fromtimestamp(int(txt[6:-2])/1000.0) for txt in dat_sesiones['FechaInicio']]
dat_sesiones['FechaTermino'] = [datetime.fromtimestamp(int(txt[6:-2])/1000.0) for txt in dat_sesiones['FechaTermino']]

#%%
# Opción de guardado en formato .csv
#Ubicación de la carpeta de guardado
carpeta_local = r'C:/Users/'  

dat_sesiones.to_csv(carpeta_local +'dat_sesiones.csv', index = False, sep= ';')
dat_asistencias.to_csv(carpeta_local +'dat_asistencias.csv', index = False, sep= ';')
dat_votaciones.to_csv(carpeta_local +'dat_votaciones.csv', index = False, sep= ';')
dat_votaciones_detalle.to_csv(carpeta_local +'dat_votaciones_detalle.csv', index = False, sep= ';')

