import streamlit as st
from streamlit_navigation_bar import st_navbar
from streamlit_carousel import carousel
import streamlit.components.v1 as components

import io
import os
import re
import json
import uuid
import base64
import numpy as np
import random
import time
import pandas as pd
from PIL import Image
from datetime import datetime

from wordcloud import WordCloud
import matplotlib.pyplot as plt

from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, HttpRequest
from googleapiclient.errors import HttpError

st.set_page_config(
    page_title="WordClouds",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed")

def get_google_services():
    try:
        # Obtener la cadena codificada de la variable de entorno
        encoded_sa = os.getenv('GOOGLE_SERVICE_ACCOUNT')
        if not encoded_sa:
            raise ValueError("La variable de entorno GOOGLE_SERVICE_ACCOUNT no está configurada")

        # Decodificar la cadena
        sa_json = base64.b64decode(encoded_sa).decode('utf-8')

        # Crear un diccionario a partir de la cadena JSON
        sa_dict = json.loads(sa_json)

        # Crear las credenciales
        credentials = service_account.Credentials.from_service_account_info(
            sa_dict,
            scopes=[
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
        )

        drive_service = build('drive', 'v3', credentials=credentials)
        sheets_service = build('sheets', 'v4', credentials=credentials)

        return drive_service, sheets_service
    except Exception as e:
        st.error(f"Error al obtener los servicios de Google: {str(e)}")
        return None, None

def load_data_from_sheet(spreadsheet_id, range_name, sheets_service):
    try:
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            st.warning("No se encontraron datos en la hoja de cálculo.")
            return None
        else:
            # Convertir los datos en un DataFrame
            data = pd.DataFrame(values[1:], columns=values[0])
            
            # Verificar que hay suficientes columnas y seleccionar solo G y H
            if data.shape[1] < 8:
                st.warning("Los datos no contienen suficientes columnas. Verifica el rango y el contenido del spreadsheet.")
                return None
            
            # Seleccionar las columnas G y H (índices 6 y 7)
            data = data.iloc[:, [5, 7, 8]]
            data.columns = ['Group','Tags', 'Words']  # Renombrar columnas
            return data
    except Exception as e:
        st.error(f"Error al cargar datos de Google Sheets: {str(e)}")
        return None

# def create_wordcloud(text):
#     # wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
#     wordcloud = WordCloud(
#     width=800,
#     height=400,
#     background_color="white",
#     contour_color='black',
#     colormap="magma",
#     stopwords=None,  
#     ).generate(text)

#     fig, ax = plt.subplots()
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis('off')

#     plt.figtext(0.5, 0.02, f"Wordcloud - ", ha="center", fontsize=11, color='grey')

#     return fig

def create_wordcloud(text, title):
    wordcloud = WordCloud(
    width=800,
    height=400,
    background_color="white",
    contour_color='black',
    contour_width = 2,
    colormap="RdBu_r",
    stopwords=None,  
    ).generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.figtext(0.5, 0.01, title, ha="center", fontsize=11, color='grey')  # Actualizado para incluir el título
    plt.tight_layout()
    
    return plt

def main():
    st.markdown("<h1 style='text-align: center;'>How is age depicted in Generative AI?</h1>", unsafe_allow_html=True)
    st.markdown("")
    #st.markdown("<h5 style='text-align: center;'>text text text</h5>", unsafe_allow_html=True)

    # Conectar a Google Drive y Sheets
    drive_service, sheets_service = get_google_services()
    spreadsheet_id = "1kkpKzDOkwJ58vgvp0IIAhS-yOSJxId8VJ4Bjxj7MmJk"
    range_name = "Sheet1!A1:I"  # Ajusta el rango según tu hoja de cálculo

    # Configurar el tiempo de actualización
    #refresh_interval = st.slider("Intervalo de actualización (segundos)", 10, 300, 60)
    refresh_interval = 60

    # Crear contenedores vacíos para cada grupo y cada tipo de gráfico
    col1, col2 = st.columns(2)

    # Contenedores para el grupo "older"
    older_tag_plot = col1.empty()
    older_word_plot = col1.empty()

    # Contenedores para el grupo "neutral"
    neutral_tag_plot = col2.empty()
    neutral_word_plot = col2.empty()

    last_update_text = st.empty()  # Contenedor para la última actualización

    while True:
        # Cargar los datos
        data = load_data_from_sheet(spreadsheet_id, range_name, sheets_service)
        if data is not None:
            # Filtrar los datos para los grupos
            older_data = data[data['Group'] == 'older']
            neutral_data = data[data['Group'] == 'neutral']

            # Crear texto para los wordclouds
            older_tags = " ".join(older_data["Tags"].dropna())
            older_words = " ".join(older_data["Words"].dropna())
            neutral_tags = " ".join(neutral_data["Tags"].dropna())
            neutral_words = " ".join(neutral_data["Words"].dropna())

            # Actualizar plots para el grupo "older"
            with older_tag_plot:
                older_tag_plot.pyplot(create_wordcloud(older_tags, "Tags - Older person"))  # Título actualizado
            with older_word_plot:
                older_word_plot.pyplot(create_wordcloud(older_words, "Words - Older person)"))  # Título actualizado

            # Actualizar plots para el grupo "neutral"
            with neutral_tag_plot:
                neutral_tag_plot.pyplot(create_wordcloud(neutral_tags, "Tags - Person"))  # Título actualizado
            with neutral_word_plot:
                neutral_word_plot.pyplot(create_wordcloud(neutral_words, "Tags - Person"))  # Título actualizado

            # Actualizar el texto de la última actualización
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_update_text.markdown(f"<h4 style='text-align: center;'>Last update: {current_time}</h4>", unsafe_allow_html=True)

            # Esperar el tiempo de actualización
            time.sleep(refresh_interval)
        else:
            st.warning("No se pudo cargar ningún dato. Revisa la conexión.")
            break

if __name__ == "__main__":
    main()
