import sqlite3

connection = sqlite3.connect('miracle.db')
cursor = connection.cursor()
cursor.execute("SELECT * FROM facebook_profile")



def remove_duplicate(records):
    # print(count)
    for record in records:
        singleRecord = record
        # Find All Duplicate
        cursor.execute("SELECT * FROM facebook_profile GROUP BY profile_link HAVING COUNT(*) > 1;")
        records = cursor.fetchall()
        try:
            for pk in records[1]:
                duplicate_pk = (records[1])[0]
                profile_link = (records[1])[1]
                print(duplicate_pk)
                print(profile_link)
                # print(input("Press any Key: "))
                cursor.execute("DELETE FROM facebook_profile WHERE _pk_facebook_profile=?", (duplicate_pk,))
                break
            break
        except:
            print("There are no Duplicate in the list")
            break


if __name__ == '__main__':
    count = 0
    records = cursor.fetchall()
    while count < len(records):
        count = count + 1
        remove_duplicate(records)
        print(count)

    connection.commit()
    connection.close()


 