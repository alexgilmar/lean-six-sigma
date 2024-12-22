import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class DiagramaDispersion:
    def __init__(self):
        # Cargar datos desde la sesión
        self.df = st.session_state.get('uploaded_data')
        
        # Configuraciones del módulo
        self.configuraciones = {
            'max_columnas': 20,
            'max_filas': 10000,
            'tipos_datos_validos': [np.number]
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

    def preparar_columnas(self) -> list:
        """
        Preparar columnas numéricas para análisis
        """
        try:
            columnas_numericas = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not columnas_numericas:
                st.warning("⚠️ No se encontraron columnas numéricas")
                return []
            
            return columnas_numericas
        
        except Exception as e:
            st.error(f"Error preparando columnas: {e}")
            return []

    def generar_diagrama_dispersion(self):
        """
        Generación de diagrama de dispersión con análisis profesional
        """
        st.title("🔍 Análisis de Diagrama de Dispersión")
        
        # Validaciones previas
        if not self.validar_datos():
            return
        
        # Preparar columnas
        columnas_numericas = self.preparar_columnas()
        
        if len(columnas_numericas) < 2:
            st.warning("Se necesitan al menos dos columnas numéricas para el análisis")
            return
        
        # Configuración de título y descripción
        titulo = st.text_input("Título del Análisis", "Diagrama de Dispersión")
        descripcion = st.text_area("Descripción", "Análisis de relación entre variables")
        
        # Selección de variables
        col1, col2 = st.columns(2)
        
        with col1:
            variable_x = st.selectbox("Variable Eje X", columnas_numericas)
        
        with col2:
            variable_y = st.selectbox("Variable Eje Y", 
                [col for col in columnas_numericas if col != variable_x])
        
        # Opciones adicionales
        with st.expander("Opciones Avanzadas"):
            color_por = st.selectbox("Colorear por", 
                ['Ninguno'] + [col for col in self.df.columns if col not in [variable_x, variable_y]])
            
            tamaño = st.selectbox("Tamaño de puntos", 
                ['Fijo', 'Variable'], index=0)
        
        # Generar gráfico
        try:
            fig = self._crear_diagrama_dispersion(
                variable_x, 
                variable_y, 
                color_por if color_por != 'Ninguno' else None,
                tamaño
            )
            
            # Mostrar gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            # Análisis estadístico
            self._generar_analisis_estadistico(variable_x, variable_y)
            
            # Botón de exportación
            self._exportar_resultados(
                fig, 
                titulo, 
                descripcion, 
                variable_x, 
                variable_y
            )
            
        except Exception as e:
            st.error(f"Error generando diagrama de dispersión: {e}")

    def _crear_diagrama_dispersion(self, x, y, color=None, tamaño='Fijo'):
        """
        Crear diagrama de dispersión interactivo
        """
        # Preparación de datos
        datos = self.df[[x, y]]
        if color:
            datos[color] = self.df[color]
        
        # Configuración de tamaño
        if tamaño == 'Fijo':
            size = 8
        else:
            # Normalizar tamaño basado en otra variable numérica
            size = self.df[x] / self.df[x].max() * 20
        
        # Crear figura
        if color:
            fig = px.scatter(
                datos, 
                x=x, 
                y=y, 
                color=color,
                title=f'Diagrama de Dispersión: {x} vs {y}',
                labels={x: x, y: y},
                hover_data=datos.columns
            )
        else:
            fig = px.scatter(
                datos, 
                x=x, 
                y=y, 
                title=f'Diagrama de Dispersión: {x} vs {y}',
                labels={x: x, y: y}
            )
        
        # Personalización
        fig.update_traces(marker=dict(size=size))
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Rockwell"
            )
        )
        
        return fig

    def _generar_analisis_estadistico(self, x, y):
        """
        Generar análisis estadístico del diagrama de dispersión
        """
        # Cálculo de correlación
        correlacion = self.df[x].corr(self.df[y])
        
        # Tabla de métricas
        st.subheader("📊 Análisis Estadístico")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Correlación", f"{correlacion:.2f}")
        
        with col2:
            st.metric("Media X", f"{self.df[x].mean():.2f}")
        
        with col3:
            st.metric("Media Y", f"{self.df[y].mean():.2f}")
        
        # Interpretación de correlación
        interpretacion = self._interpretar_correlacion(correlacion)
        st.info(interpretacion)

    def _interpretar_correlacion(self, correlacion):
        """
        Interpretar el valor de correlación
        """
        if abs(correlacion) < 0.3:
            return f"Correlación débil ({correlacion:.2f}): No hay una relación lineal fuerte."
        elif abs(correlacion) < 0.7:
            return f"Correlación moderada ({correlacion:.2f}): Existe una relación lineal parcial."
        else:
            return f"Correlación fuerte ({correlacion:.2f}): Existe una relación lineal significativa."

    def _exportar_resultados(self, fig, titulo, descripcion, x, y):
        """
        Exportar resultados del análisis
        """
        st.subheader("📥 Exportar Resultados")
        
        # Exportar como PDF
        if st.button("Exportar Análisis"):
            # Crear PDF
            pdf_buffer = BytesIO()
            
            # Convertir figura Plotly a imagen
            img_bytes = fig.to_image(format='png')
            
            # Crear PDF con matplotlib
            plt.figure(figsize=(10, 6))
            plt.title(titulo)
            plt.imshow(plt.imread(BytesIO(img_bytes)))
            plt.axis('off')
            
            # Guardar PDF
            plt.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
            pdf_buffer.seek(0)
            
            # Generar enlace de descarga
            b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="analisis_dispersion.pdf">Descargar Análisis</a>'
            st.markdown(href, unsafe_allow_html=True)

def diagrama_dispersion():
    """Función principal del módulo de Diagrama de Dispersión"""
    dispersao = DiagramaDispersion()
    dispersao.generar_diagrama_dispersion()

# Configuración de página
if __name__ == "__main__":
    st.set_page_config(page_title="Diagrama de Dispersión", layout="wide")
    diagrama_dispersion()
