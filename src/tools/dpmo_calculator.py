import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

def dpmo_calculator_page():
    # Tabla de referencia de niveles Sigma
    sigma_table = pd.DataFrame({
        "Nivel Sigma": ["2σ", "3σ", "4σ", "5σ", "6σ"],
        "DPMO": [308537, 66807, 6210, 233, 3.4],
        "Rendimiento": ["69.2%", "93.3%", "99.38%", "99.977%", "99.9997%"]
    })

    # Función de cálculo de DPMO
    def calcular_dpmo(defectos, unidades, oportunidades):
        if unidades <= 0 or oportunidades <= 0:
            st.error("Las unidades y oportunidades deben ser mayores que cero")
            return None, None, None
        
        if defectos > (unidades * oportunidades):
            st.error("Los defectos no pueden ser mayores que las oportunidades totales")
            return None, None, None

        dpmo = (defectos * 1_000_000) / (unidades * oportunidades)
        rendimiento = 1 - (dpmo / 1_000_000)
        sigma_nivel = norm.ppf(rendimiento) + 1.5
        return dpmo, sigma_nivel, rendimiento

    # Función para crear visualizaciones
    def crear_visualizaciones(dpmo, sigma_table):
        col1, col2 = st.columns(2)
        
        # Gráfico 1: Comparación de DPMO
        with col1:
            st.subheader("Comparación de DPMO")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            sns.barplot(x=sigma_table["Nivel Sigma"], y=sigma_table["DPMO"], palette="Blues", ax=ax1)
            ax1.axhline(dpmo, color="red", linestyle="--", label=f"DPMO Calculado ({dpmo:.2f})")
            ax1.set_ylabel("DPMO")
            ax1.set_title("DPMO por Nivel Sigma")
            ax1.legend()
            st.pyplot(fig1)

        # Gráfico 2: Rendimiento por Nivel Sigma
        with col2:
            st.subheader("Rendimiento por Nivel Sigma")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sigma_table['Rendimiento_Num'] = sigma_table['Rendimiento'].str.rstrip('%').astype('float')
            sns.barplot(x=sigma_table["Nivel Sigma"], y=sigma_table["Rendimiento_Num"], palette="Greens", ax=ax2)
            ax2.set_ylabel("Rendimiento (%)")
            ax2.set_title("Rendimiento por Nivel Sigma")
            st.pyplot(fig2)

    # Función de interpretación
    def interpretar_resultado(sigma_nivel):
        if sigma_nivel is None:
            return None
        
        interpretaciones = {
            (0, 2): "Nivel Crítico: Proceso con alta variabilidad y muchos defectos",
            (2, 3): "Nivel Deficiente: Requiere mejoras significativas",
            (3, 4): "Nivel Aceptable: Proceso con calidad media",
            (4, 5): "Nivel Bueno: Proceso con alta calidad",
            (5, 6): "Nivel Excelente: Proceso de clase mundial",
            (6, float('inf')): "Nivel Six Sigma: Proceso casi perfecto"
        }
        
        for (min_val, max_val), interpretacion in interpretaciones.items():
            if min_val <= sigma_nivel < max_val:
                return interpretacion
        
        return "Resultado fuera de rango"

    # Interfaz principal
    st.title("🔢 Calculadora de DPMO")
    st.markdown("Calcula los Defectos por Millón de Oportunidades (DPMO)")

    # Formulario de entrada
    with st.form("calculadora_dpmo"):
        defectos = st.number_input("Defectos Totales", min_value=0, step=1, format="%d")
        unidades = st.number_input("Total de Unidades", min_value=1, step=1, format="%d")
        oportunidades = st.number_input("Oportunidades por Unidad", min_value=1, step=1, format="%d")
        submit_button = st.form_submit_button(label="Calcular 📊")

    # Procesamiento de resultados
    if submit_button:
        resultado = calcular_dpmo(defectos, unidades, oportunidades)
        
        if resultado[0] is not None:
            dpmo, sigma_nivel, rendimiento = resultado

            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric(label="DPMO Calculado", value=f"{dpmo:.2f}")
            col2.metric(label="Nivel Sigma", value=f"{sigma_nivel:.2f}")
            col3.metric(label="Rendimiento", value=f"{rendimiento * 100:.2f}%")

            # Interpretación
            interpretacion = interpretar_resultado(sigma_nivel)
            st.subheader("Interpretación del Resultado")
            st.info(interpretacion)

            # Visualizaciones
            crear_visualizaciones(dpmo, sigma_table)

            # Exportación de resultados
            resultados = pd.DataFrame({
                'Métrica': ['DPMO', 'Nivel Sigma', 'Rendimiento'],
                'Valor': [dpmo, sigma_nivel, rendimiento * 100]
            })
            st.download_button(
                label="Descargar Resultados", 
                data=resultados.to_csv(index=False).encode('utf-8'),
                file_name='resultados_dpmo.csv',
                mime='text/csv'
            )

# Punto de entrada
def main():
    dpmo_calculator_page()

if __name__ == "__main__":
    main()
