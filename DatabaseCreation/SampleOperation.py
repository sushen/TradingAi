import sqlite3

connection = sqlite3.connect('../backups_miracle.db')

cursor = connection.cursor()

# Add New Table
cursor.execute("""CREATE TABLE IF NOT EXISTS login(
                username text,
                password text
                )""")

# Add New Table
cursor.execute("""CREATE TABLE IF NOT EXISTS all_fb_group(
                group_name text,
                group_url text
                )""")

# Add New Table
cursor.execute("""CREATE TABLE IF NOT EXISTS all_fb_user(
                user_name text,
                user_url text,
                user_country text
                )""")

# # Add New Table Column
cursor.execute("ALTER TABLE all_fb_user ADD user_sex text")
# cursor.execute("ALTER TABLE all_fb_user ADD user_race text")

# # Delete Table Column
# cursor.execute("ALTER TABLE all_fb_user DROP COLUMN user_race")
# cursor.execute("ALTER TABLE all_fb_user DROP COLUMN new_column_name")

# # Edit Table Column
# cursor.execute("ALTER TABLE all_fb_user RENAME  COLUMN user_url TO user_address")


connection.commit()
connection.close()
