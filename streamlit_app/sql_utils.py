from typing import List
import os
from sqlalchemy import create_engine
import pandas as pd

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
    index: bool = False
) -> None:
    """
    Agrega nuevos datos a la base de datos si no existen.

    Args:
        primary_key (str): Columna clave primaria de la tabla.
        table_name (str): Nombre de la tabla en la base de datos.
        data (pd.DataFrame): DataFrame que contiene los datos a agregar.
        engine: Conexión al motor de la base de datos.
        index (bool, optional): Si se debe escribir el índice. Default es False.
    """
    # Leer la tabla existente en la base de datos
    query = f'SELECT {", ".join(keys)} FROM {table_name}'
    existing_table = pd.read_sql(query, engine)

    # Calcular los usuarios que no existen en la base de datos
    new_users = data[~data[keys].isin(existing_table[keys])]

    # Añadir los nuevos usuarios a la base de datos
    new_users.to_sql(table_name, engine, if_exists='append', index=index)