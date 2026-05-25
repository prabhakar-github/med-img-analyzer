MySQL Details :
===============
http://www.phpmyadmin.co 

Host: sql12.freesqldatabase.com
Database name: sql12827989
Database user: sql12827989
Database password: mQVMS5b1lL
Port number: 3306



-- ============================================================================
-- *******************  DDL  Scirpt (Create Tables )  *************************
-- ============================================================================
-- 1. CLIENT ( HOSPITAL ) DETAILS
-- ============================================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS sql12827989;
USE sql12827989;

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type ENUM('HOSPITAL', 'DIAGNOSTIC_CENTER', 'CLINIC') NOT NULL,
    license_number VARCHAR(100) NOT NULL UNIQUE,
    address TEXT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


-- ============================================================================
-- 2. IDENTITY AND ACCESS MANAGEMENT - OPERATORS 
-- ============================================================================

CREATE TABLE operators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Engineered to store Argon2/Bcrypt hashes
    full_name VARCHAR(150) NOT NULL,
    role ENUM('OPERATOR', 'FACILITY_ADMIN', 'SYSTEM_SUPER_ADMIN') DEFAULT 'OPERATOR' NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ,
    CONSTRAINT fk_operators_client FOREIGN KEY (client_id)
        REFERENCES clients(id) ON DELETE RESTRICT ON UPDATE CASCADE
);


-- ============================================================================
-- 3. IMAGING DATA AND TRANSACTION TABLES
-- ============================================================================

CREATE TABLE cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    operator_id INT NOT NULL,
    patient_reference_id VARCHAR(100) NOT NULL, -- Anonymized medical identifier
    modality ENUM('XRAY', 'MRI', 'CT', 'ULTRASOUND', 'MAMMOGRAPHY') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cases_client FOREIGN KEY (client_id)
        REFERENCES clients(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cases_operator FOREIGN KEY (operator_id)
        REFERENCES operators(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE raw_image_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    file_name_original VARCHAR(255) NOT NULL,
    storage_path VARCHAR(2048) NOT NULL, -- Stores object storage URI pointer (S3/Cloud Storage)
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL, -- e.g., 'application/dicom'
    checksum_sha256 CHAR(64) NOT NULL, -- Data integrity validator
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_uploads_case FOREIGN KEY (case_id)
        REFERENCES cases(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE processed_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    raw_image_id INT NOT NULL,
    file_name_original VARCHAR(255) NOT NULL,
    storage_path VARCHAR(2048) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    processing_type VARCHAR(50) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_processed_images_case FOREIGN KEY (case_id)
        REFERENCES cases(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_processed_images_raw FOREIGN KEY (raw_image_id)
        REFERENCES raw_image_uploads(id) ON DELETE RESTRICT ON UPDATE CASCADE
);


-- ============================================================================
-- 4. COMPLIANCE AND AUDIT LOGS
-- ============================================================================

CREATE TABLE login_audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    operator_id INT NULL, -- Left Nullable to capture dynamic malicious vectors or brute force attempts
    attempted_username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL, -- Accommodates both IPv4 and IPv6 string lengths
    user_agent VARCHAR(512) NULL,
    status ENUM('SUCCESS', 'FAILED_PASSWORD', 'ACCOUNT_LOCKED') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_login_logs_operator FOREIGN KEY (operator_id)
        REFERENCES operators(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE data_access_audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    operator_id INT NOT NULL,
    action ENUM('UPLOAD_IMAGE', 'VIEW_IMAGE', 'DELETE_RECORD', 'EXPORT_METADATA') NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_id INT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_data_logs_operator FOREIGN KEY (operator_id)
        REFERENCES operators(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ;


-- ============================================================================
-- 5. Performance Tuning - INDEXES
-- ============================================================================

-- Fast lookup for audit trail and compliance querying
CREATE INDEX idx_login_audit_timestamp ON login_audit_logs(timestamp);
CREATE INDEX idx_data_audit_operator ON data_access_audit_logs(operator_id, timestamp);

-- Speeds up retrieval of specific patient encounter sessions by hospital/clinic code
CREATE INDEX idx_cases_patient_lookup ON cases(client_id, patient_reference_id);

-- Accelerates loading images associated with a single case folder
CREATE INDEX idx_raw_images_case_id ON raw_image_uploads(case_id);
CREATE INDEX idx_processed_images_case_id ON processed_images(case_id);
CREATE INDEX idx_processed_images_raw_image_id ON processed_images(raw_image_id);




--  *************************** Sample Data ( Insert Script)  ***********************


USE sql12827989;

-- Seed Clients
INSERT INTO clients (id, name, type, license_number, address) VALUES
(1, 'Metro General Hospital', 'HOSPITAL', 'HOSP-2026-8891', '742 Evergreen Terrace, Springfield'),
(2, 'Apex Diagnostic Center', 'DIAGNOSTIC_CENTER', 'DIAG-2026-4412', '100 Main Street, Metropolis'),
(3, 'Valley Kids Pediatric Clinic', 'CLINIC', 'CLIN-2026-0034', '456 Oak Lane, Riverdale');

-- Seed Operators
INSERT INTO operators (id, client_id, username, password_hash, full_name, role, email, phone) VALUES
(101, 1, 'jdoe_metro', '$2b$12$ExamPlE...', 'Dr. John Doe', 'FACILITY_ADMIN', 'j.doe@metrogeneral.org', '+1-555-0192'),
(102, 1, 'jsmith_tech', '$2b$12$HashStr...', 'Jane Smith', 'OPERATOR', 'j.smith@metrogeneral.org', '+1-555-0193'),
(103, 2, 'rjones_apex', '$2b$12$SecUrE...', 'Robert Jones', 'OPERATOR', 'r.jones@apexdiag.com', '+1-555-0744');

-- Seed Cases
INSERT INTO cases (id, client_id, operator_id, patient_reference_id, modality) VALUES
(5001, 1, 102, 'PAT-HASH-9921A', 'XRAY'),
(5002, 1, 102, 'PAT-HASH-4410B', 'MRI'),
(5003, 2, 103, 'PAT-HASH-1102Z', 'CT');

-- Seed Image Upload Metadata
INSERT INTO raw_image_uploads (id, case_id, file_name_original, storage_path, file_size_bytes, mime_type, checksum_sha256) VALUES
(9001, 5001, 'chest_p_view.dcm', 's3://med-images/c1/case5001/f81a.dcm', 5242880, 'application/dicom', 'e3b0c44298fc1c149afbf4c8996fb92427ae'),
(9002, 5001, 'chest_lateral.dcm', 's3://med-images/c1/case5001/a29c.dcm', 5120000, 'application/dicom', '7f83b1657ff1fc53b92c181f67a138768d57'),
(9003, 5002, 'brain_t1_slice4.dcm', 's3://med-images/c1/case5002/bc88.dcm', 15728640, 'application/dicom', '8618a10a1f33b1e7c8f024c11c5a14d5e212');

-- Seed Authentication Audit Logs
INSERT INTO login_audit_logs (id, operator_id, attempted_username, ip_address, user_agent, status) VALUES
(100001, 102, 'jsmith_tech', '192.168.1.45', 'Mozilla/5.0 (Windows NT 10.0...)', 'SUCCESS'),
(100002, NULL, 'admin_hack', '203.0.113.195', 'curl/7.68.0', 'FAILED_PASSWORD'),
(100003, 103, 'rjones_apex', '2001:db8::ff00:42:83', 'Mozilla/5.0 (Macintosh; Intel...)', 'SUCCESS');

-- Seed System Access Audit Logs
INSERT INTO data_access_audit_logs (id, operator_id, action, target_table, target_record_id, ip_address) VALUES
(200001, 102, 'UPLOAD_IMAGE', 'raw_image_uploads', 9001, '192.168.1.45'),
(200002, 102, 'UPLOAD_IMAGE', 'raw_image_uploads', 9002, '192.168.1.45'),
(200003, 101, 'VIEW_IMAGE', 'raw_image_uploads', 9001, '192.168.1.12');

commit;



