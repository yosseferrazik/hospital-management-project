-- ====================================================================
-- HOSPITAL MANAGEMENT SYSTEM - SECURITY IMPLEMENTATION SCRIPT
-- ====================================================================
-- This script creates database roles, sets privileges, enables RLS,
-- and creates audit triggers. It must be run as a superuser.
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. CREATE DATABASE ROLES (Application Users)
-- --------------------------------------------------------------------
-- These roles are used by the Python/Tkinter application to connect.
-- Passwords will be set separately using ALTER ROLE.
-- --------------------------------------------------------------------

-- Administrative role (full access)
CREATE ROLE app_admin WITH LOGIN CONNECTION LIMIT 5;
COMMENT ON ROLE app_admin IS 'Application role for system administrators';

-- Medical staff role (doctors, surgeons)
CREATE ROLE app_doctor WITH LOGIN CONNECTION LIMIT 50;
COMMENT ON ROLE app_doctor IS 'Application role for doctors and medical staff';

-- Nursing staff role
CREATE ROLE app_nurse WITH LOGIN CONNECTION LIMIT 100;
COMMENT ON ROLE app_nurse IS 'Application role for nursing staff';

-- Receptionist role (front-desk)
CREATE ROLE app_receptionist WITH LOGIN CONNECTION LIMIT 10;
COMMENT ON ROLE app_receptionist IS 'Application role for receptionists';

-- General staff role (pharmacy, maintenance, etc.)
CREATE ROLE app_staff WITH LOGIN CONNECTION LIMIT 30;
COMMENT ON ROLE app_staff IS 'Application role for general hospital staff';

-- --------------------------------------------------------------------
-- 2. GRANT USAGE ON SCHEMA AND SEQUENCES
-- --------------------------------------------------------------------
GRANT USAGE ON SCHEMA public TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;

-- All roles need access to sequences for INSERT operations on serial columns
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;

-- --------------------------------------------------------------------
-- 3. TABLE PRIVILEGES ACCORDING TO RBAC MATRIX
-- --------------------------------------------------------------------

-- ========== PATIENTS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON patients TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON patients TO app_doctor;
GRANT SELECT, UPDATE (phone, email, address, emergency_contact_name, emergency_contact_phone, allergies) ON patients TO app_nurse;
GRANT SELECT, INSERT, UPDATE, DELETE ON patients TO app_receptionist;
GRANT SELECT (patient_id, first_name, last_name, room_number) ON patients TO app_staff;  -- Limited view via view (created later)

-- ========== VISITS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON visits TO app_admin, app_doctor;
GRANT SELECT, INSERT ON visits TO app_nurse, app_receptionist;

-- ========== SCHEDULED_APPOINTMENTS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON scheduled_appointments TO app_admin, app_doctor, app_receptionist;
GRANT SELECT, UPDATE (status) ON scheduled_appointments TO app_nurse;

-- ========== PRESCRIPTIONS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON prescriptions TO app_admin, app_doctor;
GRANT SELECT ON prescriptions TO app_nurse;
REVOKE ALL ON prescriptions FROM app_receptionist, app_staff;

-- ========== MEDICATIONS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON medications TO app_admin;
GRANT SELECT ON medications TO app_doctor, app_nurse, app_staff;  -- app_staff for pharmacy

-- ========== ADMISSIONS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON admissions TO app_admin, app_doctor;
GRANT SELECT, INSERT, UPDATE (actual_discharge_date) ON admissions TO app_nurse;
REVOKE ALL ON admissions FROM app_receptionist, app_staff;

-- ========== ROOMS / FLOORS ==========
GRANT SELECT ON floors TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;
GRANT SELECT ON rooms TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;
GRANT INSERT, UPDATE, DELETE ON floors, rooms TO app_admin;

-- ========== OPERATING_THEATERS / MEDICAL_DEVICES ==========
GRANT SELECT ON operating_theaters TO app_admin, app_doctor, app_nurse;
GRANT SELECT ON medical_devices TO app_admin, app_doctor, app_nurse;
GRANT INSERT, UPDATE, DELETE ON operating_theaters, medical_devices TO app_admin;

-- ========== SURGERIES ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON surgeries TO app_admin, app_doctor;
GRANT SELECT, INSERT ON surgeries TO app_nurse;  -- nurses can create surgery records for scheduling
GRANT SELECT, INSERT, UPDATE, DELETE ON surgery_assistants TO app_admin, app_doctor;
GRANT SELECT, INSERT ON surgery_assistants TO app_nurse;

-- ========== RADIOLOGY_EXAMS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON radiology_exams TO app_admin;
GRANT SELECT, INSERT, UPDATE ON radiology_exams TO app_doctor;  -- doctors request and view
GRANT SELECT, UPDATE (performed_at, status, result_image_url) ON radiology_exams TO app_nurse;
REVOKE ALL ON radiology_exams FROM app_receptionist, app_staff;

-- ========== PHARMACY_DISPENSATIONS ==========
GRANT SELECT, INSERT, UPDATE, DELETE ON pharmacy_dispensations TO app_admin;
GRANT SELECT ON pharmacy_dispensations TO app_doctor, app_nurse;
GRANT ALL ON pharmacy_dispensations TO app_staff;  -- pharmacy staff manage

GRANT SELECT, INSERT, UPDATE, DELETE ON dispensation_items TO app_admin;
GRANT SELECT ON dispensation_items TO app_doctor, app_nurse;
GRANT ALL ON dispensation_items TO app_staff;

-- ========== STAFF & MEDICAL_SPECIALTIES ==========
GRANT SELECT ON staff TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;
GRANT INSERT, UPDATE, DELETE ON staff TO app_admin;
GRANT SELECT ON medical_staff, nursing_staff, general_staff TO app_admin, app_doctor, app_nurse, app_receptionist;
GRANT INSERT, UPDATE, DELETE ON medical_staff, nursing_staff, general_staff TO app_admin;

GRANT SELECT ON medical_specialties TO app_admin, app_doctor, app_nurse;
GRANT INSERT, UPDATE, DELETE ON medical_specialties TO app_admin;

-- ========== APP_USERS ==========
GRANT SELECT ON app_users TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;
GRANT UPDATE (password_hash, last_login) ON app_users TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;
GRANT INSERT, DELETE ON app_users TO app_admin;

-- ========== AUDIT_LOGS ==========
GRANT SELECT ON audit_logs TO app_admin;
REVOKE ALL ON audit_logs FROM app_doctor, app_nurse, app_receptionist, app_staff;

-- --------------------------------------------------------------------
-- 4. ROW LEVEL SECURITY (RLS) POLICIES
-- --------------------------------------------------------------------
-- Enable RLS on tables that require fine‑grained access control.
-- --------------------------------------------------------------------

-- Enable RLS on PATIENTS
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;

-- Policy for nurses: only see patients currently admitted to a room on their assigned floor
CREATE POLICY nurse_patient_access ON patients
    FOR SELECT
    TO app_nurse
    USING (
        EXISTS (
            SELECT 1 FROM admissions a
            JOIN rooms r ON a.room_id = r.room_id
            JOIN nursing_staff ns ON ns.assigned_floor_id = r.floor_id
            WHERE a.patient_id = patients.patient_id
              AND a.actual_discharge_date IS NULL
              AND ns.staff_id = current_setting('app.current_staff_id')::INTEGER
        )
    );

-- Policy for doctors and admin: unrestricted (but still subject to RLS)
CREATE POLICY doctor_admin_patient_access ON patients
    FOR ALL
    TO app_doctor, app_admin
    USING (true);

-- Policy for receptionists: unrestricted (they need full patient view)
CREATE POLICY receptionist_patient_access ON patients
    FOR ALL
    TO app_receptionist
    USING (true);

-- Policy for general staff: only see name and room (achieved via column grants, but RLS can further restrict)
CREATE POLICY staff_patient_access ON patients
    FOR SELECT
    TO app_staff
    USING (true);  -- column grants already limit what they can select

-- ========== RLS on ADMISSIONS ==========
ALTER TABLE admissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY nurse_admission_access ON admissions
    FOR ALL
    TO app_nurse
    USING (
        room_id IN (
            SELECT r.room_id FROM rooms r
            JOIN nursing_staff ns ON ns.assigned_floor_id = r.floor_id
            WHERE ns.staff_id = current_setting('app.current_staff_id')::INTEGER
        )
    );

CREATE POLICY doctor_admin_admission_access ON admissions
    FOR ALL
    TO app_doctor, app_admin
    USING (true);

-- --------------------------------------------------------------------
-- 5. HELPER FUNCTIONS FOR APPLICATION CONTEXT
-- --------------------------------------------------------------------
-- The application will set a session variable 'app.current_user_id' and
-- 'app.current_staff_id' upon connection. These functions retrieve them.
-- --------------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_current_app_user_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE(NULLIF(current_setting('app.current_user_id', true), '')::INTEGER, -1);
EXCEPTION
    WHEN OTHERS THEN RETURN -1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_current_app_user_id() IS 'Returns the user_id from app_users of the currently connected application user.';

CREATE OR REPLACE FUNCTION get_current_staff_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE(NULLIF(current_setting('app.current_staff_id', true), '')::INTEGER, -1);
EXCEPTION
    WHEN OTHERS THEN RETURN -1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_current_staff_id() IS 'Returns the staff_id associated with the currently connected application user.';

-- Grant execution to all roles
GRANT EXECUTE ON FUNCTION get_current_app_user_id() TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;
GRANT EXECUTE ON FUNCTION get_current_staff_id() TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;

-- --------------------------------------------------------------------
-- 6. AUDIT TRIGGER FUNCTION AND TRIGGERS
-- --------------------------------------------------------------------
-- Automatically logs all DML operations on critical tables into AUDIT_LOGS.
-- --------------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INTEGER;
    v_action_type VARCHAR(50);
    v_old_data TEXT;
    v_new_data TEXT;
BEGIN
    -- Get current application user ID from session variable
    v_user_id := get_current_app_user_id();
    
    -- Determine action type
    CASE TG_OP
        WHEN 'INSERT' THEN
            v_action_type := 'INSERT';
            v_new_data := row_to_json(NEW)::TEXT;
        WHEN 'UPDATE' THEN
            v_action_type := 'UPDATE';
            v_old_data := row_to_json(OLD)::TEXT;
            v_new_data := row_to_json(NEW)::TEXT;
        WHEN 'DELETE' THEN
            v_action_type := 'DELETE';
            v_old_data := row_to_json(OLD)::TEXT;
    END CASE;

    -- Insert audit record
    INSERT INTO audit_logs (
        user_id,
        action_timestamp,
        action_type,
        table_name,
        record_id,
        old_data,
        new_data,
        ip_address,
        notes
    ) VALUES (
        v_user_id,
        CURRENT_TIMESTAMP,
        v_action_type,
        TG_TABLE_NAME,
        COALESCE(NEW.patient_id, OLD.patient_id, 
                 NEW.visit_id, OLD.visit_id,
                 NEW.prescription_id, OLD.prescription_id,
                 NEW.admission_id, OLD.admission_id,
                 NEW.surgery_id, OLD.surgery_id,
                 NEW.appointment_id, OLD.appointment_id,
                 NEW.dispensation_id, OLD.dispensation_id,
                 NEW.exam_id, OLD.exam_id,
                 NULL),
        v_old_data,
        v_new_data,
        inet_client_addr(),
        'Automated audit trail'
    );

    RETURN NULL;  -- for AFTER triggers, return value is ignored
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION audit_trigger_function() IS 'Generic audit trigger function logging changes to AUDIT_LOGS.';

-- Attach triggers to sensitive tables

CREATE TRIGGER audit_patients
    AFTER INSERT OR UPDATE OR DELETE ON patients
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_visits
    AFTER INSERT OR UPDATE OR DELETE ON visits
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_prescriptions
    AFTER INSERT OR UPDATE OR DELETE ON prescriptions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_admissions
    AFTER INSERT OR UPDATE OR DELETE ON admissions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_surgeries
    AFTER INSERT OR UPDATE OR DELETE ON surgeries
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_radiology_exams
    AFTER INSERT OR UPDATE OR DELETE ON radiology_exams
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_pharmacy_dispensations
    AFTER INSERT OR UPDATE OR DELETE ON pharmacy_dispensations
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_scheduled_appointments
    AFTER INSERT OR UPDATE OR DELETE ON scheduled_appointments
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- --------------------------------------------------------------------
-- 7. ADDITIONAL SECURITY MEASURES
-- --------------------------------------------------------------------

-- Prevent unauthenticated connections from modifying audit logs (already revoked)
-- Set default privileges for future tables (optional)
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_admin, app_doctor, app_nurse, app_receptionist, app_staff;

-- --------------------------------------------------------------------
-- 8. VIEW FOR LIMITED PATIENT INFORMATION (STAFF ROLE)
-- --------------------------------------------------------------------
CREATE OR REPLACE VIEW patient_directory AS
SELECT 
    p.patient_id,
    p.first_name,
    p.last_name,
    r.room_number
FROM patients p
LEFT JOIN admissions a ON p.patient_id = a.patient_id AND a.actual_discharge_date IS NULL
LEFT JOIN rooms r ON a.room_id = r.room_id;

GRANT SELECT ON patient_directory TO app_staff;
COMMENT ON VIEW patient_directory IS 'Limited patient view for general staff showing only name and current room.';

-- --------------------------------------------------------------------
-- END OF SCRIPT
-- --------------------------------------------------------------------