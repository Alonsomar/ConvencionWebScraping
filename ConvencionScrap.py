# -*- coding: utf-8 -*-
"""

@author: Alonso Valdés
https://github.com/Alonsomar

"""

import pandas as pd
import requests
import json
import pickle

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
    
#%%%
# Búsqueda de todas las asistencias por sesión
url_asist = 'https://sala.cconstituyente.cl/views/AsistenciaPorSesion.aspx'

def ses_params(s_id):
    return {'prmSesionId': s_id}

data_asistencias = []
for ses_id in sesiones_id:
    busqueda = requests.get(url_asist, params=ses_params(ses_id))
    tabla_asistencias = BeautifulSoup(busqueda.text, 'html.parser').find_all(class_ ="table table-hover tabla-asistencia")
    
    for tr in tabla_asistencias[1].find_all('tr'):
        values = [td.text.strip() for td in tr.find_all('td') if td.text.strip()]
        values.insert(0, ses_id)
        data_asistencias.append(values)

#%%%
# Búsqueda de todas las votaciones por sesión
url_vota = 'https://sala.cconstituyente.cl/doGet.asmx/getVotacionesPorSesion'

votaciones = []
for ses_id in sesiones_id:
    busqueda = requests.get(url_vota, params=ses_params(ses_id))
    vot_extend = json.loads(busqueda.text)['data']
    vot_extend = [dict(item, **{'IdSesion':ses_id}) for item in vot_extend]
    votaciones.extend(vot_extend)

votaciones_id = []
for votacion in votaciones:
    votaciones_id.append(votacion['Id'])
    
#%%%
# Búsqueda de detalle de las votaciones
url_detail = 'https://sala.cconstituyente.cl/views/VotacionDetalle.aspx'

def vot_params(v_id):
    return {'prmVotacionId': v_id}

detalle_vota = []
orden_resultado = ['Favor', 'Contra', 'Abstención', 'Dispensados']

for vot_id in votaciones_id:
    busqueda = requests.get(url_detail, params=vot_params(vot_id))
    tabla_votacion = BeautifulSoup(busqueda.text, 'html.parser').find(class_ ='col-lg-12 votacion-detalle')
    det_vot = tabla_votacion.find_all(class_= 'row')
    
    for num, orden in enumerate(orden_resultado):
        for div in det_vot[num*2 +1 ].find_all('div'):
            values = [vot_id, orden, div.text.strip()]
            detalle_vota.append(values)

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

