import requests

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