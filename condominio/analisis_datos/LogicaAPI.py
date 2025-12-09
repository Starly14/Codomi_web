import requests
from datetime import datetime, timedelta
from decimal import Decimal

API_URL = "https://web-production-77488.up.railway.app"

def consultar_todas_las_tasas():
    try:
        response = requests.get(f"{API_URL}/tasa/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al consultar todas las tasas: {e}")
        return None

def consultar_tasa_por_fecha(fecha):
    if not fecha:
        raise ValueError("La fecha es requerida.")
    try:
        response = requests.get(f"{API_URL}/tasa/{fecha}")
        response.raise_for_status()
        data = response.json()
        return data.get("tasa")
    except requests.RequestException as e:
        print(f"Error al consultar la tasa por fecha: {e}")
        return None

def subir_nueva_tasa(fecha, tasa):
    if not fecha or tasa is None:
        raise ValueError("Fecha y tasa son requeridas.")
    try:
        payload = {"fecha": fecha, "tasa": float(tasa)}
        response = requests.post(f"{API_URL}/tasa/", json=payload)
        response.raise_for_status()
        return response.json().get("mensaje", "Tasa subida con éxito.")
    except requests.RequestException as e:
        print(f"Error al subir la nueva tasa: {e}")
        return None

def obtener_ultima_tasa():
    try:
        response = requests.get(f"{API_URL}/tasa/ultima/")
        response.raise_for_status()
        data = response.json()
        return data.get("tasa")
    except requests.RequestException as e:
        print(f"Error al obtener la última tasa: {e}")
        return None

def consultar_rango_tasas(fecha_inicio, fecha_fin):
    if not fecha_inicio or not fecha_fin:
        raise ValueError("Ambas fechas son requeridas.")
    try:
        response = requests.get(f"{API_URL}/tasa/rango/", params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al consultar el rango de tasas: {e}")
        return None

def es_bisiesto(anio):
    return anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)

def promedio_tasa_mes(anio, mes):
    
    # Obtener el primer y último día del mes
    fecha_inicio = datetime(anio, mes, 1)
    if mes == 12:
        fecha_fin = datetime(anio + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = datetime(anio, mes + 1, 1) - timedelta(days=1)

    # Verificar si el mes de febrero es bisiesto
    if mes == 2 and es_bisiesto(anio):
        dias_del_mes = 29
    else:
        dias_del_mes = (fecha_fin - fecha_inicio).days + 1

    # Consultar las tasas para el rango de fechas
    tasas = consultar_rango_tasas(fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
    if not tasas:
        print("No se pudieron obtener las tasas para el mes seleccionado.")
        return None

    # Calcular el promedio de tasas
    total_tasa = sum(tasa['tasa'] for tasa in tasas)
    promedio =  round ((total_tasa / len(tasas)), 2) if tasas else None
    print(promedio.__class__)
    promedio = round(Decimal(promedio), 2)
    return promedio

def comprobarPromedio():
    valores = [7.8922, 7.9078, 7.9644, 7.9447, 7.9816, 7.9879, 8.0029, 7.9835, 7.9763, 8.004, 8.0294, 8.0277, 8.0508, 8.0275, 8.0496, 8.0959, 8.114, 8.118, 8.1018, 8.1419, 8.1475, 8.1837]
    suma = sum(valores)
    conteo = len(valores)
    promedio = round((suma / conteo), 4)
    print(f"Suma: {suma}, Conteo: {conteo}, Promedio: {promedio}")	

# print(consultar_rango_tasas("2023-03-04", "2023-03-31"))
# comprobarPromedio()