import psycopg2
from psycopg2 import sql
from datetime import datetime

host="analytics_db" # IP server PostgreSQL
port=5432
user="user_metabase"
password="secure_password"
dbname="metabase"

def insert_data_postgres(time_value, price, trade_type):
    """
    Chèn 1 bản ghi vào bảng 'trades' trong PostgreSQL.
    Bảng có 3 cột: time (TIMESTAMP), price (FLOAT), type (TEXT).
    """
    print("host :", host)
    print("port :", port)
    print("dbname :", dbname)
    print("user :", user)
    print("password :", password)
    conn = None
    try:
        # 1️⃣ Kết nối tới PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cur = conn.cursor()

        # 2️⃣ Tạo bảng nếu chưa có
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            time FLOAT NOT NULL,             -- epoch time (float)
            datetime TIMESTAMP NOT NULL,     -- thời gian thật dạng datetime
            price FLOAT NOT NULL,
            type TEXT NOT NULL
        );
        """
        cur.execute(create_table_query)

        # 3️⃣ Câu lệnh insert
        insert_query = sql.SQL("""
            INSERT INTO trades (time, datetime, price, type)
            VALUES (%s, TO_TIMESTAMP(%s), %s, %s)
        """)
        # 4️⃣ Thực thi
        cur.execute(insert_query, (time_value, time_value, price, trade_type))

        # 5️⃣ Commit thay đổi
        conn.commit()

        print("✅ Insert thành công!")

    except Exception as e:
        print("❌ Lỗi khi insert dữ liệu:", e)

    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    insert_data_postgres(
        host="http://172.16.206.40/",   # IP server PostgreSQL
        port=5432,
        dbname="mydb",
        user="admin",
        password="123456",
        time_value=int(datetime.now().timestamp()),
        price=68940,
        trade_type="real"
    )
