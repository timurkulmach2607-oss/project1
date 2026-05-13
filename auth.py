import streamlit as st
import uuid
from database import verify_user, get_user_info, set_session_token, get_user_by_token

def login_sidebar():
    """Відображає форму авторизації в боковій панелі."""
    
    # Відновлення сесії з URL (якщо вкладку оновили)
    if "user" not in st.session_state:
        if "token" in st.query_params:
            token = st.query_params["token"]
            db_user = get_user_by_token(token)
            if db_user:
                st.session_state["user"] = db_user
                st.session_state["full_name"] = get_user_info(db_user)

    if "user" in st.session_state:
        st.sidebar.success(f"Ви ввійшли як {st.session_state['user']}")
        return st.session_state["user"]
        
    st.sidebar.header("Авторизація")
    username = st.sidebar.text_input("Користувач")
    password = st.sidebar.text_input("Пароль", type="password")
    
    if st.sidebar.button("Увійти"):
        if verify_user(username, password):
            # Генеруємо унікальний токен для сесії
            new_token = str(uuid.uuid4())
            set_session_token(username, new_token)
            
            st.session_state["user"] = username
            st.session_state["full_name"] = get_user_info(username)
            st.query_params["token"] = new_token
            st.rerun()
        else:
            st.sidebar.error("Невірний логін або пароль")
            
    return None
