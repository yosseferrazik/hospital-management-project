-- Initial data script: create a system administrator staff and user
-- Generated: 2026-05-13

-- Ensure pgcrypto is available for secure password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Insert staff record for Yossef Errazik and create an ADMIN application user
WITH new_staff AS (
	INSERT INTO STAFF (
		national_id, first_name, last_name, birth_date, phone, ssn, email, address, staff_type
	) VALUES (
		'000000000', 'Yossef', 'Errazik', '1988-06-15', '+34-600000000', NULL, 'yossef.errazik@example.com', 'System Administrator', 'GENERAL'
	)
	RETURNING staff_id
),
general_row AS (
	INSERT INTO GENERAL_STAFF (staff_id, job_type)
	SELECT ns.staff_id, 'System Administrator'
	FROM new_staff ns
)
INSERT INTO APP_USERS (username, password_hash, staff_id, role, is_active, created_at)
SELECT
	'yossef',
	crypt('ChangeMePleaseChange!', gen_salt('bf')),
	ns.staff_id,
	'ADMIN',
	TRUE,
	CURRENT_TIMESTAMP
FROM new_staff ns;

-- NOTE: The inserted password is the bcrypt hash of 'ChangeMePleaseChange!'.
-- Change the password on first login or update the script to use a different secret.

SELECT * FROM audit_logs;