import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

def data_upload_page():
    st.title("📝 Carga y Análisis de Datos")
    
    # Sección de carga de archivo
    st.header("Cargar Archivo de Datos")
    uploaded_file = st.file_uploader(
        "Selecciona un archivo CSV o Excel", 
        type=['csv', 'xlsx']
    )
    
    if uploaded_file is not None:
        # Leer el archivo
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Almacenar DataFrame en sesión
            st.session_state['uploaded_data'] = df
            
            # Pestañas de análisis
            tab1, tab2, tab3, tab4 = st.tabs([
                "Previsualización", 
                "Análisis Descriptivo", 
                "Valores Faltantes", 
                "Conversión de Variables"
            ])
            
            with tab1:
                st.subheader("Previsualización de Datos")
                st.dataframe(df.head(10))
                
                # Información básica del dataset
                st.subheader("Información del Dataset")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Número de Filas", df.shape[0])
                with col2:
                    st.metric("Número de Columnas", df.shape[1])
                with col3:
                    st.metric("Tipos de Datos", len(df.dtypes.unique()))
            
            with tab2:
                st.subheader("Análisis Descriptivo")
                # Estadísticas descriptivas para variables numéricas
                desc_stats = df.describe()
                st.dataframe(desc_stats)
                
                # Gráficos de distribución
                st.subheader("Distribución de Variables Numéricas")
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                selected_col = st.selectbox("Selecciona una variable", numeric_cols)
                
                fig = px.histogram(df, x=selected_col, 
                                   title=f'Distribución de {selected_col}')
                st.plotly_chart(fig)
            
            with tab3:
                st.subheader("Análisis de Valores Faltantes")
                # Conteo de valores faltantes
                missing_data = df.isnull().sum()
                missing_percent = 100 * df.isnull().sum() / len(df)
                
                missing_df = pd.DataFrame({
                    'Valores Faltantes': missing_data,
                    'Porcentaje (%)': missing_percent
                })
                
                st.dataframe(missing_df)
                
                # Visualización de valores faltantes
                if missing_data.sum() > 0:
                    st.warning("Se encontraron valores faltantes en algunas columnas.")
                    
                    # Opciones de manejo de valores faltantes
                    handle_method = st.radio(
                        "Selecciona método para manejar valores faltantes:", 
                        ['Eliminar filas', 'Rellenar con promedio', 'Rellenar con mediana']
                    )
                    
                    if st.button("Aplicar método de manejo"):
                        if handle_method == 'Eliminar filas':
                            df_cleaned = df.dropna()
                        elif handle_method == 'Rellenar con promedio':
                            df_cleaned = df.fillna(df.mean())
                        else:
                            df_cleaned = df.fillna(df.median())
                        
                        st.success("Datos procesados exitosamente.")
                        st.dataframe(df_cleaned)
                else:
                    st.success("No se encontraron valores faltantes en el dataset.")
            
            with tab4:
                st.subheader("Conversión de Variables")
                
                # Selección de columna para conversión
                col_to_convert = st.selectbox(
                    "Selecciona columna para conversión", 
                    df.columns
                )
                
                # Tipo de conversión
                conversion_type = st.radio(
                    "Tipo de conversión", 
                    ['Numérico', 'Categórico', 'One-Hot Encoding']
                )
                
                if st.button("Convertir Variable"):
                    if conversion_type == 'Numérico':
                        try:
                            df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce')
                            st.success(f"Columna {col_to_convert} convertida a numérico")
                        except Exception as e:
                            st.error(f"Error en conversión: {e}")
                    
                    elif conversion_type == 'Categórico':
                        df[col_to_convert] = df[col_to_convert].astype('category')
                        st.success(f"Columna {col_to_convert} convertida a categórico")
                    
                    elif conversion_type == 'One-Hot Encoding':
                        df_encoded = pd.get_dummies(df, columns=[col_to_convert])
                        st.success(f"One-Hot Encoding aplicado a {col_to_convert}")
                        st.dataframe(df_encoded)
        
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

# Función para ser llamada desde main.py
def upload_data_page():
    data_upload_page()
