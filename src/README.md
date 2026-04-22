with conn.cursor() as cur:
    cur.execute("SET app.current_user_id = %s", (user_id,))
    cur.execute("SET app.current_staff_id = %s", (staff_id,))