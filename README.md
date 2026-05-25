<img width="1408" height="768" alt="data_pipe_line" src="https://github.com/user-attachments/assets/95b091a4-b57b-44e2-b8d4-1a7eea0d840a" />

## 🚀 Quick Start (Phase 1: Upload Module)

### Prerequisites

- Python 3.8+
- MySQL database (existing schema provided)
- MinIO server (local or cloud)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/prabhakar-github/med-img-analyzer.git
   cd med-img-analyzer
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   ```bash   
   py -m pip install -r requirements.txt 
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL and MinIO credentials
   ```

4. **Set up MinIO (Local Development)**
   
   Using Docker:
   ```bash
   docker run -p 9000:9000 -p 9001:9001 \
     minio/minio server /data --console-address ":9001"
   ```
   
   Or download from [min.io](https://min.io/download)
   
   Default credentials:
   - Access Key: `minioadmin`
   - Secret Key: `minioadmin`
   - Console: http://localhost:9001

5. **Initialize MySQL database**
   
   The database schema is provided in `my_sql.sql`. Run it to create tables:
   ```bash
   mysql -h <host> -u <user> -p < database_name < my_sql.sql
   ```

6. **Create operator accounts**
   
   Use the provided sample data in `my_sql.sql` or insert operators with hashed passwords:
   ```python
   from werkzeug.security import generate_password_hash
   # Generate password hash for insertion
   print(generate_password_hash('your_password'))
   ```

7. **Run the application**
   ```bash
   python run.py
   ```
   OR directly initiate FastAPI webserver...
   ```bash   
   py -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload
   ```
   
8. **Access the application**
   - Web Interface: http://localhost:5000
   - Login with credentials from MySQL `operators` table

### Features Implemented

- **Authentication**: Secure login for operators with audit logging
- **Multi-file Upload**: Upload up to 50 DICOM files per session
- **Real-time Validation**: DICOM format, file size, and metadata validation
- **Dual Storage**: Raw DICOM files + processed preview images (PNG)
- **Audit Logging**: All actions logged for compliance
- **Client Management**: Support for hospitals, diagnostic centers, and clinics

### Project Structure

```
med-img-analyzer/
├── README.md
├── requirements.txt
├── run.py
├── hash_password.py
├── app/
│   ├── __init__.py                 # FastAPI app factory and router registration
│   ├── config.py                   # Environment-based application settings
│   ├── database.py                 # Async SQLAlchemy engine/session setup
│   ├── models.py                   # SQLAlchemy 2.0 ORM models
│   ├── template_helpers.py         # Jinja templates and flash-message helpers
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── forms.py                # Login-related constants
│   │   └── routes.py               # FastAPI auth routes: login/logout/session auth
│   │
│   ├── upload/
│   │   ├── __init__.py
│   │   ├── forms.py                # Upload-related constants
│   │   ├── routes.py               # FastAPI upload dashboard and upload handlers
│   │   ├── validators.py           # DICOM/file validation logic
│   │   └── processors.py           # DICOM-to-preview PNG processing
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── minio_client.py         # MinIO object-storage client wrapper
│   │   ├── my_sql.sql              # MySQL schema and seed data
│   │   └── DB_Model.xlsx           # Database model/design spreadsheet
│   │
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── base.html               # Shared Bootstrap layout
│   │   ├── auth/
│   │   │   └── login.html          # Operator login page
│   │   └── upload/
│   │       └── dashboard.html      # DICOM upload dashboard
│   │
│   └── test/
│       └── test-connection-mysql.py
```


**Main Application Modules**
- app/__init__.py: Creates the FastAPI app, configures session middleware, registers auth/upload routers.
- app/database.py: Provides async MySQL sessions using SQLAlchemy + aiomysql.
- app/auth/routes.py: Handles login/logout and session-based operator lookup.
- app/upload/routes.py: Handles upload dashboard and DICOM file upload workflow.
- app/storage/minio_client.py: Stores raw DICOM and processed PNG previews in MinIO.
- app/upload/processors.py: Converts DICOM pixel data into PNG previews.
- app/upload/validators.py: Validates file extension, size, DICOM tags, and modality.


**Next Steps to Run:**
1. Install dependencies: `pip install -r requirements.txt`
2. Copy [.env.example](file:///c:/Windspace/med-img-analyzer/.env.example:0:0-0:0) to `.env` and configure credentials
3. Set up MinIO locally (Docker: `docker run -p 9000:9000 minio/minio server /data`)
4. Initialize MySQL database with existing [my_sql.sql](file:///c:/Windspace/med-img-analyzer/my_sql.sql:0:0-0:0) schema
5. Generate password hashes using `python hash_password.py` for operator accounts
6. Run application: `python run.py`
7. Access at http://localhost:5000


---
*Developed for clinical research and diagnostic assistance.*
