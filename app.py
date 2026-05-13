import streamlit as st
import pandas as pd
import os
from datetime import datetime
from database import init_db, get_connection, add_audit_log, get_all_assets, add_asset, get_audit_log, get_all_users, add_user, delete_user
from auth import login_sidebar
import utils
import plotly.express as px

st.set_page_config(
    page_title="Управління ІТ-активами", 
    page_icon="💻", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

LOGO_PATH = "logo.png"

def render_logo():
    # Додаємо CSS для естетичного відображення логотипа
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stImage"] {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stImage"] > div {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            border-radius: 12px;
            padding: 16px !important;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 0 !important;
            display: block !important;
            vertical-align: top !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    else:
        st.sidebar.markdown("### [Корпоративний Логотип]")

def main():
    init_db()
    render_logo()
    
    user = login_sidebar()
    if not user:
        st.warning("Будь ласка, авторизуйтесь для доступу до системи.")
        return

    st.title("Система обліку ІТ-активів")
    
    # --- Естетична верхня полоска ---
    st.markdown("""
    <style>
    .top-stripe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: #4A6274;
        z-index: 999999;
    }
    /* Додатковий відступ для основного контенту */
    .main .block-container {
        padding-top: 3.5rem !important;
    }
    /* --- Базові світлі стилі --- */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Чиста стилізація блоків */
    [data-testid="stDataEditor"], [data-testid="stDataFrame"], [data-testid="stTable"], 
    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #F1F3F5 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
    }
    
    /* Світлий сайдбар */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #F1F3F5 !important;
    }
    
    /* Кнопки */
    .stButton > button, .stDownloadButton > button {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #64748B !important;
    }
    
    /* Акцентні кнопки */
    button[kind="primary"], 
    button[data-testid="stBaseButton-primary"],
    [data-testid="stFormSubmitButton"] button {
        background-color: #64748B !important;
        border-color: #64748B !important;
        color: white !important;
    }
    
    /* Фото активів */
    .stMainBlockContainer [data-testid="stImage"] img {
        border: 1px solid #F1F3F5 !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Вертикальна навігація у сайдбарі ---
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .nav-btn button {
        width: 100% !important;
        text-align: left !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        border: 1px solid transparent !important;
        background-color: transparent !important;
        color: #31333F !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stSidebar"] .nav-btn button:hover {
        background-color: rgba(74, 98, 116, 0.05) !important;
        border-color: rgba(74, 98, 116, 0.2) !important;
    }
    div[data-testid="stSidebar"] .nav-btn-active button {
        background-color: rgba(74, 98, 116, 0.1) !important;
        color: #4A6274 !important;
        border-color: #4A6274 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stSidebar"] .nav-btn {
        margin-bottom: 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    pages = [
        (":material/dashboard:", "Дашборд"),
        (":material/add_circle:", "Реєстрація активів"),
        (":material/manage_search:", "Операції з активом"),
        (":material/qr_code_2:", "Генерація QR-кодів та штрихкодів"),
        (":material/history:", "Журнал аудиту"),
        (":material/settings:", "Налаштування"),
    ]

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Дашборд"

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### Навігація")
    for icon, name in pages:
        is_active = st.session_state.active_page == name
        css_class = "nav-btn-active nav-btn" if is_active else "nav-btn"
        with st.sidebar:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(name, icon=icon, key=f"nav_{name}", use_container_width=True):
                st.session_state.active_page = name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    page = st.session_state.active_page

    if page == "Дашборд":
        render_dashboard(user)
    elif page == "Реєстрація активів":
        render_registration(user)
    elif page == "Операції з активом":
        render_scanning(user)
    elif page == "Генерація QR-кодів та штрихкодів":
        render_print_station()
    elif page == "Журнал аудиту":
        render_audit_log()
    elif page == "Налаштування":
        render_settings(user)

    # --- Кнопка Вийти внизу сайдбару ---
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .logout-btn {
        margin-top: 15px;
        width: 100%;
    }
    div[data-testid="stSidebar"] .logout-btn button {
        width: 100% !important;
        background-color: transparent !important;
        border: 1px solid rgba(220, 50, 50, 0.4) !important;
        color: #e53e3e !important;
        border-radius: 6px !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stSidebar"] .logout-btn button:hover {
        background-color: rgba(220, 50, 50, 0.1) !important;
        border-color: #e53e3e !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        
        if not st.session_state.get("confirm_logout", False):
            if st.button("Вийти з системи", icon=":material/logout:", key="logout_btn", use_container_width=True):
                st.session_state.confirm_logout = True
                st.rerun()
        else:
            st.warning("Ви дійсно хочете вийти?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Так", icon=":material/check:", key="logout_yes", use_container_width=True, type="primary"):
                    from database import set_session_token
                    set_session_token(st.session_state["user"], None)
                    if "token" in st.query_params:
                        del st.query_params["token"]
                    del st.session_state["user"]
                    if "full_name" in st.session_state:
                        del st.session_state["full_name"]
                    st.session_state.confirm_logout = False
                    st.rerun()
            with col2:
                if st.button("Скасувати", icon=":material/close:", key="logout_no", use_container_width=True):
                    st.session_state.confirm_logout = False
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")

        # Attribution at the very end
        st.markdown("""
        <div style="margin-top: 30px; text-align: center; color: rgba(128,128,128,0.7); font-size: 15px; font-style: italic; font-weight: 500; line-height: 1.3;">
            Directed by<br>
            <span style="font-size: 16px; font-weight: 600;">Tymur Kulmach and Anatolii Novyk</span>
        </div>
        """, unsafe_allow_html=True)


def render_dashboard(username):
    st.header("Візуальна аналітика та Дашборд")
    
    df = get_all_assets()
    
    if df.empty:
        st.info("Немає активів для відображення.")
        return

    # Фільтруємо лише офіційно списані товари (Scrapped)
    df_active = df[df['status'] != 'Списано (Scrapped)']

    col1, col2, col3 = st.columns(3)
    
    total_assets = df_active['quantity'].sum()
    in_stock = df_active[df_active['status'] == 'В наявності (In Stock)']['quantity'].sum()
    in_use = df_active[df_active['status'] == 'У використанні (In Use)']['quantity'].sum()
    
    col1.metric("Всього активів", int(total_assets))
    col2.metric("В наявності", int(in_stock))
    col3.metric("У використанні", int(in_use))
    
    st.markdown("---")
    col_chart1, col_chart2 = st.columns([1, 1], gap="small")
    with col_chart1:
        st.subheader("Розподіл за статусами")
        status_counts = df_active.groupby('status')['quantity'].sum().reset_index()
        status_counts.columns = ['Статус', 'Кількість']
        
        # Визначаємо кольори для статусів
        status_colors = {
            'В наявності (In Stock)': '#2D3E4B',
            'У використанні (In Use)': '#808080',
            'Обслуговування (Maintenance)': '#A65A5F'
        }
        
        # Очищуємо назви для графіку (прибираємо текст у дужках для краси)
        status_counts['DisplayLabel'] = status_counts['Статус'].apply(lambda x: x.split(' (')[0] if ' (' in x else x)
        
        fig_status = px.pie(
            status_counts, 
            names='DisplayLabel', 
            values='Кількість', 
            hole=0.5,
            color='Статус',
            color_discrete_map=status_colors
        )
        
        fig_status.update_traces(
            textinfo='percent+label',
            textposition='outside',
            textfont_size=14,
            marker=dict(line=dict(color='#FFFFFF', width=8)), # Широка біла межа для ефекту розділення без зміщення
            rotation=90
        )
        
        fig_status.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col_chart2:
        st.subheader("Кількість за категоріями")
        cat_counts = df_active.groupby('category')['quantity'].sum().reset_index()
        cat_counts.columns = ['Категорія', 'Кількість']
        cat_counts = cat_counts.sort_values(by='Кількість', ascending=False)
        
        fig_cat = px.bar(cat_counts, x='Категорія', y='Кількість')
        
        cycle_colors = ['#A65A5F', '#808080', '#2D3E4B']
        border_colors = [cycle_colors[i % len(cycle_colors)] for i in range(len(cat_counts))]
        
        fig_cat.update_traces(
            marker_color='rgba(0,0,0,0)',
            marker_line_color=border_colors,
            marker_line_width=5 
        )
        
        fig_cat.update_layout(
            margin=dict(l=20, r=20, t=20, b=120),
            height=350,
            bargap=0.15, # Зменшуємо відстань між стовпцями, щоб вони були ближче один до одного
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=True, zerolinecolor='#D1D9E0', zerolinewidth=1),
            yaxis=dict(showgrid=False, showticklabels=True),
            showlegend=False
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")
    st.subheader("Фільтрація та Список активів")
    
    df['main_cat'] = df['category'].apply(lambda x: x.split(' - ')[0] if isinstance(x, str) else x)
    
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    with col_f1:
        f_category = st.selectbox("Категорія", ["Всі"] + sorted(list(df['main_cat'].dropna().unique())))
        
    f_subcategory = "Всі"
    with col_f2:
        if f_category == "Принтер":
            subcats = ["Всі", "Пристрої (Принтери)", "Тонер (Toner)", "Барабан (Drum unit)", "Контейнер відходів (Waste toner container)"]
            f_subcategory = st.selectbox("Підкатегорія", subcats)
            
    with col_f3:
        f_status = st.selectbox("Статус", ["Всі"] + list(df['status'].unique()))
    with col_f4:
        f_search = st.text_input("Пошук (Бренд, Модель, SN, ПІБ)")
    with col_f5:
        # Checkbox is vertically centered using some top padding
        st.write("")
        st.write("")
        hide_scrapped = st.checkbox("Приховати списані", value=True)

    filtered_df = df.copy()
    if hide_scrapped:
        filtered_df = filtered_df[filtered_df['status'] != 'Списано (Scrapped)']
    
    if f_category != "Всі":
        if f_category == "Принтер":
            if f_subcategory == "Всі":
                filtered_df = filtered_df[filtered_df['main_cat'] == 'Принтер']
            elif f_subcategory == "Пристрої (Принтери)":
                filtered_df = filtered_df[filtered_df['category'] == 'Принтер']
            else:
                filtered_df = filtered_df[filtered_df['category'] == f"Принтер - {f_subcategory}"]
        else:
            filtered_df = filtered_df[filtered_df['main_cat'] == f_category]
            
    if f_status != "Всі":
        filtered_df = filtered_df[filtered_df['status'] == f_status]
    if f_search:
        f_search_lower = f_search.lower()
        # Handle NaN values explicitly before str operations
        filtered_df = filtered_df.fillna('')
        filtered_df = filtered_df[
            filtered_df['brand'].astype(str).str.lower().str.contains(f_search_lower) |
            filtered_df['model'].astype(str).str.lower().str.contains(f_search_lower) |
            filtered_df['serial_number'].astype(str).str.lower().str.contains(f_search_lower) |
            filtered_df['assigned_to'].astype(str).str.lower().str.contains(f_search_lower)
        ]
        
    filtered_df = filtered_df.drop(columns=['main_cat'], errors='ignore')
    
    # Робимо порядкові номери послідовними (1, 2, 3...) незалежно від ID
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1
    
    st.download_button(
        label="Експортувати список в CSV",
        icon=":material/download:",
        data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
        file_name='it_assets_export.csv',
        mime='text/csv'
    )
    
    st.caption("Ви можете редагувати статус або опис активу безпосередньо в таблиці.")
    
    disabled_cols = ["id", "category", "brand", "model", "serial_number", "part_number", "barcode_data"]
    
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        disabled=disabled_cols,
        key="asset_editor"
    )
    
    if st.button("Зберегти зміни"):
        changes_made = False
        logs_to_add = []
        conn = get_connection()
        cursor = conn.cursor()
        
        ALLOWED_EDIT_COLS = ['status', 'assigned_to', 'description', 'quantity']
        
        for index, row in edited_df.iterrows():
            orig_row = df.loc[index]
            if not row.equals(orig_row):
                asset_id = int(row['id'])
                for col in edited_df.columns:
                    if col in ALLOWED_EDIT_COLS and str(row[col]) != str(orig_row[col]):
                        val = row[col]
                        if col == 'quantity':
                            try:
                                val = int(val)
                            except ValueError:
                                val = int(orig_row[col])
                                
                            if val <= 0:
                                val = 0
                                cursor.execute(f"UPDATE assets SET quantity = ?, status = 'Списано (Scrapped)' WHERE id = ?", (val, asset_id))
                                logs_to_add.append(("Списання", f"Актив ID {asset_id}: кількість досягла 0, статус змінено на 'Списано (Scrapped)'"))
                            else:
                                cursor.execute(f"UPDATE assets SET quantity = ? WHERE id = ?", (val, asset_id))
                                logs_to_add.append(("Оновлення", f"Актив ID {asset_id}: змінено кількість з '{orig_row[col]}' на '{val}'"))
                        else:
                            cursor.execute(f"UPDATE assets SET {col} = ? WHERE id = ?", (str(val), asset_id))
                            logs_to_add.append(("Оновлення", f"Актив ID {asset_id}: змінено {col} з '{orig_row[col]}' на '{row[col]}'"))
                            
                        changes_made = True
                        
        if changes_made:
            conn.commit()
            conn.close()
            for action, details in logs_to_add:
                add_audit_log(username, action, details)
            # Очищуємо кеш актів, щоб вони перегенерувалися з новими даними
            st.session_state.pop('docx_cache', None)
            st.success("Зміни успішно збережено!")
            st.rerun()
        else:
            conn.close()
            st.info("Немає змін для збереження.")

def render_registration(username):
    st.header("Реєстрація нового активу")
    
    def reset_upc():
        keys_to_clear = ["upc_brand", "upc_model", "upc_category", "upc_subcategory", "upc_title", "upc_desc", "upc_code", "upc_search"]
        for key in keys_to_clear:
            if key in st.session_state:
                st.session_state[key] = ""
                
    st.subheader("Автозаповнення за штрихкодом (UPC/EAN)")
    col_upc, col_btn = st.columns([3, 1])
    with col_upc:
        upc_input = st.text_input("Відскануйте або введіть заводський штрихкод", key="upc_search")
    with col_btn:
        st.write("")
        st.write("")
        if st.button("Знайти в UPCitemdb", icon=":material/search:", use_container_width=True):
            if upc_input:
                try:
                    import requests
                    resp = requests.get(f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc_input}")
                    data = resp.json()
                    if data.get("code") == "OK" and data.get("items"):
                        import re
                        item = data["items"][0]
                        brand_val = item.get("brand", "")
                        st.session_state.upc_brand = brand_val
                        
                        model_val = item.get("model", "")
                        title_val = item.get("title", "")
                        # UPCitemdb title is usually much more accurate than the model field
                        raw_model = title_val if title_val else model_val
                        
                        if brand_val and raw_model.lower().startswith(brand_val.lower()):
                            raw_model = re.sub(rf'(?i)^{re.escape(brand_val)}\s*', '', raw_model).strip()
                            raw_model = re.sub(r'^-\s*', '', raw_model).strip()
                            
                        st.session_state.upc_title = title_val
                        st.session_state.upc_desc = "" # Спеціально очищуємо, щоб не тягнути SEO спам з магазинів
                        st.session_state.upc_code = upc_input
                        
                        # Guess category
                        cat_str = (item.get("category", "") + " " + title_val).lower()
                        guessed_cat = "Інше"
                        guessed_sub = None
                        
                        if "toner" in cat_str or "cartridge" in cat_str or "ink" in cat_str or "тонер" in cat_str or "c-exv" in cat_str:
                            guessed_cat = "Принтер"
                            guessed_sub = "Тонер (Toner)"
                        elif "drum" in cat_str or "барабан" in cat_str:
                            guessed_cat = "Принтер"
                            guessed_sub = "Барабан (Drum unit)"
                        elif "waste" in cat_str and ("toner" in cat_str or "container" in cat_str):
                            guessed_cat = "Принтер"
                            guessed_sub = "Контейнер відходів (Waste toner container)"
                        elif "printer" in cat_str or "принтер" in cat_str:
                            guessed_cat = "Принтер"
                            guessed_sub = "Принтер (Пристрій)"
                        elif "monitor" in cat_str or "display" in cat_str or "монітор" in cat_str:
                            guessed_cat = "Монітор"
                        elif "mouse" in cat_str or "мишка" in cat_str:
                            guessed_cat = "Мишка"
                        elif "headset" in cat_str or "headphones" in cat_str or "гарнітура" in cat_str:
                            guessed_cat = "Гарнітура"
                        elif "laptop" in cat_str or "notebook" in cat_str or "ноутбук" in cat_str:
                            guessed_cat = "Ноутбук"
                        elif "pc" in cat_str or "desktop" in cat_str or "пк" in cat_str:
                            guessed_cat = "ПК"
                        elif "switch" in cat_str or "router" in cat_str or "мережеве" in cat_str:
                            guessed_cat = "Мережеве обладнання"
                        elif "powerbank" in cat_str or "power bank" in cat_str or "павербанк" in cat_str or "battery" in cat_str or "mah" in cat_str or "powercore" in cat_str:
                            guessed_cat = "Павербанк"

                        # Розумний пошук моделі
                        raw_lower = raw_model.lower()
                        if guessed_sub == "Барабан (Drum unit)":
                            if "034" in raw_lower:
                                raw_model = "Drum Unit 034 Black"
                            elif "49" in raw_lower:
                                raw_model = "C-EXV 49 Drum Unit"
                        elif guessed_sub == "Тонер (Toner)":
                            if "47" in raw_lower:
                                if "cyan" in raw_lower or "синій" in raw_lower: raw_model = "C-EXV 47 (Toner Cyan)"
                                elif "magenta" in raw_lower or "малиновий" in raw_lower: raw_model = "C-EXV 47 (Toner Magenta)"
                                elif "yellow" in raw_lower or "жовтий" in raw_lower: raw_model = "C-EXV 47 (Toner Yellow)"
                                else: raw_model = "C-EXV 47 (Toner Black)"
                            elif "49" in raw_lower:
                                if "cyan" in raw_lower or "синій" in raw_lower: raw_model = "C-EXV 49 (Toner Cyan)"
                                elif "magenta" in raw_lower or "малиновий" in raw_lower: raw_model = "C-EXV 49 (Toner Magenta)"
                                elif "yellow" in raw_lower or "жовтий" in raw_lower: raw_model = "C-EXV 49 (Toner Yellow)"
                                else: raw_model = "C-EXV 49 (Toner Black)"
                                
                        st.session_state.upc_model = raw_model
                        st.session_state.upc_category = guessed_cat
                        if guessed_sub:
                            st.session_state.upc_subcategory = guessed_sub
                            
                        st.success("Товар знайдено! Дані та Категорію підставлено у форму нижче.")
                    else:
                        st.warning("Товар не знайдено в базі UPCitemdb.")
                except Exception as e:
                    st.error(f"Помилка API: {e}")
            else:
                st.warning("Введіть штрихкод.")
    st.markdown("---")
    
    col_cat, col_sub = st.columns(2)
    
    categories = ["Ноутбук", "ПК", "Принтер", "Монітор", "Мережеве обладнання", "Мишка", "Гарнітура", "Павербанк", "Інше"]
    upc_cat = st.session_state.get("upc_category", "Ноутбук")
    cat_idx = categories.index(upc_cat) if upc_cat in categories else 0
    
    with col_cat:
        category = st.selectbox("Категорія", categories, index=cat_idx, on_change=reset_upc)
    with col_sub:
        subcategory = None
        if category == "Принтер":
            subcats = ["Принтер (Пристрій)", "Тонер (Toner)", "Барабан (Drum unit)", "Контейнер відходів (Waste toner container)"]
            upc_sub = st.session_state.get("upc_subcategory", "Принтер (Пристрій)")
            sub_idx = subcats.index(upc_sub) if upc_sub in subcats else 0
            subcategory = st.selectbox("Підкатегорія принтера", subcats, index=sub_idx, on_change=reset_upc)
            
    col_brand, col_model = st.columns(2)
    
    def get_idx(options, val):
        if not val: return 0
        val_lower = val.lower()
        for i, opt in enumerate(options):
            if opt.lower() == val_lower:
                return i
        return len(options) - 1

    df_assets = get_all_assets()

    with col_brand:
        upc_b = st.session_state.get('upc_brand', '')
        db_brands = []
        if not df_assets.empty:
            db_brands = df_assets[df_assets['category'].str.startswith(category, na=False)]['brand'].dropna().unique().tolist()
            
        default_brands = []
        if category == "Принтер": default_brands = ["HP"]
        elif category == "Ноутбук": default_brands = ["HP", "Lenovo"]
        
        opts_brand = sorted(list(set(default_brands + db_brands))) + ["Інший (ввести вручну)"]
        brand_sel = st.selectbox("Бренд", opts_brand, index=get_idx(opts_brand, upc_b), on_change=reset_upc)
        
        if brand_sel == "Інший (ввести вручну)":
            brand = st.text_input("Введіть бренд вручну", value=upc_b)
        else:
            brand = brand_sel
            
    with col_model:
        upc_m = st.session_state.get('upc_model', '')
        
        final_category_for_db = category
        if category == "Принтер" and subcategory and subcategory != "Принтер (Пристрій)":
            final_category_for_db = f"Принтер - {subcategory}"
            
        db_models = []
        if not df_assets.empty:
            db_models = df_assets[df_assets['category'] == final_category_for_db]['model'].dropna().unique().tolist()
            
        default_models = []
        if category == "Принтер" and subcategory == "Принтер (Пристрій)":
            default_models = []
        elif category == "Принтер" and subcategory == "Тонер (Toner)":
            default_models = []
        elif category == "Принтер" and subcategory == "Барабан (Drum unit)":
            default_models = []
        elif category == "Принтер" and subcategory == "Контейнер відходів (Waste toner container)":
            default_models = []
            
        opts_model = sorted(list(set(default_models + db_models))) + ["Інша (ввести вручну)"]
        model_sel = st.selectbox("Модель", opts_model, index=get_idx(opts_model, upc_m), on_change=reset_upc)
        
        if model_sel == "Інша (ввести вручну)":
            model = st.text_input("Введіть модель вручну", value=upc_m)
        else:
            model = model_sel
            
    # Пошук існуючого фото для цієї моделі
    existing_model_photo = None
    if not df_assets.empty and model:
        # Шукаємо будь-який актив з такою ж моделлю, де є фото
        model_match = df_assets[(df_assets['model'] == model) & (df_assets['photo_path'].notna()) & (df_assets['photo_path'] != '')]
        if not model_match.empty:
            existing_model_photo = model_match.iloc[0]['photo_path']
            
    with st.form("registration_form", clear_on_submit=False):
        st.subheader("Деталі активу")
        
        col_sn, col_pn = st.columns(2)
        with col_sn:
            serial_number = st.text_input("Серійний номер (S/N)", placeholder="Введіть S/N")
        with col_pn:
            part_number = st.text_input("Парт-номер (P/N)", placeholder="Введіть P/N або залиште порожнім")
            
        description = st.text_area("Додатковий опис / Примітка", placeholder="Наприклад: Новий, у коробці")
        
        col_qty, col_upc2 = st.columns(2)
        with col_qty:
            quantity = st.number_input("Кількість (шт.)", min_value=1, value=1)
        with col_upc2:
            upc_code = st.text_input("Заводський штрихкод (UPC/EAN)", value=st.session_state.get('upc_code', ''))
            
        st.markdown("---")
        uploaded_file = st.file_uploader("Завантажити фото активу", type=["png", "jpg", "jpeg"])
        
        submit_button = st.form_submit_button("Зареєструвати актив", icon=":material/add_circle:", type="secondary", use_container_width=True)
        
        if submit_button:
            if not brand or not model:
                st.error("Заповніть поля Бренд та Модель.")
            else:
                success_all = True
                error_msg = ""
                
                for i in range(int(quantity)):
                    import uuid
                    import re
                    
                    current_serial = serial_number.strip()
                    
                    if not current_serial:
                        current_serial = f"GEN-{str(uuid.uuid4())[:8].upper()}"
                    elif int(quantity) > 1:
                        current_serial = f"{current_serial}-{i+1}"
                        
                    prefixes = {"Ноутбук": "LAP", "ПК": "PC", "Принтер": "PRN", "Монітор": "MON", "Мережеве обладнання": "NET", "Мишка": "MOU", "Гарнітура": "HST", "Павербанк": "PWR", "Інше": "OTH"}
                    prefix = prefixes.get(category, "AST")
                    
                    final_category = category
                    if category == "Принтер" and subcategory and subcategory != "Принтер (Пристрій)":
                        final_category = f"Принтер - {subcategory}"
                    
                    photo_path = None
                    if uploaded_file is not None:
                        os.makedirs("uploads", exist_ok=True)
                        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '', uploaded_file.name)
                        if not safe_name: safe_name = "photo.jpg"
                        photo_path = os.path.join("uploads", f"{current_serial}_{safe_name}")
                        with open(photo_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    elif existing_model_photo:
                        photo_path = existing_model_photo
                    
                    barcode_data = f"{prefix}-{current_serial}"
                    
                    asset_data = {
                        "category": final_category,
                        "brand": brand,
                        "model": model,
                        "serial_number": current_serial,
                        "part_number": part_number,
                        "description": description,
                        "status": "В наявності (In Stock)",
                        "barcode_data": barcode_data,
                        "assigned_to": "Не призначено",
                        "photo_path": photo_path,
                        "quantity": 1,
                        "upc": upc_code
                    }
                    
                    success, msg = add_asset(asset_data, username)
                    if not success:
                        success_all = False
                        error_msg = msg
                        break
                
                if success_all:
                    st.success(f"Успішно додано {quantity} одиниць!")
                else:
                    st.error(error_msg)

    st.markdown("---")
    st.subheader("Масовий імпорт через CSV")
    st.caption("Файл повинен містити наступні стовпці: `category`, `brand`, `model`, `serial_number`, `part_number`, `description`, `status`")
    
    uploaded_csv = st.file_uploader("Завантажте CSV файл", type=["csv"])
    if uploaded_csv is not None:
        if st.button("Імпортувати дані"):
            try:
                import uuid
                df_import = pd.read_csv(uploaded_csv).fillna('')
                
                required_columns = {"category", "brand", "model", "serial_number", "status"}
                if not required_columns.issubset(df_import.columns):
                    st.error(f"Файл не містить всіх обов'язкових стовпців. Знайдено: {list(df_import.columns)}")
                else:
                    success_count = 0
                    error_count = 0
                    for _, row in df_import.iterrows():
                        category = str(row['category'])
                        serial_number = str(row['serial_number']).strip()
                        if not serial_number:
                            serial_number = f"GEN-{str(uuid.uuid4())[:8].upper()}"
                            
                        prefixes = {"Ноутбук": "LAP", "ПК": "PC", "Принтер": "PRN", "Монітор": "MON", "Мережеве обладнання": "NET", "Павербанк": "PWR", "Інше": "OTH"}
                        prefix = prefixes.get(category, "AST")
                        barcode_data = f"{prefix}-{serial_number}"
                        
                        asset_data = {
                            "category": category,
                            "brand": str(row['brand']),
                            "model": str(row['model']),
                            "serial_number": serial_number,
                            "part_number": str(row.get('part_number', '')),
                            "description": str(row.get('description', '')),
                            "status": str(row['status']),
                            "barcode_data": barcode_data,
                            "assigned_to": str(row.get('assigned_to', 'Не призначено'))
                        }
                        
                        success, _ = add_asset(asset_data, username)
                        if success:
                            success_count += 1
                        else:
                            error_count += 1
                            
                    if success_count > 0:
                        st.success(f"Успішно імпортовано {success_count} активів!")
                    if error_count > 0:
                        st.warning(f"Пропущено {error_count} активів (можливо, дублікати серійних номерів).")
            except Exception as e:
                st.error(f"Помилка при читанні файлу: {e}")

def render_scanning(username):
    st.header("Операції з активом")
    
    if 'action_success' in st.session_state:
        st.success(st.session_state.action_success)
        del st.session_state.action_success
        
    st.caption("Цей інпут підтримує USB сканери штрихкодів, які працюють як емулятори клавіатури.")
    
    scan_input = st.text_input("Відскануйте штрихкод або введіть серійний номер (через кому для кількох):", key="scanner_input")
    
    if scan_input:
        from database import get_assets_by_serial_or_barcode
        raw_codes = [c.strip() for c in scan_input.split(',') if c.strip()]
        codes = list(dict.fromkeys(raw_codes))
        
        assets = []
        missing_codes = []
        for code in codes:
            found_assets = get_assets_by_serial_or_barcode(code)
            if found_assets:
                assets.extend(found_assets)
            else:
                missing_codes.append(code)
                
        if missing_codes:
            st.error(f"Не знайдено активи з кодами: {', '.join(missing_codes)}")
            
        if assets:
            # Показуємо все крім офіційно списаних (Scrapped).
            # 'Використано (Used)' лишається видимим — його ще треба окремо списати.
            active_assets = [a for a in assets if a.get('status') != 'Списано (Scrapped)']
            scrapped_count = len(assets) - len(active_assets)
            
            if not active_assets:
                st.warning("Усі активи за цим кодом вже списані та знаходяться в архіві. Операції з ними неможливі.")
            else:
                if scrapped_count > 0:
                    st.markdown(f"""
                    <div style="background-color: rgba(28, 131, 225, 0.1); color: rgb(0, 66, 128); padding: 16px; border-radius: 0.5rem; margin-bottom: 1rem;">
                        Знайдено {scrapped_count} списаних одиниць у історії. Вони приховані, щоб ви бачили лише актуальні активи.
                    </div>
                    """, unsafe_allow_html=True)
                    
                assets = active_assets
                full_name = st.session_state.get('full_name', username)
                
                # Об'єднуємо результати та дії для стабільності (без st.fragment через помилки DOM)
                def render_full_scan_result(assets, username, full_name):
                    if len(assets) == 1:
                        asset = assets[0]
                        st.success(f"Актив знайдено: {asset['category']} {asset['brand']} {asset['model']}")
                        
                        col_info, col_img = st.columns([1.5, 1])
                        with col_info:
                            st.markdown(f"### {asset['brand']} {asset['model']}")
                            st.markdown(f":material/folder: **Категорія:** {asset['category']}")
                            st.markdown(f":material/barcode_scanner: **Серійний номер:** `{asset['serial_number']}`")
                            
                            # Кольоровий статус
                            status = asset['status']
                            st.markdown(f":material/info: **Статус:** {status}")
                            
                            st.markdown(f":material/person: **Призначено:** {asset['assigned_to']}")
                            if asset.get('upc'):
                                st.markdown(f":material/tag: **UPC/EAN:** `{asset['upc']}`")
                            if asset.get('description'):
                                st.markdown(f":material/description: **Опис:** {asset['description']}")
                                
                        with col_img:
                            photo_path = asset.get('photo_path')
                            if photo_path and os.path.exists(os.path.abspath(photo_path)):
                                st.image(os.path.abspath(photo_path), use_container_width=True)
                            else:
                                st.info("Фото пристрою відсутнє")
                        
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Штрихкод (Code128)**")
                            barcode_img = utils.generate_barcode(asset['barcode_data'])
                            st.image(barcode_img, width=300)
                            st.download_button("Завантажити Штрихкод", icon=":material/download:", data=barcode_img.getvalue(), file_name=f"barcode_{asset['serial_number']}.png", mime="image/png", key=f"dl_bar_{asset['id']}")
                        with col2:
                            st.markdown("**QR Код**")
                            qr_img = utils.generate_qr(asset['barcode_data'])
                            st.image(qr_img, width=200)
                            st.download_button("Завантажити QR", icon=":material/download:", data=qr_img.getvalue(), file_name=f"qr_{asset['serial_number']}.png", mime="image/png", key=f"dl_qr_{asset['id']}")
                    else:
                        st.success(f"Знайдено активів: {len(assets)}")
                        st.dataframe(pd.DataFrame(assets).drop(columns=['photo_path', 'barcode_data'], errors='ignore'))
                
                # Внутрішня функція для дій
                def render_actions_internal(assets, username, full_name):
                    st.markdown("---")
                    st.subheader("Документи та Дії")
                    assignees = list(set([a.get('assigned_to', 'Не призначено') for a in assets]))
                    assets_key = "_".join([str(a['id']) for a in assets])
                    
                    if 'docx_cache' not in st.session_state:
                        st.session_state.docx_cache = {}
                    
                    if len(assignees) == 1 and assignees[0] == 'Не призначено':
                        st.write("Всі відскановані активи знаходяться на складі (Не призначено).")
                        cache_id = f"act_issue_{assets_key}"
                        if cache_id not in st.session_state.docx_cache:
                            st.session_state.docx_cache[cache_id] = utils.generate_act_docx(assets, full_name)
                        
                        col_doc1, col_doc2 = st.columns(2)
                        with col_doc1:
                            st.download_button(f"Акт прийому-передачі (Видача {len(assets)} шт.)", icon=":material/description:", data=st.session_state.docx_cache[cache_id], file_name=f"Акт_видачі_{len(assets)}_шт.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_act_issue_{assets_key}")
                        with col_doc2:
                            with st.expander(f"Видати співробітнику ({len(assets)} шт.)", icon=":material/ios_share:"):
                                with st.form(key=f"form_issue_{assets_key}"):
                                    new_assignee = st.text_input("ПІБ співробітника:")
                                    new_status = st.selectbox("Новий статус", ["У використанні (In Use)", "Обслуговування (Maintenance)"])
                                    if st.form_submit_button("Зберегти видачу"):
                                        if new_assignee.strip():
                                            conn = get_connection()
                                            cursor = conn.cursor()
                                            ids = [a['id'] for a in assets]
                                            placeholders = ','.join(['?']*len(ids))
                                            cursor.execute(f"UPDATE assets SET status = ?, assigned_to = ? WHERE id IN ({placeholders})", [new_status, new_assignee.strip()] + ids)
                                            conn.commit()
                                            conn.close()
                                            st.session_state.docx_cache = {}
                                            add_audit_log(username, "Видача", f"Масова видача {len(assets)} активів співробітнику {new_assignee.strip()}")
                                            st.session_state.action_success = "Активи успішно видано!"
                                            st.rerun()
                                        else:
                                            st.error("Будь ласка, введіть ПІБ.")
                                
                                st.write("---")
                                if st.button(f"Встановити 'У використанні' (без ПІБ)", icon=":material/settings:", key=f"btn_general_use_{assets_key}", use_container_width=True):
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        ids = [a['id'] for a in assets]
                                        placeholders = ','.join(['?']*len(ids))
                                        cursor.execute(f"UPDATE assets SET status = 'У використанні (In Use)', assigned_to = 'Загальне використання' WHERE id IN ({placeholders})", ids)
                                        conn.commit()
                                        conn.close()
                                        st.session_state.docx_cache = {}
                                        add_audit_log(username, "Використання", f"Масове переведення {len(assets)} активів у статус 'У використанні' (без ПІБ)")
                                        st.session_state.action_success = "Статус оновлено на 'У використанні'!"
                                        st.rerun()
                    elif len(assignees) == 1 and assignees[0] != 'Не призначено':
                        assigned_to = assignees[0]
                        st.write(f"Всі відскановані активи закріплено за: **{assigned_to}**")
                        cache_id = f"act_assign_{assets_key}"
                        if cache_id not in st.session_state.docx_cache:
                            st.session_state.docx_cache[cache_id] = utils.generate_act_docx(assets, full_name)
                        return_cache_id = f"act_return_{assets_key}"
                        if return_cache_id not in st.session_state.docx_cache:
                            st.session_state.docx_cache[return_cache_id] = utils.generate_return_act_docx(assets, assigned_to, full_name)
                        
                        col_doc1, col_doc2 = st.columns(2)
                        with col_doc1:
                            st.download_button(f"Акт прийому-передачі (Видача {len(assets)} шт.)", icon=":material/description:", data=st.session_state.docx_cache[cache_id], file_name=f"Акт_видачі_{len(assets)}_шт.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_act_assigned_{assets_key}")
                            st.download_button(f"Акт повернення (Повернення {len(assets)} шт.)", icon=":material/history_edu:", data=st.session_state.docx_cache[return_cache_id], file_name=f"Акт_повернення_{len(assets)}_шт.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_return_{assets_key}")
                        with col_doc2:
                            if st.button(f"Зняти з користувача ({len(assets)} шт.)", icon=":material/person_remove:", type="primary", key=f"btn_return_{assets_key}"):
                                conn = get_connection()
                                cursor = conn.cursor()
                                ids = [a['id'] for a in assets]
                                placeholders = ','.join(['?']*len(ids))
                                cursor.execute(f"UPDATE assets SET status = 'В наявності (In Stock)', assigned_to = 'Не призначено' WHERE id IN ({placeholders})", ids)
                                conn.commit()
                                conn.close()
                                st.session_state.docx_cache = {}
                                add_audit_log(username, "Повернення", f"Масове повернення {len(assets)} активів на склад від {assigned_to}")
                                st.session_state.action_success = "Успішно оновлено (знято з користувача)!"
                                st.rerun()
                    else:
                        st.warning("⚠️ Відскановані активи мають різні статуси або призначені різним співробітникам.")
                        
                    st.markdown("---")
                    st.subheader("Списання та Утилізація")
                    for a in assets:
                        current_qty = int(a.get('quantity', 1))
                        is_consumable = "Тонер" in a.get('category', '') or "Барабан" in a.get('category', '') or "Контейнер" in a.get('category', '')
                        assigned_to = a.get('assigned_to', 'Не призначено')
                        
                        is_scrapped = a.get('status') == 'Списано (Scrapped)'
                        
                        if is_scrapped:
                            st.info(f"**{a['category']} {a['brand']} {a['model']}**: вже офіційно списано.")
                        elif assigned_to != 'Не призначено':
                            st.warning(f"**{a['category']} {a['brand']} {a['model']}**: Не можна списати, оскільки актив закріплений за **{assigned_to}**. Спочатку зніміть його з користувача.")
                        elif current_qty == 0 and a.get('status') == 'У використанні (In Use)':
                            # Витратний матеріал повністю використано — чекає на офіційне списання
                            st.write(f"**{a['category']} {a['brand']} {a['model']}**")
                            with st.form(key=f"writeoff_{a['id']}"):
                                btn_scrap = st.form_submit_button("Списати (Утилізувати)", icon=":material/delete:", type="primary")
                                if btn_scrap:
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE assets SET status = 'Списано (Scrapped)' WHERE id = ?", (a['id'],))
                                    conn.commit()
                                    conn.close()
                                    add_audit_log(username, "Списання", f"Офіційно списано {a['category']} {a['brand']} {a['model']} (ID: {a['id']}) після використання.")
                                    st.success("Успішно списано!")
                                    st.rerun()
                        elif current_qty <= 0:
                            # Залишок 0, але не "У використанні" — можливо дані застаріли; пропонуємо фінальне списання
                            effective_qty = current_qty if is_consumable else max(current_qty, 1)
                            st.warning(f"**{a['category']} {a['brand']} {a['model']}** (Залишок: {effective_qty} шт.) — доступне офіційне списання.")
                            with st.form(key=f"writeoff_{a['id']}"):
                                btn_scrap = st.form_submit_button("Списати (Утилізувати)", icon=":material/delete:", type="primary")
                                if btn_scrap:
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE assets SET status = 'Списано (Scrapped)' WHERE id = ?", (a['id'],))
                                    conn.commit()
                                    conn.close()
                                    add_audit_log(username, "Списання", f"Списано {a['category']} {a['brand']} {a['model']} (ID: {a['id']}).")
                                    st.success("Успішно списано!")
                                    st.rerun()
                        else:
                            with st.form(key=f"writeoff_{a['id']}"):
                                st.write(f"**{a['category']} {a['brand']} {a['model']}** (Залишок: {current_qty} шт.)")
                                write_off_qty = st.number_input("Кількість для списання", min_value=1, max_value=current_qty, step=1, key=f"qty_{a['id']}")
                                
                                if is_consumable:
                                    col_btn1, col_btn2 = st.columns(2)
                                    with col_btn1:
                                        btn_use = st.form_submit_button("Встановити в роботу", icon=":material/check:")
                                    with col_btn2:
                                        btn_scrap = st.form_submit_button("Списати (Утилізувати)", icon=":material/delete:")
                                else:
                                    btn_use = False
                                    btn_scrap = st.form_submit_button("Списати (Утилізувати)", icon=":material/delete:", type="primary")
                                    
                                if btn_use or btn_scrap:
                                    action_type = "Використання" if btn_use else "Списання"
                                    status_if_zero = "У використанні (In Use)" if btn_use else "Списано (Scrapped)"
                                    verb = "Використано" if btn_use else "Списано"
                                    
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    new_qty = current_qty - write_off_qty
                                    log_msg = ""
                                    if new_qty <= 0:
                                        cursor.execute("UPDATE assets SET quantity = 0, status = ?, assigned_to = 'Не призначено' WHERE id = ?", (status_if_zero, a['id']))
                                        log_msg = f"{verb} останню кількість ({write_off_qty} шт.) активу {a['category']} (ID: {a['id']}). Статус змінено на '{status_if_zero}'."
                                    else:
                                        cursor.execute("UPDATE assets SET quantity = ? WHERE id = ?", (new_qty, a['id']))
                                        log_msg = f"{verb} {write_off_qty} шт. активу {a['category']} (ID: {a['id']}). Залишок: {new_qty} шт."
                                    conn.commit()
                                    conn.close()
                                    
                                    add_audit_log(username, action_type, log_msg)
                                    st.success(f"Успішно {verb.lower()}!")
                                    st.rerun()
                
                render_actions_internal(assets, username, full_name)
                
                render_full_scan_result(assets, username, full_name)

def render_print_station():
    st.header("Генерація QR-кодів та штрихкодів")
    df = get_all_assets()
    if df.empty:
        st.info("Немає активів для відображення.")
        return
        
    st.write("Виберіть активи для генерації макету:")
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        type_choice = st.radio("Оберіть тип коду:", ["QR-код", "Штрихкод"], horizontal=True)
    
    df_selectable = df.copy()
    df_selectable.insert(0, "Вибрати", False)
    
    edited_df = st.data_editor(
        df_selectable,
        hide_index=True,
        use_container_width=True,
        disabled=df.columns.tolist(),
        key="print_selection"
    )
    
    selected_assets = edited_df[edited_df["Вибрати"] == True]
    
    if not selected_assets.empty:
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("Попередній перегляд", icon=":material/visibility:", use_container_width=True):
                st.session_state.show_preview = True
        with col_btn2:
            all_codes_docx = utils.generate_codes_docx(selected_assets.to_dict('records'), type_choice)
            st.download_button(
                label="Завантажити всі одним файлом (DOCX)",
                icon=":material/download:",
                data=all_codes_docx,
                file_name=f"labels_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        if st.session_state.get('show_preview'):
            st.markdown("---")
            st.subheader("Попередній перегляд наліпок")
            
            # Рендеримо сіткою 3xN
            assets_list = selected_assets.to_dict('records')
            for i in range(0, len(assets_list), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(assets_list):
                        asset = assets_list[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                # Заголовок наклейки
                                st.markdown(f"""
                                    <div style='text-align: center; min-height: 50px; display: flex; flex-direction: column; justify-content: center;'>
                                        <div style='font-weight: bold; font-size: 0.85em; line-height: 1.2;'>{asset['category']} {asset['brand']}</div>
                                        <div style='font-size: 0.75em; color: #555;'>SN: {asset['serial_number']}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                if type_choice == "QR-код":
                                    gen_img = utils.generate_qr(asset['barcode_data'])
                                    file_ext = "qr"
                                    img_width = 140
                                else:
                                    gen_img = utils.generate_barcode(asset['barcode_data'])
                                    file_ext = "barcode"
                                    img_width = 220
                                    
                                # Контейнер для зображення та кнопки
                                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                                st.image(gen_img, width=img_width)
                                st.download_button(
                                    label=f"Завантажити",
                                    icon=":material/download:",
                                    data=gen_img.getvalue(),
                                    file_name=f"{file_ext}_{asset['serial_number'] or asset['id']}.png",
                                    mime="image/png",
                                    key=f"dl_{file_ext}_{asset['id']}_{i+j}"
                                )
                                st.markdown("</div>", unsafe_allow_html=True)

def render_audit_log():
    st.header("Журнал аудиту")
    df = get_audit_log()
    if not df.empty:
        # Секція фільтрів
        st.subheader("Фільтри")
        col1, col2 = st.columns(2)
        
        with col1:
            filter_map = {
                "Всі події": None,
                "Списання товару": "Списання",
                "Призначення (Видача)": "Видача",
                "Надходження (Додавання)": "Додавання",
                "Повернення на склад": "Повернення",
                "Безпека (Користувачі)": "Безпека"
            }
            selected_label = st.selectbox("Категорія події", list(filter_map.keys()))
            selected_action = filter_map[selected_label]
            
        with col2:
            search_query = st.text_input("Пошук за деталями (Бренд, Модель, SN, ПІБ)")

        filtered_df = df.copy()
        
        if selected_action:
            filtered_df = filtered_df[filtered_df['action'] == selected_action]
            
        if search_query:
            q = search_query.lower()
            filtered_df = filtered_df[filtered_df['details'].str.lower().str.contains(q, na=False)]

        st.markdown("---")
        
        st.download_button(
            label="Експортувати журнал в CSV",
            icon=":material/download:",
            data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
            file_name='audit_log_export.csv',
            mime='text/csv'
        )
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("Журнал аудиту порожній.")

def render_settings(user):
    st.header("Налаштування")
    
    st.subheader("Зміна власного пароля")
    with st.form("change_own_pwd_form"):
        new_pwd = st.text_input("Новий пароль", type="password")
        if st.form_submit_button("Оновити пароль"):
            if len(new_pwd) < 3:
                st.error("Пароль занадто короткий.")
            else:
                from database import update_password
                update_password(user, new_pwd)
                add_audit_log(user, "Безпека", f"Користувач {user} змінив власний пароль")
                st.success("Пароль успішно змінено!")
                
    if user == 'admin':
        st.markdown("---")
        st.header("Налаштування Системи (Admin)")
        
        with st.expander("Оновити логотип компанії", icon=":material/image:"):
            uploaded_logo = st.file_uploader("Оберіть новий файл логотипа", type=["png", "jpg", "jpeg"], key="logo_uploader_admin")
            if uploaded_logo is not None:
                if st.button("Зберегти новий логотип"):
                    with open(LOGO_PATH, "wb") as f:
                        f.write(uploaded_logo.getbuffer())
                    add_audit_log(user, "Налаштування", "Оновлено логотип компанії")
                    st.success("Логотип успішно оновлено!")
                    st.rerun()

        st.markdown("---")
        st.header("Управління Користувачами")
        st.write("Тут ви можете керувати доступом до системи.")
        
        st.subheader("Створити нового користувача")
        with st.form("new_user_form"):
            new_username = st.text_input("Логін")
            new_fullname = st.text_input("ПІБ")
            new_password = st.text_input("Пароль", type="password")
            submit_btn = st.form_submit_button("Створити")
            
            if submit_btn:
                if not new_username or not new_password or not new_fullname:
                    st.error("Будь ласка, заповніть всі поля.")
                else:
                    success, msg = add_user(new_username, new_password, new_fullname)
                    if success:
                        st.success(msg)
                        add_audit_log(user, "Безпека", f"Створено нового користувача: {new_username}")
                    else:
                        st.error(msg)
                        
        st.subheader("Список користувачів")
        users_df = get_all_users()
        if not users_df.empty:
            for _, row in users_df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f":material/person: **{row['username']}** ({row.get('full_name', 'Без імені')}) (ID: {row['id']})")
                
                with col2.popover(f"Змінити пароль"):
                    with st.form(key=f"pwd_form_{row['id']}"):
                        admin_new_pwd = st.text_input("Введіть новий пароль", type="password")
                        if st.form_submit_button("Змінити"):
                            if len(admin_new_pwd) >= 3:
                                from database import update_password
                                update_password(row['username'], admin_new_pwd)
                                add_audit_log(user, "Безпека", f"Адмін змінив пароль користувачу {row['username']}")
                                st.success("Пароль змінено!")
                            else:
                                st.error("Короткий пароль")
                                
                if row['username'] != 'admin':
                    if col3.button("Видалити", key=f"del_user_{row['id']}"):
                        delete_user(row['id'])
                        add_audit_log(user, "Безпека", f"Видалено користувача: {row['username']}")
                        st.rerun()

if __name__ == "__main__":
    main()
