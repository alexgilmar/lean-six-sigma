import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import io
import base64

class ParetoDiagram:
    def __init__(self, df):
        self.df = df
        self.categorias_posibles = list(df.columns)

    def preparar_datos_pareto(self, columna_categoria, columna_valor=None):
        """
        Prepara los datos para el diagrama de Pareto con flexibilidad
        """
        if columna_valor:
            # Agrupar por categoría y sumar valores
            grouped = self.df.groupby(columna_categoria)[columna_valor].sum()
        else:
            # Conteo de frecuencias
            grouped = self.df[columna_categoria].value_counts()
        
        # Calcular porcentajes
        total = grouped.sum()
        porcentajes = (grouped / total * 100).round(2)
        
        # Crear DataFrame de Pareto
        df_pareto = pd.DataFrame({
            'Categoria': grouped.index,
            'Valor': grouped.values,
            'Porcentaje Individual': porcentajes.values
        })
        
        # Calcular porcentaje acumulado
        df_pareto['Porcentaje Acumulado'] = df_pareto['Porcentaje Individual'].cumsum()
        
        # Ordenar de mayor a menor
        df_pareto = df_pareto.sort_values('Valor', ascending=False)
        
        return df_pareto

    def generar_grafico_pareto(self, df_pareto):
        """
        Genera gráfico de Pareto interactivo
        """
        fig = go.Figure()
        
        # Barras de frecuencia
        fig.add_trace(go.Bar(
            x=df_pareto['Categoria'],
            y=df_pareto['Valor'],
            name='Valor',
            marker_color='rgba(58, 71, 80, 0.6)',
            yaxis='y1'
        ))
        
        # Línea de porcentaje acumulado
        fig.add_trace(go.Scatter(
            x=df_pareto['Categoria'],
            y=df_pareto['Porcentaje Acumulado'],
            name='% Acumulado',
            marker_color='red',
            yaxis='y2'
        ))
        
        # Configuración de layout
        fig.update_layout(
            title='Diagrama de Pareto - Análisis Detallado',
            xaxis_title='Categorías',
            yaxis_title='Valor',
            yaxis2=dict(
                title='Porcentaje Acumulado',
                overlaying='y',
                side='right',
                range=[0, 110]
            )
        )
        
        return fig

    def interpretar_pareto(self, df_pareto, columna_categoria):
        """
        Genera interpretación contextualizada del diagrama de Pareto
        """
        # Identificar categorías críticas (80% del problema)
        categorias_criticas = df_pareto[df_pareto['Porcentaje Acumulado'] <= 80]
        
        # Interpretaciones por tipo de análisis
        interpretaciones = {
            'defectos': [
                "Los defectos críticos requieren atención inmediata.",
                "Concentre esfuerzos en reducir las causas principales de los defectos."
            ],
            'tiempos': [
                "Las etapas con mayor tiempo de proceso necesitan optimización.",
                "Identifique oportunidades de mejora en los procesos más lentos."
            ],
            'costos': [
                "Los rubros con mayor impacto económico demandan una revisión estratégica.",
                "Priorice acciones para reducir los costos más significativos."
            ],
            'default': [
                "Se han identificado las categorías más relevantes del análisis.",
                "Enfoque sus esfuerzos en las áreas con mayor impacto."
            ]
        }
        
        # Seleccionar interpretación
        if 'defecto' in columna_categoria.lower():
            contexto = 'defectos'
        elif 'tiempo' in columna_categoria.lower():
            contexto = 'tiempos'
        elif 'costo' in columna_categoria.lower():
            contexto = 'costos'
        else:
            contexto = 'default'
        
        base_interpretacion = interpretaciones[contexto]
        
        return base_interpretacion

    def generar_resumen_critico(self, df_pareto):
        """
        Genera un resumen de las categorías críticas según Pareto
        """
        # Categorías que representan el 80% del problema
        criticos = df_pareto[df_pareto['Porcentaje Acumulado'] <= 80]
        
        resumen = pd.DataFrame({
            'Categoría': criticos['Categoria'],
            'Valor': criticos['Valor'],
            '% Individual': criticos['Porcentaje Individual'],
            '% Acumulado': criticos['Porcentaje Acumulado']
        })
        
        return resumen

def exportar_pdf(fig, df_pareto, interpretacion):
    """
    Exporta el análisis de Pareto a PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Título
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Análisis de Pareto", styles['Title']))
    
    # Guardar gráfico como imagen
    img_buffer = io.BytesIO()
    fig.write_image(img_buffer, format='png')
    img_buffer.seek(0)
    
    # Convertir imagen a base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    # Agregar imagen al PDF
    img_path = f"data:image/png;base64,{img_base64}"
    elements.append(Image(img_path, width=500, height=300))
    
    # Tabla de datos
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    
    tabla_datos = [df_pareto.columns.tolist()] + df_pareto.values.tolist()
    tabla = Table(tabla_datos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    elements.append(tabla)
    
    # Interpretación
    elements.append(Paragraph("Interpretación", styles['Heading2']))
    elements.append(Paragraph(interpretacion, styles['Normal']))
    
    doc.build(elements)
    
    return buffer.getvalue()

def lss_tool1_pareto_page():
    st.title("🔍 Herramienta Diagrama de Pareto")
    
    # Verificar si hay datos cargados
    if 'uploaded_data' not in st.session_state:
        st.warning("Por favor, cargue primero un conjunto de datos.")
        return
    
    df = st.session_state['uploaded_data']
    
    # Columnas numéricas y categóricas
    cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_categoricas = df.select_dtypes(include=['object']).columns.tolist()
    
    # Selectores de columnas
    col1, col2 = st.columns(2)
    
    with col1:
        columna_categoria = st.selectbox(
            "Seleccione columna categórica", 
            options=cols_categoricas
        )
    
    with col2:
        columna_valor = st.selectbox(
            "Seleccione columna de valor (opcional)", 
            options=['Sin valor'] + cols_numericas
        )
    
    # Preparar datos de Pareto
    pareto = ParetoDiagram(df)
    
    # Condicional para preparar datos
    if columna_valor == 'Sin valor':
        df_pareto = pareto.preparar_datos_pareto(columna_categoria)
    else:
        df_pareto = pareto.preparar_datos_pareto(columna_categoria, columna_valor)
    
    # Generar gráfico
    fig_pareto = pareto.generar_grafico_pareto(df_pareto)
    
    # Mostrar gráfico
    st.plotly_chart(fig_pareto)
    
    # Interpretación
    interpretacion = pareto.interpretar_pareto(df_pareto, columna_categoria)
    st.info(" ".join(interpretacion))
    
    # Resumen crítico
    st.subheader("Resumen de Categorías Críticas")
    resumen_critico = pareto.generar_resumen_critico(df_pareto)
    st.dataframe(resumen_critico)
    
    # Botón de exportación PDF
    if st.button("Exportar Análisis a PDF"):
        pdf_data = exportar_pdf(fig_pareto, df_pareto, " ".join(interpretacion))
        st.download_button(
            label="Descargar PDF",
            data=pdf_data,
            file_name="analisis_pareto.pdf",
            mime="application/pdf"
        )

# Función para ser llamada en main.py
def load_lss_tool1_pareto():
    lss_tool1_pareto_page()
