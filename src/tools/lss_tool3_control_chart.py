import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import base64

class ControlChartAnalyzer:
    def __init__(self, dataframe):
        self.df = dataframe
        self.numeric_columns = dataframe.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = dataframe.select_dtypes(include=['object']).columns.tolist()

    def calcular_limites_control_xbarra(self, variable):
        """
        Calcula límites de control para gráfico X-barra
        """
        datos = self.df[variable]
        media = datos.mean()
        desviacion = datos.std()
        
        # Límites de control clásicos (3-sigma)
        lim_superior = media + 3 * (desviacion / np.sqrt(len(datos)))
        lim_inferior = media - 3 * (desviacion / np.sqrt(len(datos)))
        
        return {
            'media': media,
            'limite_superior': lim_superior,
            'limite_inferior': lim_inferior
        }

    def generar_grafico_control_xbarra(self, variable):
        """
        Genera gráfico de control X-barra interactivo
        """
        limites = self.calcular_limites_control_xbarra(variable)
        
        fig = go.Figure()
        
        # Puntos de datos
        fig.add_trace(go.Scatter(
            x=self.df.index, 
            y=self.df[variable],
            mode='markers+lines',
            name=f'{variable}',
            marker=dict(
                color=self.df[variable].apply(
                    lambda x: 'red' if x > limites['limite_superior'] or x < limites['limite_inferior'] else 'blue'
                )
            )
        ))
        
        # Línea de media
        fig.add_trace(go.Scatter(
            x=self.df.index, 
            y=[limites['media']] * len(self.df),
            mode='lines',
            name='Media',
            line=dict(color='green', dash='dash')
        ))
        
        # Límites de control
        fig.add_trace(go.Scatter(
            x=self.df.index, 
            y=[limites['limite_superior']] * len(self.df),
            mode='lines',
            name='Límite Superior',
            line=dict(color='red', dash='dot')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.df.index, 
            y=[limites['limite_inferior']] * len(self.df),
            mode='lines',
            name='Límite Inferior',
            line=dict(color='red', dash='dot')
        ))
        
        fig.update_layout(
            title=f'Gráfico de Control X-barra para {variable}',
            xaxis_title='Muestra',
            yaxis_title='Valor'
        )
        
        return fig, limites

    def interpretar_grafico_control(self, variable, limites):
        """
        Genera interpretación contextualizada
        """
        fuera_control = self.df[
            (self.df[variable] > limites['limite_superior']) | 
            (self.df[variable] < limites['limite_inferior'])
        ]
        
        interpretacion = [
            f"Análisis de Control de Calidad para {variable}:",
            f"Media: {limites['media']:.2f}",
            f"Límite Superior de Control: {limites['limite_superior']:.2f}",
            f"Límite Inferior de Control: {limites['limite_inferior']:.2f}",
            f"Número de muestras fuera de control: {len(fuera_control)}"
        ]
        
        if len(fuera_control) > 0:
            interpretacion.append("ALERTA: Existen muestras fuera de los límites de control")
        
        return interpretacion

    def exportar_pdf(self, fig, variable, limites, interpretacion):
        """
        Exporta análisis a PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elementos = []
        
        # Estilos
        estilos = getSampleStyleSheet()
        
        # Título
        elementos.append(Paragraph(f"Análisis de Control de Calidad - {variable}", estilos['Title']))
        
        # Guardar gráfico como imagen
        img_buffer = io.BytesIO()
        fig.write_image(img_buffer, format='png')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Imagen
        from reportlab.platypus import Image
        img_path = f"data:image/png;base64,{img_base64}"
        elementos.append(Image(img_path, width=500, height=300))
        
        # Interpretación
        elementos.append(Paragraph("Interpretación", estilos['Heading2']))
        for linea in interpretacion:
            elementos.append(Paragraph(linea, estilos['Normal']))
        
        # Tabla de Límites
        datos_tabla = [
            ['Métrica', 'Valor'],
            ['Media', f"{limites['media']:.2f}"],
            ['Límite Superior', f"{limites['limite_superior']:.2f}"],
            ['Límite Inferior', f"{limites['limite_inferior']:.2f}"]
        ]
        tabla = Table(datos_tabla)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elementos.append(tabla)
        
        doc.build(elementos)
        return buffer.getvalue()

def lss_tool3_control_chart_page():
    st.title("🔍 Gráficos de Control de Calidad")
    
    # Verificar datos cargados
    if 'uploaded_data' not in st.session_state:
        st.warning("Por favor, cargue un conjunto de datos primero.")
        return
    
    df = st.session_state['uploaded_data']
    
    # Instanciar analizador
    analizador = ControlChartAnalyzer(df)
    
    # Selección de variables
    variable = st.selectbox(
        "Seleccione Variable para Análisis de Control",
        options=analizador.numeric_columns
    )
    
    # Generar gráfico
    fig, limites = analizador.generar_grafico_control_xbarra(variable)
    
    # Mostrar gráfico
    st.plotly_chart(fig)
    
    # Interpretación
    interpretacion = analizador.interpretar_grafico_control(variable, limites)
    st.info("\n".join(interpretacion))
    
    # Botón de exportación
    if st.button("Exportar Análisis a PDF"):
        pdf_data = analizador.exportar_pdf(fig, variable, limites, interpretacion)
        st.download_button(
            label="Descargar Informe PDF",
            data=pdf_data,
            file_name=f"control_calidad_{variable}.pdf",
            mime="application/pdf"
        )

def load_lss_tool3_control_chart():
    lss_tool3_control_chart_page()
