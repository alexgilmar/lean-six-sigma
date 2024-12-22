import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import matplotlib.pyplot as plt
from typing import List, Optional

class HistogramaLSS:
    def __init__(self):
        self.df = st.session_state.get('uploaded_data')
        
        # Configuraciones de seguridad y validación
        self.configuraciones = {
            'max_columnas': 20,
            'max_filas': 10000,
            'tipos_datos_validos': [np.number, 'object', 'category']
        }

    def validar_datos(self) -> bool:
        """
        Validación integral de datos antes del análisis
        """
        if self.df is None:
            st.error("⚠️ No hay datos cargados")
            return False
        
        try:
            # Validaciones de seguridad
            if len(self.df.columns) > self.configuraciones['max_columnas']:
                st.warning(f"Demasiadas columnas. Máximo {self.configuraciones['max_columnas']}")
                return False
            
            if len(self.df) > self.configuraciones['max_filas']:
                st.warning(f"Demasiadas filas. Máximo {self.configuraciones['max_filas']}")
                return False
            
            return True
        
        except Exception as e:
            st.error(f"Error en validación de datos: {e}")
            return False

    def preparar_columnas(self) -> tuple:
        """
        Preparar columnas para análisis con manejo de excepciones
        """
        try:
            columnas_numericas = self.df.select_dtypes(include=[np.number]).columns.tolist()
            columnas_categoricas = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not columnas_numericas:
                st.warning("⚠️ No se encontraron columnas numéricas")
                return [], []
            
            return columnas_numericas, columnas_categoricas
        
        except Exception as e:
            st.error(f"Error preparando columnas: {e}")
            return [], []

    def generar_histograma_profesional(self):
        """
        Generación de histograma con validaciones y análisis profesional
        """
        st.title("📊 Análisis Estadístico Profesional")
        
        # Validaciones previas
        if not self.validar_datos():
            return
        
        # Preparar columnas
        columnas_numericas, columnas_categoricas = self.preparar_columnas()
        
        if not columnas_numericas:
            st.warning("No hay datos numéricos para analizar")
            return
        
        # Selector de variable
        variable = st.selectbox("Seleccione Variable para Análisis", columnas_numericas)
        
        try:
            # Generación de histograma
            fig = self._crear_histograma_detallado(variable)
            
            # Mostrar gráfico
            st.plotly_chart(fig)
            
            # Tabla resumen y análisis
            self._generar_tabla_resumen(variable)
            
        except Exception as e:
            st.error(f"Error generando histograma: {e}")

    def _crear_histograma_detallado(self, variable: str):
        """
        Crear histograma con detalles profesionales
        """
        datos = self.df[variable]
        
        # Cálculos estadísticos
        media = datos.mean()
        mediana = datos.median()
        desv_std = datos.std()
        
        # Histograma con distribución
        fig = go.Figure()
        
        # Histograma base
        fig.add_trace(go.Histogram(
            x=datos, 
            name='Distribución',
            marker_color='blue',
            opacity=0.7
        ))
        
        # Línea de media
        fig.add_shape(
            type='line', 
            x0=media, 
            x1=media, 
            y0=0, 
            y1=1, 
            yref='paper',
            line=dict(color='red', width=2, dash='dash')
        )
        
        # Configuraciones adicionales
        fig.update_layout(
            title=f'Análisis Detallado de {variable}',
            xaxis_title=variable,
            yaxis_title='Frecuencia',
            annotations=[
                dict(
                    x=media, 
                    y=1.1, 
                    xref='x', 
                    yref='paper',
                    text=f'Media: {media:.2f}',
                    showarrow=True
                )
            ]
        )
        
        return fig

    def _generar_tabla_resumen(self, variable: str):
        """
        Generar tabla resumen con interpretaciones
        """
        datos = self.df[variable]
        
        # Métricas estadísticas
        metricas = {
            'Media': datos.mean(),
            'Mediana': datos.median(),
            'Desviación Estándar': datos.std(),
            'Mínimo': datos.min(),
            'Máximo': datos.max(),
            'Rango': datos.max() - datos.min(),
            'Varianza': datos.var()
        }
        
        # Tabla resumen
        st.subheader("📋 Tabla Resumen Estadístico")
        df_resumen = pd.DataFrame.from_dict(metricas, orient='index', columns=['Valor'])
        st.dataframe(df_resumen)
        
        # Interpretaciones
        st.subheader("🔍 Interpretación")
        
        # Interpretación básica
        interpretacion = f"""
        Análisis de {variable}:
        - Valor Central: La media de {metricas['Media']:.2f} indica el punto central de distribución.
        - Variabilidad: Desviación estándar de {metricas['Desviación Estándar']:.2f} sugiere dispersión de datos.
        - Rango: Varía entre {metricas['Mínimo']:.2f} y {metricas['Máximo']:.2f}.
        """
        
        st.info(interpretacion)

def histograma():
    """Función principal del módulo de Histograma"""
    hist = HistogramaLSS()
    hist.generar_histograma_profesional()

# Configuración de página
if __name__ == "__main__":
    st.set_page_config(page_title="Análisis Estadístico", layout="wide")
    histograma()
