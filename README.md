# Predicción de Fraude en Transacciones Financieras

## Colaboradores
Andres G Velasquez: 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/andres946/)
[![Correo Electrónico](https://img.shields.io/badge/Correo%20Electrónico-andresgvelasquez8@gmail.com-red?style=for-the-badge&logo=mail.ru)](mailto:andresgvelasquez8@gmail.com)  

Laura Vasquez: 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/laura-cristina-vasquez-analistadedatos)
[![Correo Electrónico](https://img.shields.io/badge/Correo%20Electrónico-lauravasquez112399@gmail.com-red?style=for-the-badge&logo=mail.ru)](mailto:lauravasquez112399@gmail.com)  

## Descripción
Desarrollar un modelo predictivo para detectar transacciones fraudulentas en una plataforma de pagos electrónicos, utilizando técnicas de aprendizaje automático y análisis de comportamiento.

# Entregables:
- Pagina Web: El **usuario** podra cargar un .zip que contenga el archivo .csv con los datos que necesitan predicción. La pagina predice en tiempo real, carga los datos a la base de datos en PostgreSQL y devuelve feedback en forma de visualizaciones. 
- Base de datos en PostgreSQL: El **usuario** puede realizar consultas SQL al conectarse en la base de datos. 
- Power BI: A partir del Análisis Exploratorio de Datos se responden algunas preguntas a traves de poderosas visualizaciones. 

## Tecnolgías
![Python](https://img.shields.io/badge/-Python-blue?style=for-the-badge&logo=python&logoColor=white&logoWidth=40)
![Pandas](https://img.shields.io/badge/-Pandas-blue?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/-NumPy-blue?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/-Matplotlib-blue?style=for-the-badge&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/-Seaborn-blue?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/-scikit--learn-blue?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-ffc40d?style=flat-square&logo=power-bi&logoColor=white)

## Fuente de datos
El dataset fue descargado de Kaggle con el titulo "Credit Card Transactions Fraud Detection Dataset". Se puede revisar en el siguiente enlace: https://www.kaggle.com/datasets/kartik2112/fraud-detection?select=fraudTrain.csv

### Diccionario de datos

#### Variables características
- `Unique` - Identificador para cada fila  
- `trans_date_trans_time` - Fecha de transaccion  
- `cc_num` - Numero de la tarjeta de credito del cliente  
- `merchant` - Nombre del vendedor  
- `category` - Categoria de venta  
- `amt` - Monto de transacción   
- `first` - Nombre del propietario de la tarjeta de credito  
- `last` - Apellido del propietario de la tarjeta de credito  
- `gender` - Genero del propietario de la tarjeta de credito  
- `street` - Calle del propietario de la tarjeta de credito  
- `city` - Ciudad del propietario de la tarjeta de credito  
- `state` - Estado del propietario de la tarjeta de credito 
- `zip` - Zip de la tarjeta de credito del propietario
- `lat` - Latitud del propietario de la tarjeta de credito  
- `long` - Longitud del propietario de la tarjeta de credito
- `city_pop` - Población de la ciudad del propietario de la tarjeta de credito  
- `job` - Trabajo del propietario de la tarjeta de credito 
- `dob` - Fecha de nacimiento del propietario de la tarjeta de credito 
- `trans_num` - Numero de transacción  
- `unix_time` - UNIX fecha de transacción  
- `merch_lat` - Latitud del vendedor 
- `merch_long` - Longitud del vendedor 

#### Variable objetivo
- `is_fraud` - Indica si la transacción es fraude

## Instalación de dependencias

Para instalar las dependencias necesarias para este proyecto, puedes ejecutar el siguiente comando:

```bash
pip install -r requirements.txt
```
**Nota** Esta versión de Boruta puede arrojar un error al utilizar np.float, np.int y np.bool. Basta con reemplazarlos por
float, int, bool respectivamente en el archivo donde este el error. 
