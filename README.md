# Convencion Constitucional Web Scraping
Web Scraping de la Convención Constitucional en Chile


Los script `ConvencionScrap.py` y `ConvencionScrap_async.py` hacen un web scraping de las sesiones, asistencias y votaciones de la Convención Constitucional de Chile, específicamente de la web: [https://sala.cconstituyente.cl/](url)

La única diferencia entre ambos script es el uso de la librería grequests para que el proceso de requests sea ascincrónico, esto permite que se puedan realizar múltiples requests al mismo tiempo y la descarga de información sea más rápida.

Ambos script en sus últimas líneas exportan cuatro archvios con la infromación recopilada en formato `CSV` y separados por `;`. Los  archvios tienen la siguiente estructura:

| Archivo  | Variables |
| ------------- | ------------- |
| dat_sesiones.csv | IdSesion ,  Numero ,  Nombre ,  DiscucionPresupuesto ,  FechaTexto ,  Tipo , FechaInicio ,  FechaTermino ,  Estado ,  BoletinId ,  SintesisId , ActaId |
| dat_asistencias.csv  | IdSesion ,  Convencional ,  HoraIngreso ,  Asistencia ,  Observaciones  |
| dat_votaciones.csv  | IdVotacion ,  Descripcion ,  Materia ,  Articulo ,  Tramite ,  Fecha , Sesion ,  TotalSI ,  TotalNO ,  TotalAbstencion ,  TotalDispensado , Resultado ,  Votos ,  IdSesion  |
| dat_votaciones_detalle.csv  | IdVotacion ,  Voto ,  Nombre  |

La variable `IdSesion` identifica a cada sesión alojada en la web, mientras que `IdVotacion` identifica a cada votación.

Estos códigos se comparten con motivos académicos, para que el usuario tenga más herramientas para obtener información de la Convención Constitucional.
Con esta información se podría estudiar cómo votan los distintos conglomerados de la convención.

## Pequeño análisis de datos
A modo de motivación, presento un par de gráficos realizados con los datos disponibles.

IMAGEN RETRASO

IMAGEN ASISTENCIA REMOTA


