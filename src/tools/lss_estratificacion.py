import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns

def lss_estratificacion():
    """
    Función principal de Estratificación que maneja todo el análisis
    """
    st.title("🔬 Análisis de Estratificación")
    
    # Cargar datos desde la sesión
    df = st.session_state.get('uploaded_data')
    
    # Validaciones de datos
    if df is None:
        st.error("⚠️ No hay datos cargados")
        return
    
    # Configuraciones del módulo
    max_columnas = 20
    max_filas = 10000
    
    # Validaciones de seguridad
    if len(df.columns) > max_columnas:
        st.warning(f"Demasiadas columnas. Máximo {max_columnas}")
        return
    
    if len(df) > max_filas:
        st.warning(f"Demasiadas filas. Máximo {max_filas}")
        return
    
    # Preparar columnas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    columnas_categoricas = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Configuración de título y descripción
    titulo = st.text_input("Título del Análisis", "Análisis de Estratificación")
    descripcion = st.text_area("Descripción", "Análisis detallado de estratificación de datos")
    
    # Selección de variables
    col1, col2 = st.columns(2)
    
    with col1:
        variable_categorica = st.selectbox("Variable Categórica", 
            columnas_categoricas if columnas_categoricas else ['Sin categorías'])
    
    with col2:
        variable_numerica = st.selectbox("Variable Numérica", 
            columnas_numericas if columnas_numericas else ['Sin variables numéricas'])
    
    # Validar selección de variables
    if variable_categorica == 'Sin categorías' or variable_numerica == 'Sin variables numéricas':
        st.warning("Seleccione variables válidas para el análisis")
        return
    
    # Generar gráficos
    try:
        # Boxplot
        fig1 = px.box(
            df, 
            x=variable_categorica, 
            y=variable_numerica,
            title=f'Distribución de {variable_numerica} por {variable_categorica}'
        )
        
        # Gráfico de barras con agregación
        datos_agregados = df.groupby(variable_categorica)[variable_numerica].agg(['mean', 'count']).reset_index()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=datos_agregados[variable_categorica],
            y=datos_agregados['mean'],
            name='Promedio',
            marker_color='blue'
        ))
        fig2.add_trace(go.Scatter(
            x=datos_agregados[variable_categorica],
            y=datos_agregados['count'],
            name='Conteo',
            yaxis='y2',
            mode='lines+markers',
            marker_color='red'
        ))
        fig2.update_layout(
            title=f'Análisis de {variable_numerica} por {variable_categorica}',
            xaxis_title=variable_categorica,
            yaxis_title=f'Promedio de {variable_numerica}',
            yaxis2=dict(
                title='Conteo',
                overlaying='y',
                side='right'
            )
        )
        
        # Mostrar gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # Tabla resumen
        st.subheader("📊 Tabla Resumen")
        resumen = df.groupby(variable_categorica)[variable_numerica].agg([
            'count', 'mean', 'median', 'min', 'max', 'std'
        ]).round(2)
        st.dataframe(resumen)
        
        # Interpretación de resultados
        st.subheader("🔍 Interpretación de Resultados")
        interpretacion = f"""
        Análisis de Estratificación de {variable_numerica} por {variable_categorica}:
        
        - Categorías Identificadas: {len(resumen)} 
        - Distribución:
        {resumen.to_string()}
        
        Observaciones Principales:
        - Mayor concentración: {resumen['count'].idxmax()} 
        - Promedio más alto: {resumen['mean'].idxmax()}
        """
        st.info(interpretacion)
        
        # Exportación
        st.subheader("📥 Exportar Resultados")
        if st.button("Exportar Análisis"):
            # Lógica de exportación similar a versiones anteriores
            plt.figure(figsize=(15, 10))
            plt.suptitle(titulo, fontsize=16)
            
            # Añadir gráficos al PDF
            plt.subplot(1, 2, 1)
            img_bytes1 = fig1.to_image(format='png')
            plt.imshow(plt.imread(BytesIO(img_bytes1)))
            plt.axis('off')
            
            plt.subplot(1, 2, 2)
            img_bytes2 = fig2.to_image(format='png')
            plt.imshow(plt.imread(BytesIO(img_bytes2)))
            plt.axis('off')
            
            # Guardar y generar enlace de descarga
            pdf_buffer = BytesIO()
            plt.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
            pdf_buffer.seek(0)
            
            b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="analisis_estratificacion.pdf">Descargar Análisis</a>'
            st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error generando análisis de estratificación: {e}")

# Configuración de página
if __name__ == "__main__":
    st.set_page_config(page_title="Análisis de Estratificación", layout="wide")
    lss_estratificacion()
