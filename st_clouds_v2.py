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
        encoded_sa = os.getenv('GOOGLE_SERVICE_ACCOUNT')
        if not encoded_sa:
            raise ValueError("La variable de entorno GOOGLE_SERVICE_ACCOUNT no está configurada")

        sa_json = base64.b64decode(encoded_sa).decode('utf-8')

        sa_dict = json.loads(sa_json)

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
            data = pd.DataFrame(values[1:], columns=values[0])
            
            # Verificar que hay suficientes columnas y seleccionar solo G y H
            if data.shape[1] < 8:
                st.warning("Los datos no contienen suficientes columnas. Verifica el rango y el contenido del spreadsheet.")
                return None
            
            #Seleccionar las columnas G y H (índices 6 y 7) + grup
            data = data.iloc[:, [4, 6, 7]]
            #data = data[['E', 'G', 'H']]
            data.columns = ['Group','Tags', 'Words']  
            return data
    except Exception as e:
        st.error(f"Error al cargar datos de Google Sheets: {str(e)}")
        return None

def create_wordcloud(text, title):
    wordcloud = WordCloud(
        width=800,  
        height=400,  
        background_color="white",
        contour_color='black',
        contour_width=2,
        colormap="RdBu_r",
        stopwords=None,
    ).generate(text)

    plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.figtext(0.5, 0.01, title, ha="center", fontsize=11, color='grey')
    plt.tight_layout()

    return plt

qr_image_path = Path(__file__).parent / "qr.png"

def main():
    st.markdown("<h1 style='text-align: center;'>How is age depicted in Generative AI?</h1>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")

    drive_service, sheets_service = get_google_services()
    spreadsheet_id = "1kkpKzDOkwJ58vgvp0IIAhS-yOSJxId8VJ4Bjxj7MmJk"
    range_name = "Sheet1!A1:H"

    refresh_interval = 600

    col1, spacer, col2 = st.columns([1, 0.2, 1])

    col1.markdown("<h3 style='text-align: center;'>People</h3>", unsafe_allow_html=True)
    col2.markdown("<h3 style='text-align: center;'>Older People</h3>", unsafe_allow_html=True)

    # Contenedores para wordclouds
    neutral_word_plot = col1.empty()
    older_word_plot = col2.empty()

    last_update_text = st.empty()

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: left;'>Participate with the QR below:</p>", unsafe_allow_html=True)

    if qr_image_path.exists():
        st.image(str(qr_image_path), width=100)#use_column_width=True)
    else:
        st.error(f"Error: La imagen '{qr_image_path}' no se encuentra.")

    while True:
        data = load_data_from_sheet(spreadsheet_id, range_name, sheets_service)
        if data is not None:
            older_data = data[data['Group'] == 'older']
            neutral_data = data[data['Group'] == 'neutral']

            # Juntar tags y words para cada grupo
            older_text = " ".join(older_data["Tags"].dropna()) + " " + " ".join(older_data["Words"].dropna())
            neutral_text = " ".join(neutral_data["Tags"].dropna()) + " " + " ".join(neutral_data["Words"].dropna())

           # Estilos CSS para ajustar el espaciado entre los gráficos
            neutral_style = "<div style='margin-left: 20px; margin-right: -20px;'>"
            older_style = "<div style='margin-left: -20px; margin-right: 20px;'>"

            # Actualizar plot para el grupo "neutral"
            with neutral_word_plot:
                neutral_word_plot.pyplot(create_wordcloud(neutral_text, ""))

            # Actualizar plot para el grupo "older"
            with older_word_plot:
                older_word_plot.pyplot(create_wordcloud(older_text, ""))

            #st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.markdown("")
            st.markdown("")
            last_update_text.markdown(f"<h6 style='text-align: center;'>Last update: {current_time}</h6>", unsafe_allow_html=True)

            time.sleep(refresh_interval)
        else:
            st.warning("No se pudo cargar ningún dato. Revisa la conexión.")
            break

if __name__ == "__main__":
    main()
