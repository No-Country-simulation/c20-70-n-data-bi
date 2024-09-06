import os
import pandas as pd
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import zipfile
from catboost import CatBoostClassifier
import streamlit as st
from sklearn.metrics import accuracy_score, classification_report
import tempfile

def fraud_pct_by_column(data, column, target, fraud_pct_col_name, rank_col_name):
    # Agrupar por columna y obtener la cantidad de ventas y cantidad de fraudes
    group_fraud_by_column = data.groupby(column).agg(
        total_sales=(target, 'count'),
        fraud_sales=(target, 'sum')
    )

    # Calcular el porcentaje de fraude en las ventas para cada valor
    group_fraud_by_column[fraud_pct_col_name] = (group_fraud_by_column['fraud_sales'] / group_fraud_by_column['total_sales']) * 100
    group_fraud_by_column = group_fraud_by_column.reset_index()

    # Rank de los vendedores por porcentaje de fraude
    group_fraud_by_column[rank_col_name] = group_fraud_by_column[fraud_pct_col_name].rank(ascending=False)

    # Unirlo con el df original
    data = data.merge(group_fraud_by_column[[column, fraud_pct_col_name, rank_col_name]], on=column,how='left')

    return data


# Se agruparan las profesiones para disminuir la dimensionalidad
def assign_sector(x):
    group_jobs = {
        "Engineering and Technology": ["engineer", "developer", "programmer", "technician", "architect", "systems", 
                                    "network", "administrator", "data scientist", "cybersecurity", "web developer", 
                                    "analyst", "database", "devops", "maintenance", "manufacturing", "site", 
                                    "structural", "materials", "biomedical", "environmental", "telecommunications"],
        
        "Healthcare and Medicine": ["doctor", "nurse", "therapist", "pharmacist", "health", "surgeon", "dentist", 
                                    "clinician", "physician", "optometrist", "radiologist", "paramedic", "midwife", 
                                    "veterinarian", "psychiatrist", "psychologist", "radiographer", "biochemist", 
                                    "cytogeneticist", "audiologist", "pathologist"],
        
        "Education and Training": ["teacher", "professor", "educator", "trainer", "lecturer", "scientist", "tutor", 
                                "principal", "instructor", "counselor", "academic", "researcher", "dean", 
                                "headmaster", "careers adviser", "museum education officer", "education administrator"],
        
        "Science and Environment": ["scientist", "environmental consultant", "ecologist", "geologist", "hydrologist", 
                                    "conservation officer", "horticulturist", "geophysicist", "soil scientist", 
                                    "agricultural consultant", "agricultural engineer", "oceanographer", 
                                    "fisheries officer"],
        
        "Art, Design, and Media": ["designer", "artist", "animator", "photographer", "film editor", "video editor", 
                                "television producer", "film producer", "radio producer", "curator"],
        
        "Finance": ["analyst", "accountant", "auditor", "banker", "financial", "investment", "controller", "broker", 
                    "consultant", "treasurer", "loan officer", "trader", "actuary", "economist", "portfolio", "credit"],
        
        "Marketing": ["manager", "executive", "specialist", "consultant", "advertising", "public relations", "strategist", 
                    "director", "coordinator", "brand", "SEO", "content", "digital", "market research", "social media", 
                    "copywriter"],
        
        "Manufacturing": ["operator", "mechanic", "assembler", "fabricator", "engineer", "technician", "welder", 
                        "planner", "quality", "machinist", "production", "inspector", "supervisor", "foreman", 
                        "toolmaker", "CNC"],
        
        "Retail": ["cashier", "salesperson", "store", "associate", "manager", "clerk", "shopkeeper", "merchandiser", 
                "assistant", "retail", "customer service", "sales", "inventory", "buyer", "stocker", "checkout"],
        
        "Legal": ["lawyer", "attorney", "paralegal", "judge", "legal", "solicitor", "notary", "clerk", "litigator", 
                "advocate", "barrister", "counsel", "magistrate", "prosecutor", "defense", "compliance"],
        
        "Hospitality": ["chef", "waiter", "bartender", "host", "manager", "receptionist", "housekeeper", "concierge", 
                        "caterer", "cook", "hotel", "tour guide", "event planner", "sous chef", "sommelier", "valet"],
        
        "Construction": ["builder", "carpenter", "electrician", "plumber", "architect", "project manager", "site manager", 
                        "surveyor", "foreman", "bricklayer", "roofer", "civil engineer", "construction", "contractor", 
                        "inspector", "draftsman"]
    }
    for key in group_jobs:
        for role in group_jobs[key]:
            if x.find(role) != -1:
                return key
    return "Other"


def datetime_split(data, datatime_col_name, day_col_name, month_col_name, year_col_name, hour_col_name, weekday_col_name):
    # Transformar la columna a datetime para el procesado
    data[datatime_col_name] = pd.to_datetime(data[datatime_col_name])

    # Dividir el día del mes, mes, año, hora y día de la semana en nuevas columnas
    data[day_col_name] = data[datatime_col_name].dt.day
    data[month_col_name] = data[datatime_col_name].dt.month
    data[year_col_name] = data[datatime_col_name].dt.year
    data[hour_col_name] = data[datatime_col_name].dt.hour
    data[weekday_col_name] = data[datatime_col_name].dt.weekday

    return data

def dob_to_age(data, dob_col_name, age_col_name):
    # Transformar la columna dob de object a datetime
    data[dob_col_name] = pd.to_datetime(data[dob_col_name])

    # Obtener la fecha actual
    actual_date = pd.to_datetime(datetime.now().date())

    # Convertir la fecha de nacimiento a edad [años] (fecha actual - fecha de nacimiento)/días promedio por año
    data[age_col_name] = ((actual_date - data[dob_col_name]).dt.days / 365.25).astype(int)

    return data

# Función para calcular la distancia
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la tierra [km]
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def extract_zip_to_csv(uploaded_file, temp_dir):
    """
    Extrae un archivo zip, busca un archivo CSV dentro y lo convierte a csv.
    """
    zip_path = os.path.join(temp_dir, "temp.zip")

    # Guardar el archivo zip subido en el directorio temporal
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    # Descomprimir el archivo zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Buscar archivos CSV en el directorio temporal
    extracted_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]

    return extracted_files


def catboost_model(features_scaled, target, model):
    predictions = model.predict(features_scaled)                   # Hacer predicciones

    # Mostrar las predicciones
    st.write("Mostrando las primeras 5 predicciones:")
    st.dataframe(pd.DataFrame(predictions, columns=['Predicción']).head())

    # Mostrar el objetivo real
    st.write("Mostrando las primeras 5 reales:")
    st.dataframe(target.head())

    # Evaluar el modelo
    accuracy = accuracy_score(target, predictions)
    report = classification_report(target, predictions)
    return predictions, accuracy, report

def extract_zip_to_model(zip_path, name_model):
    try:
        # Crear un directorio temporal para extraer el archivo
        with tempfile.TemporaryDirectory() as tmpdirname:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Filtrar los archivos y extraer solo el que necesitas
                for file_name in zip_ref.namelist():
                    if file_name.endswith(name_model):
                        zip_ref.extract(file_name, tmpdirname)
                        model_path = os.path.join(tmpdirname, file_name)
                        break
                else:
                    raise FileNotFoundError(f'{name_model} no encontrado en el archivo ZIP.')

            # Cargar el modelo de CatBoost
            model = CatBoostClassifier()
            model.load_model(model_path)
            return model
            
    except Exception as e:
        print(f"Error al extraer o cargar el modelo: {e}")
        return None