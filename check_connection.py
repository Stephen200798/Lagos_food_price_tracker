import mssql_python

connection_string = (
    "Server=localhost\\SQLEXPRESS;"
    "Database=LagosFoodPriceTracker;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

connection = mssql_python.connect(connection_string)
cursor = connection.cursor()

cursor.execute("SELECT DB_NAME(), SUSER_SNAME();")
result = cursor.fetchone()

print("Connected to database:", result[0])
print("Signed in as:", result[1])

cursor.close()
connection.close()