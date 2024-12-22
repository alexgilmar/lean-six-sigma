import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

class HojaVerificacion:
    def __init__(self):
        # Inicialización de variables de estado
        if 'hoja_verificacion' not in st.session_state:
            st.session_state.hoja_verificacion = None
        if 'datos_hoja' not in st.session_state:
            st.session_state.datos_hoja = None

    def crear_hoja_verificacion(self):
        """
        Crear una nueva hoja de verificación con configuración personalizada
        """
        st.subheader("🛠 Crear Hoja de Verificación")
        
        # Tipos de hojas de verificación
        tipos_hoja = [
            "Conteo de Defectos",
            "Registro de Eventos",
            "Control de Proceso",
            "Análisis de Frecuencia"
        ]
        
        # Selección de tipo de hoja
        tipo_hoja = st.selectbox("Seleccione el Tipo de Hoja", tipos_hoja)
        
        # Configuración de campos
        num_campos = st.number_input("Número de Campos", min_value=1, max_value=10, value=3)
        
        campos = []
        for i in range(num_campos):
            col1, col2 = st.columns(2)
            with col1:
                nombre_campo = st.text_input(f"Nombre del Campo {i+1}")
            with col2:
                tipo_campo = st.selectbox(f"Tipo de Dato Campo {i+1}", 
                                          ["Texto", "Numérico", "Categoría", "Fecha"])
            
            campos.append({
                "nombre": nombre_campo,
                "tipo": tipo_campo
            })
        
        # Botón para crear hoja
        if st.button("Crear Hoja de Verificación"):
            st.session_state.hoja_verificacion = {
                "tipo": tipo_hoja,
                "campos": campos
            }
            st.success("Hoja de Verificación creada exitosamente")

    def ingresar_datos(self):
        """
        Interfaz para ingresar datos en la hoja de verificación
        """
        if st.session_state.hoja_verificacion is None:
            st.warning("Primero debe crear una Hoja de Verificación")
            return

        st.subheader("📝 Ingresar Datos")
        
        # Preparar estructura de datos
        datos = {}
        for campo in st.session_state.hoja_verificacion['campos']:
            if campo['tipo'] == 'Texto':
                datos[campo['nombre']] = st.text_input(campo['nombre'])
            elif campo['tipo'] == 'Numérico':
                datos[campo['nombre']] = st.number_input(campo['nombre'])
            elif campo['tipo'] == 'Categoría':
                opciones = st.text_input(f"Opciones para {campo['nombre']} (separadas por coma)")
                datos[campo['nombre']] = st.selectbox(campo['nombre'], opciones.split(','))
            elif campo['tipo'] == 'Fecha':
                datos[campo['nombre']] = st.date_input(campo['nombre'])
        
        # Botón para guardar datos
        if st.button("Guardar Datos"):
            if st.session_state.datos_hoja is None:
                st.session_state.datos_hoja = pd.DataFrame(columns=[campo['nombre'] for campo in st.session_state.hoja_verificacion['campos']])
            
            nuevos_datos = pd.DataFrame([datos])
            st.session_state.datos_hoja = pd.concat([st.session_state.datos_hoja, nuevos_datos], ignore_index=True)
            st.success("Datos guardados exitosamente")

    def visualizar_datos(self):
        """
        Visualización y análisis de datos de la hoja de verificación
        """
        st.subheader("📊 Visualización de Datos")
        
        if st.session_state.datos_hoja is not None and not st.session_state.datos_hoja.empty:
            # Mostrar datos
            st.dataframe(st.session_state.datos_hoja)
            
            # Selección de columna para análisis
            columna_analisis = st.selectbox("Seleccione columna para análisis", 
                                            st.session_state.datos_hoja.columns)
            
            # Tipo de gráfico según tipo de dato
            if pd.api.types.is_numeric_dtype(st.session_state.datos_hoja[columna_analisis]):
                # Gráficos para datos numéricos
                fig_hist = px.histogram(st.session_state.datos_hoja, x=columna_analisis, 
                                        title=f'Distribución de {columna_analisis}')
                st.plotly_chart(fig_hist)
                
                # Estadísticas descriptivas
                st.subheader("Estadísticas Descriptivas")
                st.write(st.session_state.datos_hoja[columna_analisis].describe())
            
            elif pd.api.types.is_categorical_dtype(st.session_state.datos_hoja[columna_analisis]):
                # Gráficos para datos categóricos
                fig_pie = px.pie(st.session_state.datos_hoja, names=columna_analisis, 
                                 title=f'Distribución de {columna_analisis}')
                st.plotly_chart(fig_pie)
            
            # Opciones de exportación
            if st.button("Exportar Datos a CSV"):
                csv = st.session_state.datos_hoja.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name='hoja_verificacion.csv',
                    mime='text/csv'
                )
        else:
            st.info("No hay datos para visualizar. Ingrese datos primero.")

def hoja_verificacion():
    """
    Función principal para el módulo de Hoja de Verificación
    """
    st.title("📋 Hoja de Verificación - Lean Six Sigma")
    
    # Instancia de la clase HojaVerificacion
    hv = HojaVerificacion()
    
    # Menú de opciones
    opcion = st.radio("Seleccione una Acción", [
        "Crear Hoja de Verificación", 
        "Ingresar Datos", 
        "Visualizar y Analizar Datos"
    ])
    
    # Llamar al método correspondiente según la opción
    if opcion == "Crear Hoja de Verificación":
        hv.crear_hoja_verificacion()
    elif opcion == "Ingresar Datos":
        hv.ingresar_datos()
    elif opcion == "Visualizar y Analizar Datos":
        hv.visualizar_datos()

# Punto de entrada para pruebas directas
if __name__ == "__main__":
    st.set_page_config(page_title="Hoja de Verificación LSS")
    hoja_verificacion()
