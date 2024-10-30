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

os.environ['GOOGLE_SERVICE_ACCOUNT'] = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAidHJhbnF1aWwtaGF3ay00Mjk3MTItcjkiLAogICJwcml2YXRlX2tleV9pZCI6ICJjYTIyMmZlMmI1Y2I4YjkwZTdhZTUyYTdkYjI3NzRjZDg2ZTYxZmE4IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdlFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLY3dnZ1NqQWdFQUFvSUJBUURsdVhYc1lMVG0zeGJpXG5FN0Q5eTR6R1R6ZXlmV2xsWnEwTVhhVjRka2ZiSWNYWnZhdWVKUlluY1dRZVNheThFdk1IZ0NlcmN2Y3VDL0xnXG52OEtyY21NTEZtRTc2Qm1URENya1duSEdsUzlsZUJLRGtmWVh3c09PdWd4VmZrSStadDNtc3dud3V2Unlsdld6XG5QSXZPWDJyTm5DV1U0K05PR3NJa0hmeitVaFRGQXZuSkhBc3E2N25zZzU5MEhza09yUU1ZalRTWXpoa0hKdkRUXG5JcVRNa29lZ3FFQVQ4V0FpUzRsSUJPMDQ3YkEwb1VXZUh6UWxOZTJTZVdHMVpkQjNOclpGeCt1b1BVYjREbnJLXG5Hdlh1Q213a3dad2tWb0VEM0h0QnJJYXZMclJENDVNajlPN3kwKy9MbzMwejltcTJROGc0YWhQcUNCazI3RmR4XG5pRnRIOHJHRkFnTUJBQUVDZ2dFQU1VQXVOb1BUTk80ZVIxRG1jTHNManRhYi85SGdYME9BbFRhY2k3TjhHMUJsXG56UlZiYmxmUUpKdXNWY3dBMHYrVENBZ2pPU0E0T3pDSG5VU3ZkVGRjWVp1bU5BUkNPMkx2N1M0dzExelRvUUw1XG5vU2lSWksyMlpHcWh5MUI2M2tzS2h2UGFqVGhmd1JONVVMaUoxckJoUXZ5WG1CQzFnbUM5UDZZSVAvUVVETnA2XG45M0RoNWxLZGZidjNMaENJWEdYR3JQUnROdmszNEZ5OTQ4ME1rZHVwallEQVJmZXdVWEo4VEhSOGczdzZ5VTZLXG5xOXlhd3ZaZzBkSXp6ajJ6REV5WTk1THg1a0hNKzZiRXF6UVJDSTkrV0lRQzcrTkRXeDMycDI3SGEyTitTVDJDXG50bjRKdldCcS9HQ0tDTmRVYUptbVdxM0RKY2RSQVFUMFZLMWFYRjNPM3dLQmdRRDNGc0JVREFrSmllU3RyVWxVXG5vSEJXVFFaTmt0ZDVaeCt5UllhVzNJVTVMKzRzSDdyWWpZdDJzQWJqYjJXL1BVZjRGcmhBaHRXd0E4UHBCLzZOXG5WQkxZWVArb1pMNjQ0ZEtFUi9uTmNyMFg1Nk5QTFE5UEYvcUJodDhBTkFncmtTMVdubDhxYlRJSjZ2bTY2UnVHXG5wTDdoTmVkU1p3TnRtWDV2UjVzT09aaVYzd0tCZ1FEdUFtUnZ2WGFDM1laTnI5aHREOWlKWEs4TURxZlEwVStzXG5YNVpGbnFRTkYyRXRkVDBURWlKK0Y3N29FbGZBNlFwSWU5WW50VmxMSXdjLzRLZjNIVWVjQ3lNUUJDaHp1NFY3XG4zcnpKK3psaFAyWUJuQ0VDdE55VDA4R2ZDZDZMS2FNd01pa0VkUjlLV3dBMGo2NzhPcnRSTlVtcXJtL29lUVIyXG5IMWpPci9OOUd3S0JnQjlsL0xxeGJOU1JlVVc0cDREaGdtVDFGTC8yMFByVVorcTNld3JncXUxQmNmcVpiWnpuXG5IN25OVkpMQ0xTUElIY1VnM2ZrVktVSmN1Q0I4cTVRNkFzc01TSENWbk1iUnEzYXp6c0tVdWdLM3BNRUM4TmNVXG5MUGtZc20zTUx0MmFiVEI4bjRzOHBRY3RuTjVya052alEzNUs0MEpOWk5vZ2p6aUUyT2ROMmwzeEFvR0FNN3lsXG5aSHpFMURHZlRpZlpYZXZCNENvYml2MXNrVUhPbGVPNVlLelpjRmNTc3JUM2I3dlRiNkZ0eURpa2hyU2huWnY5XG5zMmdDWHdqZ1BJeHpObzVRMEtUREhHb3ErTzFjV003VUx2dkRQMVp1c0E3bVJoWldsSFBGZFBMS1EybnJwVUJpXG5GaXYzZjB4RXdTZ3ltM1dRM2xnOUNUTWQ5R1RLQ1h0SzdMTG10TjBDZ1lFQTV5RDFwd01Hd29HbFZ6aVF1dE1yXG4yVnJxOTRuQ1dvUU1NL0k4a1ZncEQyc0M1cXBlWGhiUXl3SWNJZjVNN0dWWWc3VzByTjd1cVZQa2Ntdm5Sb1pHXG5RVWZHY1A0UDd4ZDM1eXJOd09NejFFUTk0TlQ4UjNIL1JxVHhldDdUQ0RtNjc4RWZSamlET2Jra0pzby8xUDFvXG5la3E3SSs5OWpuU3F5TjRWMUNBYlAzND1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJjb21wdGUtc2VydmVpQHRyYW5xdWlsLWhhd2stNDI5NzEyLXI5LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwNzgyMzc0Mzk5MTM5MTk4NDYwMyIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvY29tcHRlLXNlcnZlaSU0MHRyYW5xdWlsLWhhd2stNDI5NzEyLXI5LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9Cg=="  # Pruébalo directamente en el código

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