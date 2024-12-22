import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime
import os

def validate_login(username, password):
    users_file = 'data/users.csv'
    
    # Verificar si el archivo existe
    if not os.path.exists(users_file):
        return False, "Archivo de usuarios no encontrado"
    
    # Leer archivo de usuarios
    df = pd.read_csv(users_file)
    
    # Buscar usuario
    user = df[df['username'] == username]
    
    if user.empty:
        return False, "Usuario no encontrado"
    
    # Verificar contraseña
    stored_password = user['password_hash'].values[0]
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        # Actualizar último inicio de sesión
        df.loc[df['username'] == username, 'last_login'] = datetime.now().isoformat()
        df.to_csv(users_file, index=False)
        return True, "Inicio de sesión exitoso"
    
    return False, "Contraseña incorrecta"

def login_page():
    st.title("Iniciar Sesión")
    
    # Verificar si ya está logueado
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Formulario de login
    with st.form("login_form"):
        username = st.text_input("Nombre de Usuario")
        password = st.text_input("Contraseña", type="password")
        
        submit_button = st.form_submit_button("Iniciar Sesión")
        
        if submit_button:
            # Validar campos no vacíos
            if not username or not password:
                st.error("Por favor, complete todos los campos")
                return
            
            # Intentar iniciar sesión
            login_successful, message = validate_login(username, password)
            
            if login_successful:
                # Establecer estado de sesión
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                
                # Mostrar mensaje de éxito
                st.success(message)
                
                # Usar rerun() en lugar de experimental_rerun()
                st.rerun()
            else:
                # Mostrar error de inicio de sesión
                st.error(message)
    
    # Opción de registro
    st.markdown("¿No tienes una cuenta? [Regístrate aquí](/register)")

# Si se ejecuta directamente
if __name__ == "__main__":
    login_page()
