import streamlit as st
import pandas as pd
import os
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
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            border-radius: 12px;
            padding: 10px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    else:
        st.sidebar.markdown("### [Корпоративний Логотип]")
        
    try:
        with st.sidebar.popover("⚙️ Оновити логотип", use_container_width=True):
            uploaded_logo = st.file_uploader("Оберіть файл", type=["png", "jpg", "jpeg"], key="logo_uploader")
            if uploaded_logo is not None:
                with open(LOGO_PATH, "wb") as f:
                    f.write(uploaded_logo.getbuffer())
                st.rerun()
    except AttributeError:
        # Fallback для старіших версій Streamlit, якщо popover недоступний
        with st.sidebar.expander("⚙️ Оновити логотип"):
            uploaded_logo = st.file_uploader("Оберіть файл", type=["png", "jpg", "jpeg"], key="logo_uploader")
            if uploaded_logo is not None:
                with open(LOGO_PATH, "wb") as f:
                    f.write(uploaded_logo.getbuffer())
                st.rerun()

def main():
    init_db()
    render_logo()
    
    user = login_sidebar()
    if not user:
        st.warning("Будь ласка, авторизуйтесь для доступу до системи.")
        return

    st.title("Система обліку ІТ-активів")
    
    tab_names = [
        "📊 Дашборд", 
        "➕ Реєстрація активів", 
        "🔍 Сканування та Ідентифікація", 
        "🖨️ Станція друку етикеток", 
        "📋 Журнал аудиту"
    ]
    if user == 'admin':
        tab_names.append("⚙️ Налаштування")
        
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_dashboard(user)
        
    with tabs[1]:
        render_registration(user)
        
    with tabs[2]:
        render_scanning(user)
        
    with tabs[3]:
        render_print_station()
        
    with tabs[4]:
        render_audit_log()
        
    if user == 'admin' and len(tabs) > 5:
        with tabs[5]:
            render_settings(user)

def render_dashboard(username):
    st.header("Візуальна аналітика та Дашборд")
    
    df = get_all_assets()
    
    if df.empty:
        st.info("Немає активів для відображення.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Всього активів", len(df))
    col2.metric("В наявності", len(df[df['status'] == 'В наявності (In Stock)']))
    col3.metric("У використанні", len(df[df['status'] == 'У використанні (In Use)']))
    
    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Розподіл за статусами")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Статус', 'Кількість']
        fig_pie = px.pie(status_counts, names='Статус', values='Кількість', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("Кількість за категоріями")
        cat_counts = df['category'].value_counts().reset_index()
        cat_counts.columns = ['Категорія', 'Кількість']
        fig_bar = px.bar(cat_counts, x='Категорія', y='Кількість', color='Категорія')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Фільтрація та Список активів")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        f_category = st.selectbox("Категорія", ["Всі"] + list(df['category'].unique()))
    with col_f2:
        f_status = st.selectbox("Статус", ["Всі"] + list(df['status'].unique()))
    with col_f3:
        f_search = st.text_input("Пошук (Бренд, Модель, SN, ПІБ)")

    filtered_df = df.copy()
    if f_category != "Всі":
        filtered_df = filtered_df[filtered_df['category'] == f_category]
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
    
    st.download_button(
        label="📥 Експортувати список в CSV",
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
        conn = get_connection()
        cursor = conn.cursor()
        
        ALLOWED_EDIT_COLS = ['status', 'assigned_to', 'description']
        
        for index, row in edited_df.iterrows():
            orig_row = df.loc[index]
            if not row.equals(orig_row):
                asset_id = int(row['id'])
                for col in edited_df.columns:
                    if col in ALLOWED_EDIT_COLS and str(row[col]) != str(orig_row[col]):
                        cursor.execute(f"UPDATE assets SET {col} = ? WHERE id = ?", (str(row[col]), asset_id))
                        add_audit_log(username, "Оновлення", f"Актив ID {asset_id}: змінено {col} з '{orig_row[col]}' на '{row[col]}'")
                        changes_made = True
                        
        if changes_made:
            conn.commit()
            # Очищуємо кеш актів, щоб вони перегенерувалися з новими даними
            st.session_state.pop('docx_cache', None)
            st.success("Зміни успішно збережено!")
            st.rerun()
        else:
            st.info("Немає змін для збереження.")
        conn.close()

def render_registration(username):
    st.header("Реєстрація нового активу")
    
    col_cat, col_sub = st.columns(2)
    with col_cat:
        category = st.selectbox("Категорія", ["Ноутбук", "ПК", "Принтер", "Монітор", "Мережеве обладнання", "Мишка", "Гарнітура", "Інше"])
    with col_sub:
        subcategory = None
        if category == "Принтер":
            subcategory = st.selectbox("Підкатегорія принтера", ["Принтер (Пристрій)", "Тонер (Toner)", "Барабан (Drum unit)", "Контейнер відходів (Waste toner container)"])
            
    col_brand, col_model = st.columns(2)
    with col_brand:
        if category == "Принтер":
            brand_sel = st.selectbox("Бренд", ["Canon", "Інший (ввести вручну)"])
            if brand_sel == "Інший (ввести вручну)":
                brand = st.text_input("Введіть бренд вручну")
            else:
                brand = brand_sel
        elif category == "Ноутбук":
            brand_sel = st.selectbox("Бренд", ["HP", "Lenovo", "Інший (ввести вручну)"])
            if brand_sel == "Інший (ввести вручну)":
                brand = st.text_input("Введіть бренд вручну")
            else:
                brand = brand_sel
        else:
            brand = st.text_input("Бренд")
            
    with col_model:
        if category == "Принтер" and subcategory == "Принтер (Пристрій)":
            model_sel = st.selectbox("Модель", ["C3725i", "iR C1225", "iR C3325", "Інша (ввести вручну)"])
            if model_sel == "Інша (ввести вручну)":
                model = st.text_input("Введіть модель вручну")
            else:
                model = model_sel
        elif category == "Принтер" and subcategory == "Тонер (Toner)":
            toner_models = [
                "C-EXV 47 (Toner Black)", "C-EXV 47 (Toner Cyan)", "C-EXV 47 (Toner Magenta)", "C-EXV 47 (Toner Yellow)",
                "C-EXV 49 (Toner Black)", "C-EXV 49 (Toner Cyan)", "C-EXV 49 (Toner Magenta)", "C-EXV 49 (Toner Yellow)",
                "Інша (ввести вручну)"
            ]
            model_sel = st.selectbox("Модель", toner_models)
            if model_sel == "Інша (ввести вручну)":
                model = st.text_input("Введіть модель вручну")
            else:
                model = model_sel
        elif category == "Принтер" and subcategory == "Барабан (Drum unit)":
            drum_models = ["C-EXV 49 Drum Unit", "Drum Unit 034", "Інша (ввести вручну)"]
            model_sel = st.selectbox("Модель", drum_models)
            if model_sel == "Інша (ввести вручну)":
                model = st.text_input("Введіть модель вручну")
            else:
                model = model_sel
        elif category == "Принтер" and subcategory == "Контейнер відходів (Waste toner container)":
            waste_models = ["WT-202", "WT-201", "Інша (ввести вручну)"]
            model_sel = st.selectbox("Модель", waste_models)
            if model_sel == "Інша (ввести вручну)":
                model = st.text_input("Введіть модель вручну")
            else:
                model = model_sel
        else:
            model = st.text_input("Модель")
            
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            is_consumable = category == "Принтер" and subcategory in ["Тонер (Toner)", "Барабан (Drum unit)", "Контейнер відходів (Waste toner container)"]
            
            serial_number = ""
            if not is_consumable:
                serial_number = st.text_input("Серійний номер (обов'язково)")
                
            part_number = st.text_input("Парт-номер / Номер партії")
            description = st.text_area("Опис")
            
            quantity = 1
            if is_consumable:
                quantity = st.number_input("Кількість", min_value=1, value=1, step=1)
                
        with col2:
            status = st.selectbox("Статус", ["В наявності (In Stock)", "У використанні (In Use)", "Обслуговування (Maintenance)", "Списано (Scrapped)"])
            assigned_to = st.text_input("Призначено (ПІБ співробітника)", "Не призначено")
            photo_file = st.file_uploader("Фото пристрою (опціонально)", type=["png", "jpg", "jpeg"])
            
        submit = st.form_submit_button("Зареєструвати актив")
        
        if submit:
            if not is_consumable and not serial_number:
                st.error("Серійний номер є обов'язковим полем.")
            elif not brand or not model:
                st.error("Заповніть поля Бренд та Модель.")
            else:
                success_all = True
                error_msg = ""
                
                for i in range(int(quantity)):
                    import uuid
                    current_serial = serial_number
                    
                    if is_consumable:
                        current_serial = f"GEN-{str(uuid.uuid4())[:8].upper()}"
                    elif int(quantity) > 1:
                        current_serial = f"{serial_number}-{i+1}"
                        
                    prefixes = {"Ноутбук": "LAP", "ПК": "PC", "Принтер": "PRN", "Монітор": "MON", "Мережеве обладнання": "NET", "Мишка": "MOU", "Гарнітура": "HST", "Інше": "OTH"}
                    prefix = prefixes.get(category, "AST")
                    
                    final_category = category
                    if category == "Принтер" and subcategory and subcategory != "Принтер (Пристрій)":
                        final_category = f"Принтер - {subcategory}"
                    
                    photo_path = None
                    if photo_file is not None:
                        os.makedirs("uploads", exist_ok=True)
                        photo_path = os.path.join("uploads", f"{current_serial}_{photo_file.name}")
                        with open(photo_path, "wb") as f:
                            f.write(photo_file.getbuffer())
                    
                    barcode_data = f"{prefix}-{current_serial}"
                    
                    asset_data = {
                        "category": final_category,
                        "brand": brand,
                        "model": model,
                        "serial_number": current_serial,
                        "part_number": part_number,
                        "description": description,
                        "status": status,
                        "barcode_data": barcode_data,
                        "assigned_to": assigned_to,
                        "photo_path": photo_path,
                        "quantity": 1 # Кожен запис тепер - 1 одиниця
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
                df_import = pd.read_csv(uploaded_csv).fillna('')
                
                required_columns = {"category", "brand", "model", "serial_number", "status"}
                if not required_columns.issubset(df_import.columns):
                    st.error(f"Файл не містить всіх обов'язкових стовпців. Знайдено: {list(df_import.columns)}")
                else:
                    success_count = 0
                    error_count = 0
                    for _, row in df_import.iterrows():
                        category = str(row['category'])
                        serial_number = str(row['serial_number'])
                        prefixes = {"Ноутбук": "LAP", "ПК": "PC", "Принтер": "PRN", "Монітор": "MON", "Мережеве обладнання": "NET", "Інше": "OTH"}
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
    st.header("Сканування та Ідентифікація")
    st.caption("Цей інпут підтримує USB сканери штрихкодів, які працюють як емулятори клавіатури.")
    
    scan_input = st.text_input("Відскануйте штрихкод або введіть серійний номер (через кому для кількох):", key="scanner_input")
    
    if scan_input:
        from database import get_asset_by_serial_or_barcode
        codes = [c.strip() for c in scan_input.split(',') if c.strip()]
        
        assets = []
        missing_codes = []
        for code in codes:
            asset = get_asset_by_serial_or_barcode(code)
            if asset:
                assets.append(asset)
            else:
                missing_codes.append(code)
                
        if missing_codes:
            st.error(f"Не знайдено активи з кодами: {', '.join(missing_codes)}")
            
        if assets:
            full_name = st.session_state.get('full_name', username)
            
            # Об'єднуємо результати та дії в один фрагмент для стабільності
            @st.fragment
            def render_full_scan_result(assets, username, full_name):
                if len(assets) == 1:
                    asset = assets[0]
                    st.success(f"Актив знайдено: {asset['category']} {asset['brand']} {asset['model']}")
                    col_info, col_photo = st.columns([2, 1])
                    with col_info:
                        st.json({k: v for k, v in asset.items() if k != 'photo_path'})
                    with col_photo:
                        photo_path = asset.get('photo_path')
                        if photo_path and os.path.exists(os.path.abspath(photo_path)):
                            st.image(os.path.abspath(photo_path), caption="Фото пристрою", use_container_width=True)
                        else:
                            st.info("Фото відсутнє")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Штрихкод (Code128)")
                        barcode_img = utils.generate_barcode(asset['barcode_data'])
                        st.image(barcode_img)
                        st.download_button("Завантажити Штрихкод", data=barcode_img.getvalue(), file_name=f"barcode_{asset['serial_number']}.png", mime="image/png", key=f"dl_bar_{asset['id']}")
                    with col2:
                        st.subheader("QR Код")
                        qr_img = utils.generate_qr(asset['barcode_data'])
                        st.image(qr_img)
                        st.download_button("Завантажити QR", data=qr_img.getvalue(), file_name=f"qr_{asset['serial_number']}.png", mime="image/png", key=f"dl_qr_{asset['id']}")
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
                        st.write("🟢 Всі відскановані активи знаходяться на складі (Не призначено).")
                        cache_id = f"act_issue_{assets_key}"
                        if cache_id not in st.session_state.docx_cache:
                            st.session_state.docx_cache[cache_id] = utils.generate_act_docx(assets, full_name)
                        
                        col_doc1, col_doc2 = st.columns(2)
                        with col_doc1:
                            st.download_button(f"📄 Акт прийому-передачі (Видача {len(assets)} шт.)", data=st.session_state.docx_cache[cache_id], file_name=f"Акт_видачі_{len(assets)}_шт.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_act_issue_{assets_key}")
                        with col_doc2:
                            with st.expander(f"📤 Видати співробітнику ({len(assets)} шт.)"):
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
                                            st.success("Активи успішно видано!")
                                            st.rerun()
                                        else:
                                            st.error("Будь ласка, введіть ПІБ.")
                    elif len(assignees) == 1 and assignees[0] != 'Не призначено':
                        assigned_to = assignees[0]
                        st.write(f"🔴 Всі відскановані активи закріплено за: **{assigned_to}**")
                        cache_id = f"act_assign_{assets_key}"
                        if cache_id not in st.session_state.docx_cache:
                            st.session_state.docx_cache[cache_id] = utils.generate_act_docx(assets, full_name)
                        return_cache_id = f"act_return_{assets_key}"
                        if return_cache_id not in st.session_state.docx_cache:
                            st.session_state.docx_cache[return_cache_id] = utils.generate_return_act_docx(assets, assigned_to, full_name)
                        
                        col_doc1, col_doc2 = st.columns(2)
                        with col_doc1:
                            st.download_button(f"📄 Акт прийому-передачі (Видача {len(assets)} шт.)", data=st.session_state.docx_cache[cache_id], file_name=f"Акт_видачі_{len(assets)}_шт.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_act_assigned_{assets_key}")
                            st.download_button(f"📥 Акт повернення (Повернення {len(assets)} шт.)", data=st.session_state.docx_cache[return_cache_id], file_name=f"Акт_повернення_{len(assets)}_шт.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_return_{assets_key}")
                        with col_doc2:
                            if st.button(f"🔙 Зняти з користувача ({len(assets)} шт.)", type="primary", key=f"btn_return_{assets_key}"):
                                conn = get_connection()
                                cursor = conn.cursor()
                                ids = [a['id'] for a in assets]
                                placeholders = ','.join(['?']*len(ids))
                                cursor.execute(f"UPDATE assets SET status = 'В наявності (In Stock)', assigned_to = 'Не призначено' WHERE id IN ({placeholders})", ids)
                                conn.commit()
                                conn.close()
                                st.session_state.docx_cache = {}
                                add_audit_log(username, "Повернення", f"Масове повернення {len(assets)} активів на склад від {assigned_to}")
                                st.success("Успішно оновлено!")
                                st.rerun()
                    else:
                        st.warning("⚠️ Відскановані активи мають різні статуси або призначені різним співробітникам.")
                
                render_actions_internal(assets, username, full_name)

            render_full_scan_result(assets, username, full_name)

def render_print_station():
    st.header("Станція друку етикеток")
    df = get_all_assets()
    if df.empty:
        st.info("Немає активів для відображення.")
        return
        
    st.write("Виберіть активи для генерації макету етикеток:")
    
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
        if st.button("Згенерувати макет для друку"):
            st.subheader("Попередній перегляд етикеток")
            cols = st.columns(3)
            for i, (_, asset) in enumerate(selected_assets.iterrows()):
                with cols[i % 3]:
                    st.write(f"**{asset['category']} {asset['brand']}**")
                    st.write(f"SN: {asset['serial_number']}")
                    qr_img = utils.generate_qr(asset['barcode_data'])
                    st.image(qr_img, width=150)
                    st.markdown("---")

def render_audit_log():
    st.header("Журнал аудиту")
    df = get_audit_log()
    if not df.empty:
        st.download_button(
            label="📥 Експортувати журнал в CSV",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name='audit_log_export.csv',
            mime='text/csv'
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Журнал аудиту порожній.")

def render_settings(user):
    st.header("Налаштування та Управління Користувачами")
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
            col1, col2 = st.columns([4, 1])
            col1.write(f"👤 **{row['username']}** ({row.get('full_name', 'Без імені')}) (ID: {row['id']})")
            if row['username'] != 'admin':
                if col2.button("Видалити", key=f"del_user_{row['id']}"):
                    delete_user(row['id'])
                    add_audit_log(user, "Безпека", f"Видалено користувача: {row['username']}")
                    st.rerun()

if __name__ == "__main__":
    main()
