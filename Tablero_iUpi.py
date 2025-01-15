import streamlit as st
import pandas as pd
from datetime import timedelta, datetime

# Configuración de la página
st.set_page_config(page_title="Dashboard Financiero", layout="wide")

# Función para cargar datos
@st.cache_data
def load_data():
    data = pd.read_csv("Data_finanzas_personales.csv")   # Conectar archivo de datos
    data['fecha'] = pd.to_datetime(data['fecha'])
    return data

# Función para agregar métricas agregadas por frecuencia
def aggregate_data(df, freq):
    return df.resample(freq, on='fecha').agg({
        'ingresosPesos': 'sum',
        'ingresosDolares': 'sum',
        'gastosPesos': 'sum',
        'gastosDolares': 'sum',
        'saldoPesos': 'last',
        'saldoDolares': 'last'
    })

def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

# Cargar datos
df = load_data()

# Opciones de configuración del usuario
st.sidebar.title("Configuración")
max_date = df['fecha'].max().date()
default_start_date = max_date - timedelta(days=365)  # Un año por defecto
start_date = st.sidebar.date_input("Fecha de inicio", default_start_date, min_value=df['fecha'].min().date(), max_value=max_date)
end_date = st.sidebar.date_input("Fecha de fin", max_date, min_value=df['fecha'].min().date(), max_value=max_date)
time_frame = st.sidebar.selectbox("Selecciona un rango temporal", ("Diario", "Semanal", "Mensual"))

# Preparar datos basados en la selección
if time_frame == "Diario":
    df_display = df.set_index('fecha')
elif time_frame == "Semanal":
    df_display = aggregate_data(df, 'W-MON')
elif time_frame == "Mensual":
    df_display = aggregate_data(df, 'M')

# Filtrar datos por rango de fechas
mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
df_filtered = df_display.loc[mask]

# Mostrar métricas clave
st.title("Dashboard Financiero")
st.subheader("Estadísticas Generales")

metrics = [
    ("Saldo en Pesos", "saldoPesos", "#29b5e8"),
    ("Saldo en Dólares", "saldoDolares", "#FF9F36"),
    ("Ingresos en Pesos", "ingresosPesos", "#D45B90"),
    ("Ingresos en Dólares", "ingresosDolares", "#D45B90"),
    ("Gastos en Pesos", "gastosPesos", "#7D44CF"),
    ("Gastos en Dólares", "gastosDolares", "#7D44CF"),
]

cols = st.columns(3)
for col, (title, column, color) in zip(cols * 2, metrics):  # Duplicar para incluir todas las métricas
    total_value = df_filtered[column].sum() if column.startswith("ingresos") or column.startswith("gastos") else df_filtered[column].iloc[-1]
    delta, delta_percent = calculate_delta(df_filtered, column)
    col.metric(label=title, value=f"${total_value:,.2f}", delta=f"{delta:+,.2f} ({delta_percent:+.2f}%)")

# Visualizaciones
st.subheader("Visualizaciones")
st.line_chart(df_filtered[['saldoPesos', 'saldoDolares']])
st.bar_chart(df_filtered[['ingresosPesos', 'gastosPesos', 'ingresosDolares', 'gastosDolares']])

# Mostrar DataFrame filtrado
with st.expander("Ver detalles de datos"):
    st.dataframe(df_filtered)
