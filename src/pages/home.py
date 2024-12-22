import streamlit as st

def render_home_page():
    # st.title("Bienvenido a Toritos de Pucara Analytics")
    
    # Sección de descripción
    st.markdown("""
    ## Herramientas de Análisis Estadístico para Mejora de Procesos
    
    ### Nuestra Misión
    Proporcionar herramientas avanzadas de análisis estadístico para optimizar procesos 
    y mejorar la eficiencia operativa.
    
    ### Características Principales
    - 📊 Calculadora DPMO
    - 🧩 Herramientas Lean Six Sigma
    - 📈 Análisis de Procesos
    - 📉 Gráficos de Control
    - 🔍 Análisis de Capacidad
    """)
    
    # Columnas para características
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Calculadora DPMO")
        st.write("Mide la eficiencia de tus procesos con nuestra calculadora de Defectos Por Millón de Oportunidades.")
    
    with col2:
        st.subheader("Herramientas LSS")
        st.write("Accede a herramientas de Lean Six Sigma para análisis y mejora continua.")
    
    with col3:
        st.subheader("Análisis Estadístico")
        st.write("Realiza análisis estadísticos avanzados con nuestras herramientas.")
    
    # Sección de llamado a la acción
    st.markdown("---")
    st.markdown("### ¿Listo para Optimizar tus Procesos?")
    
    # Solo mostrar botón si no está logueado
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.markdown("""
        Regístrate o inicia sesión para acceder a todas nuestras herramientas.
        
        [🔐 Iniciar Sesión](#) [📝 Registrarse](#)
        """)

# Si se ejecuta directamente este archivo (para pruebas)
if __name__ == "__main__":
    render_home_page()
