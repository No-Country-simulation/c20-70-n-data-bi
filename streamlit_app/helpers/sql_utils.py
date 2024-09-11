from typing import List
import os
from sqlalchemy import create_engine, inspect
import pandas as pd
import streamlit as st

def db_conn() -> object:
    """
    Crea y retorna una conexión a una base de datos PostgreSQL utilizando las credenciales almacenadas en las variables de entorno.

    Retorna:
    - engine: Un objeto de SQLAlchemy Engine que representa la conexión a la base de datos.

    Comportamiento:
    1. Obtiene las variables de entorno necesarias para la conexión a la base de datos.
    2. Construye una URL de conexión usando estas variables.
    3. Crea y retorna un objeto de SQLAlchemy Engine para conectar con la base de datos PostgreSQL.
    """
    # Obtener las variables de entorno
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    
    # Verificar que todas las variables de entorno están presentes
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Faltan variables de entorno necesarias para la conexión a la base de datos.")
    
    # Crear la URL de conexión
    connection_url = (
        f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )

    # Crear y retornar el engine de SQLAlchemy
    engine = create_engine(connection_url)

    return engine

def append_new_data_to_db(
    keys: List[str], 
    table_name: str, 
    data: pd.DataFrame, 
    engine, 
    index: bool = False, 
    batch_percentage: float = 0.1  # Procesar en lotes de 10% del total por defecto
) -> None:
    """
    Agrega nuevos datos a la base de datos en lotes si no existen, basado en un porcentaje del tamaño de los datos.

    Args:
        keys (List[str]): Lista de nombres de columnas que se utilizan como claves primarias para la identificación de duplicados.
        table_name (str): Nombre de la tabla en la base de datos.
        data (pd.DataFrame): DataFrame que contiene los datos a agregar.
        engine: Conexión al motor de la base de datos.
        index (bool, optional): Si se debe escribir el índice. Default es False.
        batch_percentage (float, optional): Porcentaje de filas a procesar en cada lote. Default es 0.1 (10%).
    """
    # Verificar que el porcentaje es válido
    if not 0 < batch_percentage <= 1:
        raise ValueError("El porcentaje debe estar entre 0 y 1.")

    # Permite leer si existe una tabla
    inspector = inspect(engine)

    # Calcular el tamaño del lote basado en el porcentaje
    batch_size = int(len(data) * batch_percentage)

    if batch_size == 0:
        st.warning("El tamaño del lote es 0. Aumenta el porcentaje o el tamaño de los datos.")
        return

    # Si la tabla existe, añade los datos
    if inspector.has_table(table_name):
        query = f'SELECT {", ".join(keys)} FROM {table_name}'

        existing_keys = set()
        for chunk in pd.read_sql(query, engine, chunksize=batch_size):
            existing_keys.update(set(chunk.apply(lambda row: tuple(row), axis=1)))

        # Procesar los nuevos datos en lotes
        for start in range(0, len(data), batch_size):
            batch = data.iloc[start:start + batch_size]
            new_data_keys = set(batch[keys].apply(lambda row: tuple(row), axis=1))
            
            # Filtrar los nuevos usuarios que no están en las claves existentes
            new_users = batch[batch[keys].apply(lambda row: tuple(row) not in existing_keys, axis=1)]

            if not new_users.empty:
                # Insertar los datos nuevos en la base de datos
                new_users.to_sql(table_name, engine, if_exists='append', index=index)
    else:
        # Si no existe, crea la tabla
        data.to_sql(table_name, engine, index=index, chunksize=batch_size)
