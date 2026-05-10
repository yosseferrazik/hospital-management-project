-- Hospital Management Database Schema 

-- =====================================================
-- TABLE DEFINITIONS
-- =====================================================

-- FLOORS table
CREATE TABLE FLOORS (
    floor_id SERIAL PRIMARY KEY,
    floor_number INTEGER NOT NULL UNIQUE
);

-- ROOMS table
CREATE TABLE ROOMS (
    room_id SERIAL PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL,
    floor_id INTEGER NOT NULL,
    FOREIGN KEY (floor_id) REFERENCES FLOORS(floor_id) ON DELETE RESTRICT
);

-- OPERATING_THEATERS table
CREATE TABLE OPERATING_THEATERS (
    theater_id SERIAL PRIMARY KEY,
    theater_code VARCHAR(20) NOT NULL UNIQUE,
    floor_id INTEGER NOT NULL,
    FOREIGN KEY (floor_id) REFERENCES FLOORS(floor_id) ON DELETE RESTRICT
);

-- MEDICAL_DEVICES table
CREATE TABLE MEDICAL_DEVICES (
    device_id SERIAL PRIMARY KEY,
    device_type VARCHAR(100) NOT NULL,
    theater_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    FOREIGN KEY (theater_id) REFERENCES OPERATING_THEATERS(theater_id) ON DELETE CASCADE
);

-- MEDICAL_SPECIALTIES table
CREATE TABLE MEDICAL_SPECIALTIES (
    specialty_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- STAFF table (base table for all staff types)
CREATE TABLE STAFF (
    staff_id SERIAL PRIMARY KEY,
    national_id VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    phone VARCHAR(20),
    ssn VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    address TEXT,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    staff_type VARCHAR(50) NOT NULL CHECK (staff_type IN ('MEDICAL', 'NURSING', 'GENERAL'))
);

-- MEDICAL_STAFF table
CREATE TABLE MEDICAL_STAFF (
    staff_id INTEGER PRIMARY KEY,
    specialty_id INTEGER NOT NULL,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    curriculum TEXT,
    FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE CASCADE,
    FOREIGN KEY (specialty_id) REFERENCES MEDICAL_SPECIALTIES(specialty_id) ON DELETE RESTRICT
);

-- NURSING_STAFF table
CREATE TABLE NURSING_STAFF (
    staff_id INTEGER PRIMARY KEY,
    nursing_license VARCHAR(50) NOT NULL UNIQUE,
    assigned_doctor_id INTEGER,
    assigned_floor_id INTEGER,
    certifications TEXT,
    FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_doctor_id) REFERENCES MEDICAL_STAFF(staff_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_floor_id) REFERENCES FLOORS(floor_id) ON DELETE SET NULL
);

-- GENERAL_STAFF table
CREATE TABLE GENERAL_STAFF (
    staff_id INTEGER PRIMARY KEY,
    job_type VARCHAR(100) NOT NULL,
    FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE CASCADE
);

-- MEDICAL_STAFF_SPECIALTIES (junction table for many-to-many relationship)
CREATE TABLE MEDICAL_STAFF_SPECIALTIES (
    medical_staff_specialty_id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL,
    specialty_id INTEGER NOT NULL,
    FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE CASCADE,
    FOREIGN KEY (specialty_id) REFERENCES MEDICAL_SPECIALTIES(specialty_id) ON DELETE CASCADE,
    UNIQUE(staff_id, specialty_id)
);

-- PATIENTS table
CREATE TABLE PATIENTS (
    patient_id SERIAL PRIMARY KEY,
    national_id VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    blood_type VARCHAR(5) CHECK (blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    allergies TEXT
);

-- VISITS table
CREATE TABLE VISITS (
    visit_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    visit_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    diagnosis TEXT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES MEDICAL_STAFF(staff_id) ON DELETE RESTRICT
);

-- SCHEDULED_APPOINTMENTS table
CREATE TABLE SCHEDULED_APPOINTMENTS (
    appointment_id SERIAL PRIMARY KEY,
    visit_id INTEGER NOT NULL UNIQUE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
    FOREIGN KEY (visit_id) REFERENCES VISITS(visit_id) ON DELETE CASCADE
);

-- MEDICATIONS table
CREATE TABLE MEDICATIONS (
    medication_id SERIAL PRIMARY KEY,
    medication_name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT
);

-- PRESCRIPTIONS table
CREATE TABLE PRESCRIPTIONS (
    prescription_id SERIAL PRIMARY KEY,
    visit_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration_days INTEGER,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (visit_id) REFERENCES VISITS(visit_id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES MEDICATIONS(medication_id) ON DELETE RESTRICT
);

-- ADMISSIONS table
CREATE TABLE ADMISSIONS (
    admission_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    admission_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expected_discharge_date DATE,
    actual_discharge_date DATE,
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES ROOMS(room_id) ON DELETE RESTRICT,
    CHECK (actual_discharge_date >= DATE(admission_date) OR actual_discharge_date IS NULL)
);

-- SURGERIES table
CREATE TABLE SURGERIES (
    surgery_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    theater_id INTEGER NOT NULL,
    primary_surgeon_id INTEGER NOT NULL,
    surgery_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    procedure_type VARCHAR(200) NOT NULL,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (theater_id) REFERENCES OPERATING_THEATERS(theater_id) ON DELETE RESTRICT,
    FOREIGN KEY (primary_surgeon_id) REFERENCES MEDICAL_STAFF(staff_id) ON DELETE RESTRICT,
    CHECK (end_time > start_time)
);

-- SURGERY_ASSISTANTS table (composite primary key)
CREATE TABLE SURGERY_ASSISTANTS (
    surgery_id INTEGER NOT NULL,
    nurse_id INTEGER NOT NULL,
    role VARCHAR(100) NOT NULL,
    PRIMARY KEY (surgery_id, nurse_id),
    FOREIGN KEY (surgery_id) REFERENCES SURGERIES(surgery_id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_id) REFERENCES NURSING_STAFF(staff_id) ON DELETE RESTRICT
);

-- PHARMACY_DISPENSATIONS table
CREATE TABLE PHARMACY_DISPENSATIONS (
    dispensation_id SERIAL PRIMARY KEY,
    admission_id INTEGER NOT NULL,
    dispensed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_cost DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (total_cost >= 0),
    notes TEXT,
    FOREIGN KEY (admission_id) REFERENCES ADMISSIONS(admission_id) ON DELETE CASCADE
);

-- DISPENSATION_ITEMS table
CREATE TABLE DISPENSATION_ITEMS (
    item_id SERIAL PRIMARY KEY,
    dispensation_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (dispensation_id) REFERENCES PHARMACY_DISPENSATIONS(dispensation_id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES MEDICATIONS(medication_id) ON DELETE RESTRICT
);

-- RADIOLOGY_EXAMS table
CREATE TABLE RADIOLOGY_EXAMS (
    exam_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    requesting_doctor_id INTEGER NOT NULL,
    exam_type VARCHAR(100) NOT NULL,
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    performed_at TIMESTAMP,
    result_image_url TEXT,
    radiologist_report TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'REQUESTED' CHECK (status IN ('REQUESTED', 'SCHEDULED', 'COMPLETED', 'CANCELLED')),
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (requesting_doctor_id) REFERENCES MEDICAL_STAFF(staff_id) ON DELETE RESTRICT
);

-- APP_USERS table
CREATE TABLE APP_USERS (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    staff_id INTEGER NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'NURSE', 'STAFF', 'RECEPTIONIST')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE CASCADE
);

-- AUDIT_LOGS table
CREATE TABLE AUDIT_LOGS (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT', 'LOGIN', 'LOGOUT')),
    table_name VARCHAR(100),
    record_id INTEGER,
    old_data TEXT,
    new_data TEXT,
    ip_address INET,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES APP_USERS(user_id) ON DELETE SET NULL
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- FLOORS indexes
CREATE INDEX idx_floors_floor_number ON FLOORS(floor_number);

-- ROOMS indexes
CREATE INDEX idx_rooms_floor_id ON ROOMS(floor_id);
CREATE INDEX idx_rooms_room_number ON ROOMS(room_number);

-- OPERATING_THEATERS indexes
CREATE INDEX idx_op_theaters_floor_id ON OPERATING_THEATERS(floor_id);
CREATE INDEX idx_op_theaters_code ON OPERATING_THEATERS(theater_code);

-- MEDICAL_DEVICES indexes
CREATE INDEX idx_medical_devices_theater_id ON MEDICAL_DEVICES(theater_id);
CREATE INDEX idx_medical_devices_type ON MEDICAL_DEVICES(device_type);

-- STAFF indexes
CREATE INDEX idx_staff_national_id ON STAFF(national_id);
CREATE INDEX idx_staff_last_name ON STAFF(last_name);
CREATE INDEX idx_staff_email ON STAFF(email);
CREATE INDEX idx_staff_hire_date ON STAFF(hire_date);
CREATE INDEX idx_staff_staff_type ON STAFF(staff_type);

-- MEDICAL_STAFF indexes
CREATE INDEX idx_medical_staff_specialty ON MEDICAL_STAFF(specialty_id);
CREATE INDEX idx_medical_staff_license ON MEDICAL_STAFF(license_number);

-- NURSING_STAFF indexes
CREATE INDEX idx_nursing_staff_assigned_doctor ON NURSING_STAFF(assigned_doctor_id);
CREATE INDEX idx_nursing_staff_assigned_floor ON NURSING_STAFF(assigned_floor_id);
CREATE INDEX idx_nursing_staff_license ON NURSING_STAFF(nursing_license);

-- MEDICAL_STAFF_SPECIALTIES indexes
CREATE INDEX idx_staff_specialties_staff_id ON MEDICAL_STAFF_SPECIALTIES(staff_id);
CREATE INDEX idx_staff_specialties_specialty_id ON MEDICAL_STAFF_SPECIALTIES(specialty_id);

-- PATIENTS indexes
CREATE INDEX idx_patients_national_id ON PATIENTS(national_id);
CREATE INDEX idx_patients_last_name ON PATIENTS(last_name);
CREATE INDEX idx_patients_birth_date ON PATIENTS(birth_date);
CREATE INDEX idx_patients_blood_type ON PATIENTS(blood_type);

-- VISITS indexes
CREATE INDEX idx_visits_patient_id ON VISITS(patient_id);
CREATE INDEX idx_visits_doctor_id ON VISITS(doctor_id);
CREATE INDEX idx_visits_timestamp ON VISITS(visit_timestamp);

-- SCHEDULED_APPOINTMENTS indexes
CREATE INDEX idx_appointments_visit_id ON SCHEDULED_APPOINTMENTS(visit_id);
CREATE INDEX idx_appointments_date ON SCHEDULED_APPOINTMENTS(appointment_date);
CREATE INDEX idx_appointments_status ON SCHEDULED_APPOINTMENTS(status);

-- PRESCRIPTIONS indexes
CREATE INDEX idx_prescriptions_visit_id ON PRESCRIPTIONS(visit_id);
CREATE INDEX idx_prescriptions_medication_id ON PRESCRIPTIONS(medication_id);
CREATE INDEX idx_prescriptions_start_date ON PRESCRIPTIONS(start_date);

-- ADMISSIONS indexes
CREATE INDEX idx_admissions_patient_id ON ADMISSIONS(patient_id);
CREATE INDEX idx_admissions_room_id ON ADMISSIONS(room_id);
CREATE INDEX idx_admissions_admission_date ON ADMISSIONS(admission_date);
CREATE INDEX idx_admissions_discharge_date ON ADMISSIONS(actual_discharge_date);

-- SURGERIES indexes
CREATE INDEX idx_surgeries_patient_id ON SURGERIES(patient_id);
CREATE INDEX idx_surgeries_theater_id ON SURGERIES(theater_id);
CREATE INDEX idx_surgeries_surgeon_id ON SURGERIES(primary_surgeon_id);
CREATE INDEX idx_surgeries_date ON SURGERIES(surgery_date);

-- SURGERY_ASSISTANTS indexes
CREATE INDEX idx_surgery_assistants_nurse_id ON SURGERY_ASSISTANTS(nurse_id);

-- PHARMACY_DISPENSATIONS indexes
CREATE INDEX idx_dispensations_admission_id ON PHARMACY_DISPENSATIONS(admission_id);
CREATE INDEX idx_dispensations_dispensed_at ON PHARMACY_DISPENSATIONS(dispensed_at);

-- DISPENSATION_ITEMS indexes
CREATE INDEX idx_dispensation_items_dispensation_id ON DISPENSATION_ITEMS(dispensation_id);
CREATE INDEX idx_dispensation_items_medication_id ON DISPENSATION_ITEMS(medication_id);

-- RADIOLOGY_EXAMS indexes
CREATE INDEX idx_radiology_patient_id ON RADIOLOGY_EXAMS(patient_id);
CREATE INDEX idx_radiology_doctor_id ON RADIOLOGY_EXAMS(requesting_doctor_id);
CREATE INDEX idx_radiology_status ON RADIOLOGY_EXAMS(status);
CREATE INDEX idx_radiology_requested_at ON RADIOLOGY_EXAMS(requested_at);

-- APP_USERS indexes
CREATE INDEX idx_app_users_username ON APP_USERS(username);
CREATE INDEX idx_app_users_staff_id ON APP_USERS(staff_id);
CREATE INDEX idx_app_users_role ON APP_USERS(role);
CREATE INDEX idx_app_users_active ON APP_USERS(is_active);

-- AUDIT_LOGS indexes
CREATE INDEX idx_audit_logs_user_id ON AUDIT_LOGS(user_id);
CREATE INDEX idx_audit_logs_timestamp ON AUDIT_LOGS(action_timestamp);
CREATE INDEX idx_audit_logs_action_type ON AUDIT_LOGS(action_type);
CREATE INDEX idx_audit_logs_table_name ON AUDIT_LOGS(table_name);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON DATABASE hospital_management IS 'Hospital Management System database';

COMMENT ON TABLE FLOORS IS 'Building floor information';
COMMENT ON TABLE ROOMS IS 'Patient rooms located on floors';
COMMENT ON TABLE OPERATING_THEATERS IS 'Surgical operation theaters';
COMMENT ON TABLE MEDICAL_DEVICES IS 'Medical devices assigned to operating theaters';
COMMENT ON TABLE MEDICAL_SPECIALTIES IS 'Medical specialties definitions';
COMMENT ON TABLE STAFF IS 'Base table for all hospital staff';
COMMENT ON TABLE MEDICAL_STAFF IS 'Medical staff (doctors, surgeons) extending STAFF';
COMMENT ON TABLE NURSING_STAFF IS 'Nursing staff extending STAFF';
COMMENT ON TABLE GENERAL_STAFF IS 'General staff (administrative, support) extending STAFF';
COMMENT ON TABLE PATIENTS IS 'Patient information';
COMMENT ON TABLE VISITS IS 'Patient visits and consultations';
COMMENT ON TABLE SCHEDULED_APPOINTMENTS IS 'Scheduled appointments for visits';
COMMENT ON TABLE MEDICATIONS IS 'Medication catalog';
COMMENT ON TABLE PRESCRIPTIONS IS 'Prescriptions issued during visits';
COMMENT ON TABLE ADMISSIONS IS 'Patient hospital admissions';
COMMENT ON TABLE SURGERIES IS 'Surgical procedures';
COMMENT ON TABLE SURGERY_ASSISTANTS IS 'Nursing staff assisting in surgeries';
COMMENT ON TABLE PHARMACY_DISPENSATIONS IS 'Pharmacy dispensations during admissions';
COMMENT ON TABLE DISPENSATION_ITEMS IS 'Individual items in pharmacy dispensations';
COMMENT ON TABLE RADIOLOGY_EXAMS IS 'Radiology examination records';
COMMENT ON TABLE APP_USERS IS 'Application user accounts linked to staff';
COMMENT ON TABLE AUDIT_LOGS IS 'System audit trail';