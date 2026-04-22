import psycopg2

# Put it into some secret variable later on
PASSKEY = "justiceforhina10" # POOR HINA I KNOW WHAT YOU FEEL

# PLEASE PLEASE PLEASE DON'T TOUCH THIS IT WORKS!!!
# Apparently connecting with IPv6 (which is what we all do apparently) only works with this "pooling"
# And DOES NOT work with Direct Connection (which uses IPv4 I think - we didn't pay for this)
link = "postgresql://postgres.lwolbogymjkydwumhepb:{}@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres".format(PASSKEY) # Keeping passkeys secret!
conn = psycopg2.connect(link) # Connect to the supabase db
cursor = conn.cursor() # The cursor object is the one that executes the SQL code

# testing sql query
# note that psycopg2 has slightly diff syntax
cursor.execute("SELECT * FROM test")
print(cursor.fetchall())
