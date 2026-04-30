import streamlit as st
from database import verify_user

def login_sidebar():
    """Відображає форму авторизації в боковій панелі."""
    if "user" in st.session_state:
        st.sidebar.success(f"Ви ввійшли як {st.session_state['user']}")
        if st.sidebar.button("Вийти"):
            del st.session_state["user"]
            st.rerun()
        return st.session_state["user"]
        
    st.sidebar.header("Авторизація")
    username = st.sidebar.text_input("Користувач")
    password = st.sidebar.text_input("Пароль", type="password")
    
    if st.sidebar.button("Увійти"):
        if verify_user(username, password):
            from database import get_user_info
            st.session_state["user"] = username
            st.session_state["full_name"] = get_user_info(username)
            st.rerun()
        else:
            st.sidebar.error("Невірний логін або пароль")
            
    return None
