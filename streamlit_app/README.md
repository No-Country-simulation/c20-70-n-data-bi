# Aplicación Streamlit

Esta carpeta contiene la aplicación Streamlit para la detección de fraude en transacciones financieras. La aplicación permite al usuario cargar datos, realizar predicciones, y visualizar resultados en una interfaz web interactiva. Además si el usuario lo requiere puede cargar los datos en PostgreSQL.

## Estructura del Directorio

- `assets/`: Contiene recursos estáticos utilizados en la aplicación.
  - `logo.png`: Logo de la aplicación que se muestra en la interfaz.

- `data/`: Contiene datos preliminares y resultados intermedios.
  - `group_fraud_by_city.csv`, `group_fraud_by_merch.csv`, `group_fraud_by_state.csv`, `top_5_fraud_city.csv`, `top_5_fraud_merch.csv`, `top_5_fraud_state.csv`, `global_frauds_per_day.csv`, `job_freq.csv`: Archivos CSV con datos agrupados y analizados para visualizaciones y pruebas.

- `helpers/`: Contiene funciones de ayuda que se utilizan en diferentes partes de la aplicación.
  - `__init__.py`: Inicializador del módulo.
  - `preprocessing.py`: Funciones para el procesamiento y limpieza de datos.
  - `sql_utils.py`: Funciones para interactuar con la base de datos SQL.
  - `utils.py`: Funciones auxiliares generales.

- `models/`: Contiene los modelos y transformadores usados en la aplicación.
  - `catboost_bestmodel.cbm`: El mejor modelo entrenado con CatBoost.
  - `scaler.pkl`: Escalador para normalizar los datos.
  - `onehotencoder.pkl`: Codificador para variables categóricas.

- `pages/`: Contiene las páginas de la aplicación en Streamlit.
  - `1 Crea tus predicciones.py`: Página para crear y visualizar predicciones de fraude.
  - `2 Carga a la Base de Datos.py`: Página para cargar datos a la base de datos y ver el estado de las cargas.

- `Home.py`: Archivo principal de la aplicación Streamlit. Contiene el login, visualizaciones y navegación a las diferentes páginas de la aplicación.

- `requirements.txt`: Archivo que lista las dependencias necesarias para ejecutar la aplicación Streamlit.

## Instalación y Ejecución

Para instalar las dependencias necesarias para la aplicación, ejecuta el siguiente comando en la terminal:

```bash
pip install -r streamlit_app/requirements.txt
```
Para iniciar la aplicación Streamlit, navega a esta carpeta y ejecuta el siguiente comando:

```bash
streamlit run streamlit_app/Home.py
```
Esto abrirá la aplicación en tu navegador predeterminado, donde podrás interactuar con la interfaz y cargar datos para hacer predicciones de fraude.

## Notas
- Configuración: Asegúrate de tener todas las dependencias instaladas y de que los archivos de datos necesarios están en sus respectivas carpetas.
- Uso de modelos: Los modelos y transformadores deben estar en la carpeta models para que la aplicación pueda cargarlos correctamente.