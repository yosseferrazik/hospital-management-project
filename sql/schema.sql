-- =======================================================
-- HOSPITAL MANAGEMENT SYSTEM - POSTGRESQL SCHEMA
-- Includes: Core medical entities, simple user auth, audit logs
-- =======================================================

-- -------------------------------------------------------
-- 1. HOSPITAL INFRASTRUCTURE
-- -------------------------------------------------------

-- Floors (Plantes)
CREATE TABLE floors (
    id SERIAL PRIMARY KEY,
    floor_number INT UNIQUE NOT NULL CHECK (floor_number BETWEEN 1 AND 4)
);
COMMENT ON TABLE floors IS 'Hospital floors, identified by number (1st, 2nd, 3rd, 4th).';

-- Rooms for patient admission
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL,
    floor_id INT NOT NULL REFERENCES floors(id),
    UNIQUE(floor_id, room_number)
);
COMMENT ON TABLE rooms IS 'Patient rooms on each floor. Room number is unique per floor.';

-- Operating theaters (Quiròfans)
CREATE TABLE operating_theaters (
    id SERIAL PRIMARY KEY,
    theater_code VARCHAR(10) NOT NULL, -- Q1, Q2...
    floor_id INT NOT NULL REFERENCES floors(id),
    UNIQUE(floor_id, theater_code)
);
COMMENT ON TABLE operating_theaters IS 'Surgical theaters identified by code Q1, Q2... per floor.';

-- Medical devices in operating theaters
CREATE TABLE medical_devices (
    id SERIAL PRIMARY KEY,
    device_type VARCHAR(100) NOT NULL,
    theater_id INT NOT NULL REFERENCES operating_theaters(id),
    quantity INT DEFAULT 1 CHECK (quantity >= 0),
    UNIQUE(theater_id, device_type)
);
COMMENT ON TABLE medical_devices IS 'Medical apparatus assigned to a specific theater. Tracks count per type.';

-- -------------------------------------------------------
-- 2. STAFF (Medical, Nursing, General)
-- -------------------------------------------------------

-- Medical specialties
CREATE TABLE medical_specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);
COMMENT ON TABLE medical_specialties IS 'Medical specialties (e.g., Cardiology, Pediatrics).';

-- Base staff table
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    national_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    staff_type VARCHAR(20) NOT NULL CHECK (staff_type IN ('MEDICAL', 'NURSING', 'GENERAL'))
);
COMMENT ON TABLE staff IS 'Base table for all hospital personnel.';

-- Doctors
CREATE TABLE medical_staff (
    staff_id INT PRIMARY KEY REFERENCES staff(id),
    specialty_id INT NOT NULL REFERENCES medical_specialties(id),
    license_number VARCHAR(50) UNIQUE NOT NULL,
    curriculum TEXT
    );
COMMENT ON TABLE medical_staff IS 'Doctors with unique specialty and extensive CV data.';

-- Nursing staff
CREATE TABLE nursing_staff (
    staff_id INT PRIMARY KEY REFERENCES staff(id),
    nursing_license VARCHAR(50) UNIQUE NOT NULL,
    assigned_doctor_id INT REFERENCES medical_staff(staff_id),
    is_floor_nurse BOOLEAN DEFAULT FALSE,
    certifications TEXT
);
COMMENT ON TABLE nursing_staff IS 'Nurses. May be assigned to a single doctor or work as floor nurses.';

-- General staff
CREATE TABLE general_staff (
    staff_id INT PRIMARY KEY REFERENCES staff(id),
    job_type VARCHAR(50) NOT NULL
);
COMMENT ON TABLE general_staff IS 'Miscellaneous staff (zeladors, administratius, conductors).';

-- -------------------------------------------------------
-- 3. PATIENTS AND CLINICAL ENCOUNTERS
-- -------------------------------------------------------

-- Patients
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    national_id VARCHAR(20) UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    blood_type VARCHAR(5),
    allergies TEXT
);
COMMENT ON TABLE patients IS 'Patients treated at the hospital.';

-- Visits
CREATE TABLE visits (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(id),
    doctor_id INT NOT NULL REFERENCES medical_staff(staff_id),
    visit_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    diagnosis TEXT,
    notes TEXT
);
COMMENT ON TABLE visits IS 'Record of patient consultations with a doctor.';

-- Scheduled appointment times
CREATE TABLE scheduled_appointments (
    id SERIAL PRIMARY KEY,
    visit_id INT NOT NULL REFERENCES visits(id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'SCHEDULED'
);
COMMENT ON TABLE scheduled_appointments IS 'Specific day and hour of a patient visit for each doctor.';

-- Prescriptions
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    visit_id INT NOT NULL REFERENCES visits(id),
    medication_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    duration_days INT,
    start_date DATE DEFAULT CURRENT_DATE
);
COMMENT ON TABLE prescriptions IS 'Medications prescribed during a visit.';

-- Admissions
CREATE TABLE admissions (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(id),
    room_id INT NOT NULL REFERENCES rooms(id),
    admission_date DATE NOT NULL,
    expected_discharge_date DATE NOT NULL,
    actual_discharge_date DATE,
    CONSTRAINT valid_dates CHECK (expected_discharge_date >= admission_date)
);
COMMENT ON TABLE admissions IS 'Room reservations and actual inpatient stays.';

-- Surgeries
CREATE TABLE surgeries (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(id),
    theater_id INT NOT NULL REFERENCES operating_theaters(id),
    primary_surgeon_id INT NOT NULL REFERENCES medical_staff(staff_id),
    surgery_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    procedure_type VARCHAR(100) NOT NULL,
    notes TEXT,
    UNIQUE(theater_id, surgery_date, start_time)
);
COMMENT ON TABLE surgeries IS 'Surgical procedures scheduled in operating theaters.';

-- Surgery assistants (nurses)
CREATE TABLE surgery_assistants (
    surgery_id INT NOT NULL REFERENCES surgeries(id),
    nurse_id INT NOT NULL REFERENCES nursing_staff(staff_id),
    role VARCHAR(50),
    PRIMARY KEY (surgery_id, nurse_id)
);
COMMENT ON TABLE surgery_assistants IS 'Nurses assisting a surgeon during an operation.';

-- -------------------------------------------------------
-- 4. PHARMACY AND RADIOLOGY DEPARTMENTS
-- -------------------------------------------------------

-- Pharmacy dispensations
CREATE TABLE pharmacy_dispensations (
    id SERIAL PRIMARY KEY,
    admission_id INT NOT NULL REFERENCES admissions(id),
    dispensed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost >= 0),
    notes TEXT
);
COMMENT ON TABLE pharmacy_dispensations IS 'Tracks medication supplies given to an inpatient (linked to an admission).';

-- Radiology exams
CREATE TABLE radiology_exams (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(id),
    requesting_doctor_id INT NOT NULL REFERENCES medical_staff(staff_id),
    exam_type VARCHAR(20) NOT NULL CHECK (exam_type IN ('XRAY', 'ULTRASOUND', 'MRI')),
    requested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    performed_at TIMESTAMPTZ,
    result_image_url TEXT,
    radiologist_report TEXT,
    status VARCHAR(20) DEFAULT 'PENDING'
);
COMMENT ON TABLE radiology_exams IS 'Radiology/ultrasound/MRI exams ordered by doctors.';

-- -------------------------------------------------------
-- 5. SIMPLE USER AUTHENTICATION
-- -------------------------------------------------------

-- Application users (linked to staff)
CREATE TABLE app_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    staff_id INT UNIQUE REFERENCES staff(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'NURSE', 'PHARMACY', 'RADIOLOGY', 'RECEPTION')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE app_users IS 'User accounts for staff to log into the system.';

-- -------------------------------------------------------
-- 6. AUDIT LOGS (SIMPLE PERO SUFICIENTE)
-- -------------------------------------------------------

-- Audit log table to track user actions
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INT REFERENCES app_users(id) ON DELETE SET NULL,
    action_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(20) NOT NULL CHECK (action_type IN ('INSERT', 'UPDATE', 'DELETE', 'LOGIN', 'VIEW')),
    table_name VARCHAR(50),
    record_id INT,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    notes TEXT
);
COMMENT ON TABLE audit_logs IS 'Tracks user actions for basic auditing.';

-- Index for performance
CREATE INDEX idx_audit_timestamp ON audit_logs(action_timestamp DESC);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_table ON audit_logs(table_name);

-- -------------------------------------------------------
-- 7. PATIENT MEDICAL HISTORY VIEW (Commented)
-- -------------------------------------------------------

/*
-- VIEW: patient_full_history
-- Purpose: Easy access to a patient's complete clinical record.
-- Usage: SELECT * FROM patient_full_history WHERE patient_id = ?;

CREATE OR REPLACE VIEW patient_full_history AS
SELECT 
    p.id AS patient_id,
    p.first_name || ' ' || p.last_name AS patient_name,
    jsonb_agg(DISTINCT jsonb_build_object(
        'type', 'visit',
        'date', v.visit_timestamp,
        'doctor', d.first_name || ' ' || d.last_name,
        'specialty', s.name,
        'diagnosis', v.diagnosis,
        'prescriptions', (
            SELECT jsonb_agg(jsonb_build_object(
                'medication', pr.medication_name,
                'dosage', pr.dosage,
                'frequency', pr.frequency,
                'start', pr.start_date,
                'duration_days', pr.duration_days
            ))
            FROM prescriptions pr
            WHERE pr.visit_id = v.id
        )
    )) FILTER (WHERE v.id IS NOT NULL) AS visits,
    jsonb_agg(DISTINCT jsonb_build_object(
        'type', 'surgery',
        'date', su.surgery_date,
        'procedure', su.procedure_type,
        'surgeon', ds.first_name || ' ' || ds.last_name,
        'theater', ot.theater_code,
        'floor', f.floor_number
    )) FILTER (WHERE su.id IS NOT NULL) AS surgeries,
    jsonb_agg(DISTINCT jsonb_build_object(
        'type', 'radiology',
        'exam', re.exam_type,
        'requested', re.requested_at,
        'performed', re.performed_at,
        'report', re.radiologist_report,
        'image_url', re.result_image_url
    )) FILTER (WHERE re.id IS NOT NULL) AS radiology_exams,
    (
        SELECT jsonb_agg(jsonb_build_object(
            'medication', pr.medication_name,
            'dosage', pr.dosage,
            'frequency', pr.frequency,
            'start_date', pr.start_date,
            'end_date', pr.start_date + (pr.duration_days || ' days')::INTERVAL
        ))
        FROM prescriptions pr
        JOIN visits v2 ON pr.visit_id = v2.id
        WHERE v2.patient_id = p.id
          AND pr.start_date + (pr.duration_days || ' days')::INTERVAL > CURRENT_DATE
    ) AS current_medications
FROM patients p
LEFT JOIN visits v ON v.patient_id = p.id
LEFT JOIN medical_staff md ON v.doctor_id = md.staff_id
LEFT JOIN staff d ON md.staff_id = d.id
LEFT JOIN medical_specialties s ON md.specialty_id = s.id
LEFT JOIN surgeries su ON su.patient_id = p.id
LEFT JOIN medical_staff ms ON su.primary_surgeon_id = ms.staff_id
LEFT JOIN staff ds ON ms.staff_id = ds.id
LEFT JOIN operating_theaters ot ON su.theater_id = ot.id
LEFT JOIN floors f ON ot.floor_id = f.id
LEFT JOIN radiology_exams re ON re.patient_id = p.id
GROUP BY p.id;

COMMENT ON VIEW patient_full_history IS 'Aggregated clinical history including visits, diagnoses, surgeries, radiology and current medication plan.';
*/