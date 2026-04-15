DROP database hospital_management_db;
-- First user (admin)
INSERT INTO STAFF (
    national_id,
    ssn,
    first_name,
    last_name,
    birth_date,
    phone,
    email,
    address,
    hire_date,
    staff_type
) VALUES (
    'X090900990V',
    '123-45-6789',
    'Yossef',
    'Errazik',
    '2007-07-08',
    '+1234567890',
    'yosseferrazik@hsp.com',
    'Calle Falsa 123, Ciudad, País',
    CURRENT_DATE,
    'GENERAL'  
);

INSERT INTO GENERAL_STAFF (
    staff_id,
    job_type
) VALUES (
    (SELECT staff_id FROM STAFF WHERE national_id = 'X090900990V'),
    'SYSTEM_ADMINISTRATOR'
);

SELECT * FROM STAFF;