-- Function and trigger to prevent overlapping surgeries in the same operating theater
CREATE OR REPLACE FUNCTION check_surgery_overlap()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM surgeries
        WHERE theater_id = NEW.theater_id
          AND surgery_date = NEW.surgery_date
          AND (start_time, end_time) OVERLAPS (NEW.start_time, NEW.end_time)
          AND surgery_id != COALESCE(NEW.surgery_id, -1)
    ) THEN
        RAISE EXCEPTION 'There is already a surgery scheduled in that operating room at the same time.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_prevent_surgery_overlap
BEFORE INSERT OR UPDATE ON surgeries
FOR EACH ROW EXECUTE FUNCTION check_surgery_overlap();

-- Function and trigger to validate that an assigned nurse references an existing doctor
CREATE OR REPLACE FUNCTION validate_nurse_assignment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.assigned_doctor_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM medical_staff WHERE staff_id = NEW.assigned_doctor_id) THEN
            RAISE EXCEPTION 'The assigned doctor does not exist in medical_staff';
        END IF;
    END IF;
    IF NEW.assigned_floor_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM floors WHERE floor_id = NEW.assigned_floor_id) THEN
            RAISE EXCEPTION 'The assigned floor does not exist';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_validate_nurse_assignment
BEFORE INSERT OR UPDATE ON nursing_staff
FOR EACH ROW EXECUTE FUNCTION validate_nurse_assignment();
