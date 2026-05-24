<img width="1408" height="768" alt="data_pipe_line" src="https://github.com/user-attachments/assets/95b091a4-b57b-44e2-b8d4-1a7eea0d840a" />

## 🚀 Quick Start (Phase 1: Upload Module)

### Prerequisites

- Python 3.8+
- MySQL database (existing schema provided)
- MinIO server (local or cloud)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd med-img-analyzer
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
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
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration
│   ├── models.py             # SQLAlchemy ORM models
│   ├── auth/                 # Authentication module
│   │   ├── routes.py
│   │   └── forms.py
│   ├── upload/               # Upload module
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── validators.py     # DICOM validation
│   │   └── processors.py     # DICOM processing
│   ├── storage/              # MinIO integration
│   │   └── minio_client.py
│   └── templates/            # HTML templates
├── requirements.txt
├── run.py
├── .env.example
└── my_sql.sql                # Database schema
```


**Core Components:**
- **Flask Web Application** with modular architecture (auth, upload, storage modules)
- **MySQL Integration** using SQLAlchemy ORM mapped to your existing schema
- **MinIO Storage Client** for S3-compatible local storage of raw and processed images
- **Authentication System** with login/logout, password hashing, and audit logging
- **Multi-file Upload Form** supporting up to 50 DICOM files per session
- **Real-time DICOM Validation** for format, file size, and required metadata tags
- **DICOM Processing Pipeline** that extracts metadata and generates PNG preview images
- **Bootstrap 5 UI** with responsive design and flash messages

**Key Features:**
- Secure operator authentication with audit trail
- Dual storage: Raw DICOM files (.dcm) + Processed preview images (.png)
- Comprehensive validation (file extension, size, DICOM format, required tags)
- Audit logging for all data access (HIPAA/GDPR compliance ready)
- Client management (hospitals, diagnostic centers, clinics)
- SHA256 checksums for data integrity

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
