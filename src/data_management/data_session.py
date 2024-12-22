import streamlit as st
import pandas as pd

class DataSession:
    @staticmethod
    def set_dataframe(df):
        """Almacenar DataFrame en sesión de Streamlit"""
        st.session_state['shared_dataframe'] = df


    @staticmethod
    def get_dataframe():
        """Recuperar DataFrame de sesión de Streamlit"""
        return st.session_state.get('uploaded_data', None)
    
    # @staticmethod
    # def get_dataframe():
    #     """Recuperar DataFrame de sesión de Streamlit"""
    #     return st.session_state.get('shared_dataframe', None)
    
    @staticmethod
    def clear_dataframe():
        """Limpiar DataFrame de sesión"""
        if 'shared_dataframe' in st.session_state:
            del st.session_state['shared_dataframe']
