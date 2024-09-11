import streamlit as st

from helpers.sql_utils import append_new_data_to_db, db_conn

st.subheader("Creación de tablas relacionales")

# Verificar si la conexión ya está almacenada en session_state
if 'db_engine' not in st.session_state:
    st.session_state.db_engine = db_conn()

# Usar la conexión almacenada
engine = st.session_state.db_engine

df = st.session_state.data
# Crear la tabla users
users = df[['cc_num', 'zip', 'first', 'last', 'gender', 'street', 'city', 'state', 'job', 'dob']].drop_duplicates()
# Mostrar las primeras 5 filas
st.write("Tabla: Usuarios [primeras 5 filas]")
st.dataframe(users.head())
# Cargar la tabla a la DB


# Crear la tabla transactions
transactions = df[['trans_date_trans_time', 'cc_num', 'merchant', 'category', 'amt', 'lat', 'long', 'trans_num', 'unix_time', 'is_fraud']].drop_duplicates()
# Mostrar las primeras 5 filas
st.write("Tabla: Transacciones [primeras 5 filas]")
st.dataframe(transactions.head())                        
# Cargar la tabla a la DB


col_table_locations, col_table_merchants, col_table_predictions = st.columns([1, 1.25, 1])

with col_table_locations: 
    # Crear la tabla locations
    locations = df[['city', 'state', 'city_pop']].drop_duplicates()
    # Mostrar las primeras 5 filas
    st.write("Tabla: Ubicaciones [primeras 5 filas]")
    st.dataframe(locations.head())
    # Cargar la tabla a la DB
    

with col_table_merchants:
    # Crear la tabla merchants
    merchants = df[['merchant', 'merch_lat', 'merch_long']].drop_duplicates()
    # Mostrar las primeras 5 filas
    st.write("Tabla: Vendedores [primeras 5 filas]")
    st.dataframe(merchants.head())
    # Cargar la tabla a la DB


with col_table_predictions:
    # Mostrar las primeras 5 filas de predictions
    st.write("Tabla: Predicciones [primeras 5 filas]")
    predictions_df = st.session_state.predicts
    st.dataframe(predictions_df.head())
    # Cargar la tabla a la DB

    predictions_df.to_sql('predictions', engine, if_exists='replace')

# Botón para cargar los datos a la base de datos
if st.button("Cargar datos a la base de datos"):
    try:
        append_new_data_to_db(['cc_num'], 'users', users, engine)
        append_new_data_to_db(['trans_num'], 'transactions', transactions, engine)
        append_new_data_to_db(['city', 'state'], 'locations', locations, engine)
        append_new_data_to_db(['merchant'], 'merchants', merchants, engine)
        append_new_data_to_db(['trans_num'], 'predictions', predictions_df.reset_index(), engine)
        st.success("Las tablas han sido cargadas en la Base de datos.")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")