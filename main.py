import streamlit as st
import sys
import os # Importar módulo os para manejo de archivos
import traceback # Importar módulo traceback o sys para mostrar errores


# Añadir el directorio src al path de Python
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# funciones de system
from src.auth.login import login_page
from src.auth.register import register_page
from src.pages.home import render_home_page

# Importa la función dp
from src.tools.dpmo_calculator import dpmo_calculator_page

# importacion data_management.upload
from src.data_management.upload import upload_data_page

# Importación list de dashboard
from src.pages.dashboard import dashboard
from src.tools.lss_tool1_pareto import load_lss_tool1_pareto # importacion herramienta de pareto
from src.tools.lss_tool3_control_chart import load_lss_tool3_control_chart
from src.tools.lss_hoja_verificacion import hoja_verificacion
from src.tools.lss_tool2_ishikawa import ishikawa_page
from src.tools.lss_histograma import histograma
from src.tools.lss_dispersion import diagrama_dispersion
from src.tools.lss_estratificacion import lss_estratificacion



# Configuración de página
st.set_page_config(
    # page_title="Analytics", 
    page_icon=":bar_chart:", 
    layout="wide"
)

def main():
    # Inicializar estado de sesión si no existe
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Barra lateral de navegación
    if not st.session_state['logged_in']:
        # Menú para usuarios no autenticados
        menu = st.sidebar.radio("Navegación", 
            ["🏠 Inicio", "🔐 Iniciar Sesión", "📝 Registrarse"]
        )
        
        # Renderizar páginas según selección
        if menu == "🏠 Inicio":
            render_home_page()
        elif menu == "🔐 Iniciar Sesión":
            login_page()
        elif menu == "📝 Registrarse":
            register_page()
    
    else:
        # Menú para usuarios autenticados
        menu = st.sidebar.radio("Menú Principal", [
            "🏠 Inicio",
            "📝 Carga de Datos",
            "📊 Dashboard",
            "🧮 Calculadora DPMO",
            "📋 Hoja de Verificación",
            "📊 Diagrama de Pareto",
            "🐟 Diagrama de Ishikawa",
            "📈 Histograma",
            "🔍 Diagrama de Dispersión",
            "🎛️ Gráficas de Control",
            "🔬 Estratificación",  # falta
            # "🛠️ Herramientas Complementarias LSS",
            "🚪 Cerrar Sesión"
        ])





        # if menu == "🛠️ Herramientas Complementarias LSS":
        #     # Menú de Herramientas Complementarias
        #     herramientas_complementarias = st.sidebar.radio("Herramientas Complementarias LSS", [
        #         "🗺️ SIPOC",
        #         # "🔀 Diagrama de Flujo",
        #         # "❓ Método Five Why",
        #         # "🛡️ Poka-Yoke",
        #         # "📏 Análisis de Capacidad",
        #         # "🔄 Mapa de Flujo de Valor",
        #         # "🚀 Kaizen",
        #         # "🔧 Mejora Continua"
        #     ])

        # Lógica de navegación para usuarios autenticados
        if menu == "🏠 Inicio":
            st.title(f"Bienvenido, {st.session_state['username']}")
            render_home_page()
        elif menu == "📝 Carga de Datos":
            st.title("Carga de Datos")
            # Importar e implementar función de carga de datos
            upload_data_page()
        elif menu == "📊 Dashboard":
            # Implementar dashboard
            dashboard()
        elif menu == "🧮 Calculadora DPMO": # estamos implementando
            try:
                st.write("Intentando cargar calculadora DPMO")
                dpmo_calculator_page() # lama a la función dp de dpmo_calculator.py
            except Exception as e:
                st.error(f"Error al cargar la calculadora DPMO: {e}")
                st.write(f"Detalles del error: {traceback.format_exc()}")
        
        
        elif menu == "📋 Hoja de Verificación":
            hoja_verificacion()

        elif menu == "📊 Diagrama de Pareto":
            load_lss_tool1_pareto()

        elif menu == "🐟 Diagrama de Ishikawa":
            ishikawa_page()

        elif menu == "📈 Histograma":
            histograma()

        elif menu == "🔬 Estratificación":
            lss_estratificacion()


        elif menu == "🎛️ Gráficas de Control":
            # st.title("grafico de control")
            load_lss_tool3_control_chart()

        # elif menu == "🔬 Estratificación":
        #     st.title("Diagrama ishikawa")

        elif menu == "🔬 Estratificación":
            lss_estratificacion.ejecutar_modulo()

        # elif menu == "👤 Perfil de Usuario":
        #     funcion_name()
            
        elif menu == "🚪 Cerrar Sesión":
            # Cerrar sesión
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.experimental_rerun()




# Estilos personalizados
def load_css():
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Punto de entrada principal
if __name__ == "__main__":
    load_css()  # Cargar estilos personalizados
    main()
