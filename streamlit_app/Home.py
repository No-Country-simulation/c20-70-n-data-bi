import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from helpers.utils import config_sidebar

# Ajustar el ancho para toda la pantalla 
st.set_page_config(page_title="Detección de Fraude", layout="wide")

# Configurar la barra lateral
codigo_acceso = config_sidebar()

# Verificación del código de acceso
if codigo_acceso == "1234":
    # Título de la página
    st.title("Detección de Fraude en Transacciones con Tarjetas de Crédito")

    # Obtener los datos de la DB
    n_transactions = 1852394
    n_frauds = 9651
    n_users = 999

    # Carga de datasets con el top 5 de fraudes
    top_5_fraud_merch = pd.read_csv('streamlit_app/data/top_5_fraud_merch.csv')
    top_5_fraud_city = pd.read_csv('streamlit_app/data/top_5_fraud_city.csv')
    top_5_fraud_state = pd.read_csv('streamlit_app/data/top_5_fraud_state.csv')

    # Renombrar columnas
    top_5_fraud_merch.columns = ['Vendedor', 'Fraude [%]', 'Fraudes [#]']
    top_5_fraud_city.columns = ['Ciudad', 'Fraude [%]', 'Fraudes [#]']
    top_5_fraud_state.columns = ['Estado', 'Fraude [%]', 'Fraudes [#]']

    # Crear tres columnas para cada top
    col_metrics, col_top_merch, col_top_city, col_top_state = st.columns([0.9, 2.5, 2, 2])

    # Mostrar dataframes en cada columna
    with col_metrics:
        st.subheader("Métricas")
        st.markdown(f'<p style="font-size:18px;">No. de Transacciones: <span style="color:green;">{n_transactions}💳</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:18px;">No. de Fraudes: <span style="color:red;">{n_frauds}🚨</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:18px;">No. de Usuarios:<br> <span style="color:white;">{n_users}👥</span></p>', unsafe_allow_html=True)

    with col_top_merch:
        st.subheader("Vendedores con Fraude")
        st.dataframe(top_5_fraud_merch.set_index(top_5_fraud_merch.columns[0]))

    with col_top_city:
        st.subheader("Ciudades con Fraude")
        st.dataframe(top_5_fraud_city.set_index(top_5_fraud_city.columns[0]))

    with col_top_state:
        st.subheader("Estados con Fraude")
        st.dataframe(top_5_fraud_state.set_index(top_5_fraud_state.columns[0]))
    
    global_frauds_per_day = pd.read_csv('./streamlit_app/data/global_frauds_per_day.csv', parse_dates=['trans_date_trans_time'], index_col='trans_date_trans_time')

    # Crear una figura de Plotly para la gráfica de línea

    # Leer datos de tmp_series_pred
    tmp_series_pred = pd.read_csv('./streamlit_app/data/tmp_series_pred.csv', parse_dates=['date'], index_col='date')

    # Definir la fecha límite para las predicciones
    end_date = '2020-12-22'

    # Filtrar las predicciones hasta la fecha límite
    tmp_series_pred = tmp_series_pred[tmp_series_pred.index <= end_date]

    # Identificar la fecha de inicio de las predicciones
    start_date_predictions = tmp_series_pred.index.min()

    # Filtrar los datos reales hasta la fecha de inicio de las predicciones
    global_frauds_per_day = global_frauds_per_day[global_frauds_per_day.index <= start_date_predictions]


    # Crear la figura
    fig = go.Figure()

    # Añadir la serie de fraudes originales
    fig.add_trace(go.Scatter(
        x=global_frauds_per_day.index, 
        y=global_frauds_per_day['total_transacciones'], 
        mode='lines', 
        name='Número de Fraudes',  # Nombre para la leyenda
        line=dict(color='blue')    # Color para la serie original
    ))

    # Añadir la serie de predicciones
    fig.add_trace(go.Scatter(
        x=tmp_series_pred.index, 
        y=tmp_series_pred['prediction'],  # Cambia 'prediction' si el nombre de la columna es diferente
        mode='lines', 
        name='Predicciones',  # Nombre para la leyenda
        line=dict(color='red')  # Color para las predicciones
    ))

    # Añadir título y etiquetas a los ejes
    fig.update_layout(
        title="Línea Temporal de Fraudes y Predicciones por Día",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Fraudes",
        template="plotly_white"
    )

    # Configurar el formato de fechas en el eje x
    fig.update_xaxes(
        tickformat="%d-%b-%Y",  # Formato en día-mes-año (ej. 01-Sep-2022)
        ticklabelmode="period"   # Muestra las etiquetas de las fechas en modo período
    )

    # Mostrar la gráfica en Streamlit
    st.plotly_chart(fig)
    del global_frauds_per_day
else:
    st.warning("Acceso restringido. Por favor, ingresa el código de acceso en la barra lateral.")