import psycopg2


def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        database="cryptoflow",
        user="cryptoflow",
        password="cryptoflow"
    )


if __name__ == "__main__":
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM assets;")

    count = cursor.fetchone()[0]

    print("✅ PostgreSQL connection successful!")
    print(f"📊 Assets in database: {count}")

    cursor.close()
    connection.close()