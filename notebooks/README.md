# Notebooks del Proyecto

Este directorio contiene cuadernos de Jupyter que fueron utilizados principalmente para la exploración de datos y la realización de pruebas relacionadas con la aplicación en Streamlit y la base de datos.

## Contenido:

- `EDA_2_test.ipynb`: Cuaderno de **Análisis Exploratorio de Datos (EDA)** utilizado para explorar las características del conjunto de datos y realizar pruebas preliminares de análisis, visualización, transformación de los datos y entrenamiento de modelos.
- `Analisis_serie_tmp.ipynb`: Este cuaderno fue empleado para explorar series temporales relacionadas con las transacciones y hacer pruebas para posibles modelados que aprovechen el componente temporal de los datos.
- `SQL_Test.ipynb`: Cuaderno de pruebas con **consultas SQL**, utilizado para conectar a la base de datos PostgreSQL y realizar consultas directas sobre los datos cargados. Sirve como base para probar la integración con la aplicación Streamlit.

## Descripción de los análisis:

### `EDA_2_test.ipynb`

1. **Importación de datos**: Carga y revisión del conjunto de datos principal.
2. **Limpieza de datos preliminar**: Identificación de valores nulos y eliminación de duplicados.
3. **Visualización básica**: Gráficos sencillos para comprender las distribuciones y correlaciones entre variables.
4. **Transformación de los datos**: División en entrenamiento y prueba, escalamiento, one hot-encoding.
5. **Prueba de modelos de machine learning**: Regresióon logística, árbol de desición, bosque aleatorio, catboost, LightGBM, XGBoost con optimización de hiperparámetros.

### `Analisis_serie_tmp.ipynb`

1. **Análisis de series temporales**: Evaluación de las transacciones a lo largo del tiempo para detectar patrones temporales en el comportamiento del fraude.
2. **Pruebas con modelos**: Pruebas con algunos modelos predictivos para evaluar la viabilidad de usar series temporales en la predicción de fraude.

### `SQL_Test.ipynb`

1. **Conexión a la base de datos**: Pruebas de conexión con PostgreSQL y consulta directa de las tablas.
2. **Consultas básicas**: Exploración y pruebas de extracción de datos desde la base de datos utilizando SQL.
3. **Validación de datos**: Comparación de los resultados de las consultas con los datos de Streamlit para asegurar la consistencia.

## Uso de los cuadernos

Si deseas ejecutar los cuadernos de Jupyter localmente, asegúrate de tener instaladas las dependencias necesarias listadas en `requirements.txt`. Para abrir los cuadernos, usa el siguiente comando desde la terminal:

```bash
jupyter notebook
```

Una vez abierto Jupyter, navega hasta este directorio y selecciona el cuaderno que deseas ejecutar.

**Notas adicionales:**
- Propósito de los cuadernos: Estos cuadernos fueron utilizados principalmente para pruebas y exploración de datos, y pueden contener código experimental o no optimizado.
- Reproducibilidad: Si planeas ejecutar estos cuadernos, asegúrate de revisar las rutas a los archivos y la configuración de la base de datos, ya que podrían necesitar ajustes locales.
- Los datasets se encuentran en kaggle. 