from etl.config import POSTGRES_URLS
import psycopg2

def main():
    conn = psycopg2.connect(POSTGRES_URLS["bcp_db"].replace("postgresql+psycopg2", "postgresql"))
    cur = conn.cursor()
    cur.execute('SELECT "Saldo" FROM "Cuenta" LIMIT 1')
    res = cur.fetchone()
    print("BCP DB Saldo:", res[0])

if __name__ == '__main__':
    main()
