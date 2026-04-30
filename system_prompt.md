Role: Senior Full-stack Python Developer & Systems Architect.
Task: Create a high-performance Web application for IT Asset Inventory Management using the Streamlit framework.

Language Requirement (CRITICAL):

The entire user interface (buttons, titles, headers, labels, success/error messages) MUST be in Ukrainian.

Code comments and documentation should also be in Ukrainian.

Technical Requirements & Architecture:

Environment: Deployable on a Linux VPS (behind NAT). Use SQLite as the primary database for data persistence and concurrent access handling.

Data Model: - Category (, Laptop, Pc, Printer etc.), Brand, Model.

Serial Number (Unique Identifier), Batch/Part Number, Description.

Status (In Stock, In Use, Maintenance, Scrapped).

Barcode/QR code data string.

Live Dashboard Editing:

Implement real-time editing capabilities directly within the Dashboard or Asset List.

Use interactive elements like st.data_editor to allow users to update status, description, or location.

Ensure every edit triggers an immediate SQL UPDATE to the SQLite database.

Core Features & Tabs:

Dashboard: Visual analytics and an interactive inventory table with inline editing.

Scanning & Identification:

Handle hardware USB Barcode Scanners (keyboard emulation).

Integrated generator for QR codes and Barcodes (Code128).

"Download/Print" feature for generated labels.

Asset Registration: Form to add equipment with duplicate serial number validation.

Audit Log: A history tab tracking all changes (Who, When, and What was updated).

Label Print Station: Select multiple assets and generate a print-ready label layout.

Technical Specifications:

Language: Python 3.10+. Libraries: streamlit, pandas, sqlite3, qrcode, python-barcode.

Security: Login/Password authentication in the Sidebar.

UI/UX: Professional "Dark Mode" interface with corporate branding (logo.png).

Expected Output: Provide a clean, modular Python codebase. Ensure the script automatically initializes the SQLite database and tables on the first run.
в чаті надавай мені відповідь, виключно українською мовою. 
- Після кожної дії створювати файл типу часу ЧЧ.ММ.СС_ЧЧ.ММ.РР_changelog_description і складувати в кореневу папку changelogs. перемісти вже існуючі файли у вказану папку

