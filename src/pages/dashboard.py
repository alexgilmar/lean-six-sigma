import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
import base64

from src.data_management.data_session import DataSession

class DashboardPersonalizado:
    def __init__(self, df):
        self.df = df
        self.variables = list(df.columns)
        
        # Valores por defecto
        self.titulo = "Dashboard de Análisis de Producción"
        self.descripcion = "Análisis detallado de métricas"
        self.variables_seleccionadas = self.variables[2:4]  # Seleccionar primeras 3 variables
    
    def configurar_dashboard(self):
        """Modal de configuración de dashboard"""
        with st.expander("🔧 Configurar Dashboard"):
            self.titulo = st.text_input(
                "Título del Dashboard", 
                value=self.titulo
            )
            self.descripcion = st.text_area(
                "Descripción", 
                value=self.descripcion
            )
    
    def seleccionar_variables(self):
        """Selector dinámico de variables"""
        with st.sidebar.expander("📊 Selección de Variables"):
            self.variables_seleccionadas = st.multiselect(
                "Seleccione variables para análisis",
                self.variables,
                default=self.variables_seleccionadas
            )
    
    def generar_kpis(self):
        """Generación dinámica de KPIs"""
        st.header("🎯 Indicadores Clave (KPIs)")
        
        kpi_cols = st.columns(len(self.variables_seleccionadas))
        
        for i, variable in enumerate(self.variables_seleccionadas):
            with kpi_cols[i]:
                valor_medio = self.df[variable].mean()
                valor_min = self.df[variable].min()
                valor_max = self.df[variable].max()
                
                st.metric(
                    label=f"📈 {variable}", 
                    value=f"{valor_medio:.2f}",
                    delta=f"Min: {valor_min:.2f} | Max: {valor_max:.2f}"
                )
    
    def graficos_control(self):
        """Gráficos de control para variables seleccionadas"""
        st.header("🔍 Gráficos de Control")
        
        for variable in self.variables_seleccionadas:
            # Gráfico de línea con límites de control
            fig = px.line(
                self.df, 
                y=variable, 
                title=f'Gráfico de Control - {variable}',
                labels={'index': 'Observaciones', 'value': variable}
            )
            
            # Añadir bandas de control
            fig.add_hrect(
                y0=self.df[variable].mean() - self.df[variable].std(), 
                y1=self.df[variable].mean() + self.df[variable].std(), 
                fillcolor="green", 
                opacity=0.2,
                layer="below",
                line_width=0,
            )
            
            st.plotly_chart(fig)
    
    def graficos_distribucion(self):
        """Gráficos de distribución"""
        st.header("📊 Distribución de Variables")
        
        for variable in self.variables_seleccionadas:
            # Histograma
            fig = px.histogram(
                self.df, 
                x=variable, 
                title=f'Distribución de {variable}',
                marginal='box'  # Añade un boxplot al margen
            )
            st.plotly_chart(fig)
    
    def exportar_pdf(self):
        """Modal de exportación a PDF"""
        with st.expander("📄 Exportar Dashboard"):
            nombre_archivo = st.text_input(
                "Nombre del archivo PDF", 
                value="dashboard_analisis"
            )
            
            if st.button("Generar PDF"):
                # Implementación básica de exportación a PDF
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                width, height = letter
                
                # Título
                c.setFont("Helvetica-Bold", 16)
                c.drawString(inch, height - inch, self.titulo)
                
                # Descripción
                c.setFont("Helvetica", 12)
                c.drawString(inch, height - (inch * 1.5), self.descripcion)
                
                c.save()
                
                pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="{nombre_archivo}.pdf">Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
    
    def render(self):
        """Renderizar dashboard completo"""
        st.title(self.titulo)
        st.write(self.descripcion)
        
        self.generar_kpis()
        self.graficos_control()
        self.graficos_distribucion()
        self.exportar_pdf()

def dashboard():
    """Función principal del dashboard"""
    # Recuperar DataFrame de sesión
    df = DataSession.get_dataframe()
    
    if df is not None:
        dashboard_instance = DashboardPersonalizado(df)
        
        # Configuraciones
        dashboard_instance.configurar_dashboard()
        dashboard_instance.seleccionar_variables()
        
        # Renderizar
        dashboard_instance.render()
    else:
        st.warning("No se ha cargado ningún conjunto de datos. Por favor, cargue datos primero.")
