from database import get_db_connection

def is_admin(user_id: int) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 'admin'