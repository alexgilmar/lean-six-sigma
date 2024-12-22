import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime
import os

def validate_username(username):
    # Validaciones de username
    if len(username) < 4:
        return False, "Username debe tener al menos 4 caracteres"
    if not username.isalnum():
        return False, "Username solo puede contener letras y números"
    return True, ""

def validate_email(email):
    # Validación básica de email
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Email inválido"
    return True, ""

def validate_password(password):
    # Validaciones de contraseña
    if len(password) < 8:
        return False, "Contraseña debe tener al menos 8 caracteres"
    if not any(char.isdigit() for char in password):
        return False, "Contraseña debe contener al menos un número"
    if not any(char.isupper() for char in password):
        return False, "Contraseña debe contener al menos una mayúscula"
    return True, ""

def user_exists(username, email):
    # Verificar si usuario o email ya existen
    users_file = 'data/users.csv'
    if not os.path.exists(users_file):
        return False
    
    df = pd.read_csv(users_file)
    return (
        username in df['username'].values or 
        email in df['email'].values
    )

def register_user(username, email, password):
    # Hash de contraseña
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Preparar datos de usuario
    user_data = pd.DataFrame({
        'username': [username],
        'email': [email],
        'password_hash': [hashed_password.decode('utf-8')],
        'created_at': [datetime.now().isoformat()],
        'last_login': [None]
    })
    
    # Guardar en CSV
    users_file = 'data/users.csv'
    
    # Crear archivo si no existe
    if not os.path.exists(users_file):
        df = pd.DataFrame(columns=['username', 'email', 'password_hash', 'created_at', 'last_login'])
        df.to_csv(users_file, index=False)
    
    # Leer y agregar nuevo usuario
    df = pd.read_csv(users_file)
    
    # Usar concat en lugar de append
    df = pd.concat([df, user_data], ignore_index=True)
    
    df.to_csv(users_file, index=False)

def register_page():
    st.title("Registro de Usuario")
    
    # Formulario de registro
    with st.form("registro_form"):
        username = st.text_input("Nombre de Usuario")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        confirm_password = st.text_input("Confirmar Contraseña", type="password")
        
        submit_button = st.form_submit_button("Registrarse")
        
        if submit_button:
            # Validaciones
            username_valid, username_error = validate_username(username)
            email_valid, email_error = validate_email(email)
            password_valid, password_error = validate_password(password)
            
            # Verificar coincidencia de contraseñas
            if password != confirm_password:
                st.error("Las contraseñas no coinciden")
                return
            
            # Validaciones
            if not (username_valid and email_valid and password_valid):
                if not username_valid:
                    st.error(username_error)
                if not email_valid:
                    st.error(email_error)
                if not password_valid:
                    st.error(password_error)
                return
            
            # Verificar existencia de usuario
            if user_exists(username, email):
                st.error("El usuario o email ya existe")
                return
            
            # Registro exitoso
            try:
                register_user(username, email, password)
                st.success("¡Registro exitoso! Ya puedes iniciar sesión.")
            except Exception as e:
                st.error(f"Error en el registro: {e}")

# Si se ejecuta directamente
if __name__ == "__main__":
    register_page()
