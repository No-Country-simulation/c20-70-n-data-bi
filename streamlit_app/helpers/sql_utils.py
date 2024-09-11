from typing import List
import os
from sqlalchemy import create_engine, inspect, text
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

    # Inspeccionar si la tabla existe
    inspector = inspect(engine)

    # Calcular el tamaño del lote basado en el porcentaje
    batch_size = int(len(data) * batch_percentage)

    if batch_size == 0:
        st.warning("El tamaño del lote es 0. Aumenta el porcentaje o el tamaño de los datos.")
        return

    # Verificar si la tabla existe
    if inspector.has_table(table_name):
        query = f'SELECT {", ".join(keys)} FROM {table_name}'

        st.info("Iniciando procesamiento en lotes...")

        # Procesar lotes del DataFrame y compararlos con lotes desde la base de datos
        for start in range(0, len(data), batch_size):
            batch = data.iloc[start:start + batch_size]  # Obtener lote actual de la DataFrame

            # Inicializar un DataFrame vacío para almacenar los nuevos usuarios de este lote
            new_users_batch = pd.DataFrame()

            # Leer y procesar lotes de la base de datos para comparar con los datos actuales
            for chunk in pd.read_sql(query, engine, chunksize=batch_size):
                # Convertir las claves existentes en el lote de la base de datos en un set de tuplas
                existing_keys = set(chunk.apply(lambda row: tuple(row), axis=1))

                # Filtrar los datos del lote actual que no estén en las claves existentes
                mask = batch[keys].apply(lambda row: tuple(row) not in existing_keys, axis=1)
                batch_new_data = batch[mask]

                # Acumular los nuevos datos de este lote
                if not batch_new_data.empty:
                    new_users_batch = pd.concat([new_users_batch, batch_new_data])

                # Liberar memoria del chunk
                del chunk

            # Si hay nuevos datos en este lote, insertarlos en la base de datos
            if not new_users_batch.empty:
                st.info(f"Insertando nuevos datos del lote {start // batch_size + 1}...")
                new_users_batch.to_sql(table_name, engine, if_exists='append', index=index)

            # Liberar memoria del lote procesado
            del new_users_batch

        st.success("Todos los datos nuevos han sido insertados correctamente.")
    else:
        # Si la tabla no existe, crearla
        st.info("Creando nueva tabla en la base de datos e insertando datos.")
        data.to_sql(table_name, engine, index=index, chunksize=batch_size)
        st.success("Datos insertados correctamente.")

def check_users_in_db(df: pd.DataFrame, user_column: str, table_name: str, engine) -> pd.DataFrame:
    """
    Verifica si los usuarios en el DataFrame están en la base de datos.

    Args:
        df (pd.DataFrame): DataFrame que contiene los usuarios a verificar.
        user_column (str): Nombre de la columna en el DataFrame que contiene los identificadores de usuario.
        engine: Conexión al motor de la base de datos.

    Returns:
        pd.DataFrame: DataFrame con los usuarios que existen en la base de datos.
    """
    user_ids = df[user_column].tolist()

    # Dividir la lista de IDs en bloques más pequeños para evitar problemas de longitud de consulta
    chunks = [user_ids[i:i + 1000] for i in range(0, len(user_ids), 1000)]

    # Inicializar un DataFrame para almacenar los usuarios existentes
    existing_users = pd.DataFrame()

    # Ejecutar consultas en bloques
    with engine.connect() as connection:
        for chunk in chunks:
            query = text(f"""
            SELECT {user_column}
            FROM {table_name}
            WHERE {user_column} IN :ids
            """)
            result = connection.execute(query, {"ids": tuple(chunk)})
            existing_users_chunk = pd.DataFrame(result.fetchall(), columns=[user_column])
            existing_users = pd.concat([existing_users, existing_users_chunk])

    return existing_users