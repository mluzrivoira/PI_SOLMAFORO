from django.shortcuts import render, HttpResponse
from .models import Location, Medicion #agregue esto
import folium
from django.http import JsonResponse
import json
from folium.plugins import BeautifyIcon 
from collections import defaultdict
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Max, Q

# Create your views here.
def home(request): 

    return render(request, "proyectowebapp/home.html")

def indiceuv(request):
    # Traer TODAS las mediciones, ordenadas de la más nueva a la más vieja
    # Obtener la última fecha de medición para cada ubicación
    ultimas_fechas = Medicion.objects.values('ubicacion_id').annotate(ultima_fecha=Max('fecha_hora'))

# Luego traemos las mediciones correspondientes a esas fechas

    filtros = Q()
    for dato in ultimas_fechas:
        filtros |= Q(ubicacion_id=dato['ubicacion_id'], fecha_hora=dato['ultima_fecha'])

    mediciones = Medicion.objects.filter(filtros)


    # Creamos el mapa
    initialmap = folium.Map(location=[-32.03855, -63.70726], zoom_start=6)


    # Colores según OMS
    colores_uv = {
        "Verde": "#00cc00",
        "Amarillo": "#ffcc00",
        "Naranja": "#ff9900",
        "Rojo": "#ff3300",
        "Violeta": "#9900cc"
    }


    for medicion in mediciones:
        coordinates = [medicion.latitud, medicion.longitud]


        popup_text = (
            f"ID {medicion.ubicacion_id}<br>"
            f"<strong>{medicion.ubicacion}</strong><br>"
            f"Temperatura: {medicion.temperatura} °C"
        )


        # Obtener color real desde el diccionario
        color_uv_hex = colores_uv.get(medicion.color_uv, "gray")


        # Crear ícono bonito con BeautifyIcon
        icono = BeautifyIcon(
            icon_shape='marker',
            number=f"{medicion.uv:.1f}",  # Muestra el valor UV dentro del ícono
            border_color=color_uv_hex,
            background_color=color_uv_hex,
            text_color='white'
        )


        # Agregar marcador al mapa
        folium.Marker(
            location=coordinates,
            popup=popup_text,
            icon=icono
        ).add_to(initialmap)


    context = {
        'mapa': initialmap._repr_html_(),
        'locations': mediciones
    }


    return render(request, 'proyectowebapp/indiceuv.html', context)


def importancia(request):
    
    return render(request, "proyectowebapp/importancia.html")


def graficos(request):
    mediciones = Medicion.objects.all().order_by('-fecha_hora')[:20]  # Mostrar las últimas 20 mediciones
    datos_json = json.dumps([
        {
            "ubicacion_id": m.ubicacion_id,
            "fecha_hora": m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            "ubicacion": m.ubicacion,
            "latitud": m.latitud,
            "longitud": m.longitud,
            "temperatura": m.temperatura,
            "uv": m.uv,
            "color_uv": m.color_uv,
            "color_temperatura": m.color_temperatura
        } for m in mediciones
    ])

    return render(request, 'proyectowebapp/graficos.html', {
        'mediciones': mediciones,
        'datos_json': datos_json
    })
