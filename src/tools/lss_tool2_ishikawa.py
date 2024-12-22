import streamlit as st
import graphviz
import pandas as pd

def initialize_session_state():
    """Inicializa el estado de la sesión si no está presente."""
    if 'causes_data' not in st.session_state:
        st.session_state.causes_data = {
            "Métodos": [],
            "Maquinaria": [],
            "Mano de obra": [],
            "Materiales": [],
            "Medio Ambiente": []
        }
    if 'effect' not in st.session_state:
        st.session_state.effect = ""

def add_cause_to_category(category, cause, whys):
    """Agrega una causa a la categoría especificada."""
    if cause:
        st.session_state.causes_data[category].append({
            "cause": cause,
            "whys": whys
        })

def create_summary_table():
    """Crea una tabla resumen de las causas y efectos."""
    data = []
    for category, items in st.session_state.causes_data.items():
        for item in items:
            data.append({
                "Categoría": category,
                "Causa": item["cause"],
                "Por qués": " → ".join(item["whys"])
            })
    return pd.DataFrame(data)

def create_styled_graph(effect, categories):
    """Crea un gráfico de estilo para el diagrama de Ishikawa."""
    graph = graphviz.Digraph(
        graph_attr={
            'rankdir': 'LR',
            'splines': 'ortho',
            'nodesep': '0.5',
            'ranksep': '2',
            'fontname': 'Arial',
            'bgcolor': 'white'
        }
    )
    
    colors = {
        "Métodos": "#FF9999",
        "Maquinaria": "#99FF99",
        "Mano de obra": "#9999FF",
        "Materiales": "#FFFF99",
        "Medio Ambiente": "#FF99FF"
    }
    
    # Nodo principal del efecto
    graph.node('effect', 
        effect, 
        shape='box',
        style='filled',
        fillcolor='#E6E6E6',
        fontname='Arial Bold',
        fontsize='14'
    )
    
    # Agregar categorías y causas
    for category, causes in categories.items():
        if causes:
            cat_id = f"cat_{category}"
            graph.node(cat_id, 
                category,
                shape='box',
                style='filled',
                fillcolor=colors[category],
                fontname='Arial',
                fontsize='12'
            )
            graph.edge(cat_id, 'effect',
                penwidth='2.0',
                color=colors[category]
            )
            
            for i, cause_data in enumerate(causes):
                cause_id = f"{category}cause{i}"
                graph.node(cause_id,
                    cause_data['cause'],
                    shape='oval',
                    style='filled',
                    fillcolor=f"{colors[category]}80",
                    fontname='Arial',
                    fontsize='10'
                )
                graph.edge(cause_id, cat_id,
                    penwidth='1.5',
                    color=f"{colors[category]}80"
                )
                
                for j, why in enumerate(cause_data['whys']):
                    why_id = f"{cause_id}why{j}"
                    graph.node(why_id,
                        why,
                        shape='oval',
                        style='filled',
                        fillcolor=f"{colors[category]}40",
                        fontname='Arial',
                        fontsize='9'
                    )
                    graph.edge(why_id, cause_id,
                        penwidth='1.0',
                        color=f"{colors[category]}60"
                    )
    return graph

def ishikawa_page():
    """Función principal de la página de Ishikawa."""
    st.title("Diagrama de Ishikawa (Causa y Efecto)")
    st.write("### Funciones del Diagrama de Ishikawa")
    st.write("""
    - *Identificación de Causas*: Ayuda a identificar las diversas causas que contribuyen a un problema específico.
    - *Visualización*: Proporciona una representación gráfica clara de las relaciones entre el efecto y sus causas.
    - *Análisis de Problemas*: Permite analizar las causas raíz de un problema.
    - *Organización de Ideas*: Facilita la lluvia de ideas y la discusión en grupo.
    - *Mejora Continua*: Identifica áreas de mejora en productos, servicios o procesos.
    """)
    
    st.write("### Componentes del Diagrama de Ishikawa")
    st.write("""
    - *Efecto (Problema)*: Representa el problema que se está analizando.
    - *Categorías de Causas*: Agrupadas en categorías como Métodos, Maquinaria, Mano de obra, Materiales y Medio Ambiente.
    """)

    initialize_session_state()
    
    input_tab, diagram_tab, summary_tab = st.tabs(["📝 Entrada", "📊 Diagrama", "📋 Resumen"])
    
    with input_tab:
        st.session_state.effect = st.text_input("Problema o Efecto Principal:", 
                                              value=st.session_state.effect)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_category = st.selectbox("Seleccione Categoría:", 
                list(st.session_state.causes_data.keys()))
        
        with col2:
            new_cause = st.text_input(f"Nueva causa para {selected_category}:")
            if new_cause:
                whys = []
                st.write("5 Por qués:")
                for i in range(5):
                    why = st.text_input(f"¿Por qué? {i+1}", key=f"why_{i}")
                    if why:  
                        whys.append(why)
                if st.button("Agregar Causa"):
                    add_cause_to_category(selected_category, new_cause, whys)
                    st.success(f"Causa agregada a {selected_category}")
    
    with diagram_tab:
        if st.button("Generar Diagrama"):
            if st.session_state.effect:
                try:
                    graph = create_styled_graph(st.session_state.effect, 
                                             st.session_state.causes_data)
                    st.graphviz_chart(graph)
                except Exception as e:
                    st.error(f"Error al generar el diagrama: {str(e)}")
            else:
                st.warning("Por favor, ingrese el problema o efecto principal")
    
    with summary_tab:
        df = create_summary_table()
        if not df.empty:
            st.write("Resumen de Causas y Efectos")
            category_filter = st.multiselect(
                "Filtrar por Categoría:",
                options=st.session_state.causes_data.keys()
            )
            
            if category_filter:
                filtered_df = df[df['Categoría'].isin(category_filter)]
            else:
                filtered_df = df
                
            st.dataframe(filtered_df)
            
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Descargar Resumen (CSV)",
                csv,
                "resumen_ishikawa.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("No hay datos para mostrar en el resumen")

if __name__ == "__main__":
    st.set_page_config(page_title="Diagrama de Ishikawa", layout="wide")
    ishikawa_page()