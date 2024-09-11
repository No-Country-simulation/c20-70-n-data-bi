import streamlit as st

from helpers.sql_utils import append_new_data_to_db, db_conn, check_users_in_db

# Verificar si el acceso ha sido concedido
if not st.session_state.get('access_granted', False):
    st.error("Acceso restringido. Por favor, ingresa el código de acceso en la barra lateral.")
    st.stop()

st.subheader("Creación de tablas relacionales")

# Verificar si la conexión ya está almacenada en session_state
if 'db_engine' not in st.session_state:
    st.session_state.db_engine = db_conn()

# Usar la conexión almacenada
engine = st.session_state.db_engine

df = st.session_state.data

col_table_locations, col_table_merchants, col_table_predictions = st.columns([1, 1.25, 1])

with col_table_locations: 
    # Crear la tabla locations
    locations = df[['city', 'state', 'city_pop']].drop_duplicates()
    # Mostrar las primeras 5 filas
    st.write("Tabla: Ubicaciones [primeras 5 filas]")
    st.dataframe(locations.head())
    
with col_table_merchants:
    # Crear la tabla merchants
    merchants = df[['merchant', 'merch_lat', 'merch_long']].drop_duplicates()
    # Mostrar las primeras 5 filas
    st.write("Tabla: Vendedores [primeras 5 filas]")
    st.dataframe(merchants.head())

with col_table_predictions:
    # Mostrar las primeras 5 filas de predictions
    st.write("Tabla: Predicciones [primeras 5 filas]")
    predictions_df = st.session_state.predicts
    st.dataframe(predictions_df.head())

# Crear la tabla users
users = df[['cc_num', 'zip', 'first', 'last', 'gender', 'street', 'city', 'state', 'job', 'dob']].drop_duplicates()
# Mostrar las primeras 5 filas
st.write("Tabla: Usuarios [primeras 5 filas]")
st.dataframe(users.head())


# Crear la tabla transactions
transactions = df[['trans_date_trans_time', 'cc_num', 'merchant', 'category', 'amt', 'lat', 'long', 'trans_num', 'unix_time', 'is_fraud']].drop_duplicates()
# Mostrar las primeras 5 filas
st.write("Tabla: Transacciones [primeras 5 filas]")
st.dataframe(transactions.head())                        

# Botón para cargar los datos a la base de datos
if st.button("Cargar datos a la base de datos"):
    try:
        users.to_sql('users', engine, if_exists='append', index=False)
        st.success("La tabla de Usuarios ha sido cargada en la Base de datos.")

        merchants.to_sql('merchants', engine, if_exists='append', index=False)
        st.success("La tabla de Vendedores ha sido cargada en la Base de datos.")

        locations.to_sql('locations', engine, if_exists='append', index=False)
        st.success("La tabla de Ubicaciones ha sido cargada en la Base de datos.")

        predictions_df.to_sql('predictions', engine, if_exists='append', index=False)
        st.success("La tabla de Predicciones ha sido cargada en la Base de datos.")

        transactions.to_sql('transactions', engine, if_exists='append', index=False)
        st.success("La tabla de Transacciones ha sido cargada en la Base de datos.")

    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")