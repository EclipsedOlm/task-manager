import psycopg2

PASSKEY = "justiceforhina10"
link = f"postgresql://postgres:{PASSKEY}@db.lwolbogymjkydwumhepb.supabase.co:5432/postgres"
conn = psycopg2.connect(link)

cursor = conn.execute("SELECT * FROM test")
print(cursor)
