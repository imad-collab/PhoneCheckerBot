import oracledb
from config.settings import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN


# Create a reusable DB connection
def get_connection():
    try:
        conn = oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=ORACLE_DSN
        )
        return conn
    except Exception as e:
        print("❌ Oracle DB connection failed:", e)
        return None


# Insert a phone lookup result
def insert_lookup(number, carrier, country, scam_report, decision):
    conn = get_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO phone_lookups (phone_number, carrier, country, scam_report, decision)
                VALUES (:1, :2, :3, :4, :5)
            """, (number, carrier, country, scam_report, decision))
            conn.commit()
    except Exception as e:
        print("❌ Insert failed:", e)
    finally:
        conn.close()


# Fetch the most recent lookup for a number
def get_previous_lookup(number):
    conn = get_connection()
    if conn is None:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT decision, checked_at
                FROM phone_lookups
                WHERE phone_number = :1
                ORDER BY checked_at DESC
                FETCH FIRST 1 ROWS ONLY
            """, (number,))
            row = cursor.fetchone()
        return row
    except Exception as e:
        print("❌ Fetch failed:", e)
        return None
    finally:
        conn.close()
