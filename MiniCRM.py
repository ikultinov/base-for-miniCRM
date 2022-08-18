import psycopg2

conn = psycopg2.connect(database='miniCRM', user='postgres', password='1375')


def create_db():
    """
    Функция, создающая структуру БД (таблицы)
    """
    with conn.cursor() as cur:
        # cur.execute("""
        #     DROP TABLE phone;
        #     DROP TABLE person;
        #     """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS person(
                person_id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                email VARCHAR(40) UNIQUE
                );
                """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phone(
                phone_id SERIAL PRIMARY KEY,
                person_id INTEGER NOT NULL REFERENCES person(person_id),
                phone_number BIGINT        
                );
                """)
        conn.commit()
    conn.close()


def person_add(f_name, l_name, email, phone=None):
    """
    Функция, позволяющая добавить нового клиента
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO person(first_name, last_name, email) 
                VALUES(%s, %s, %s) RETURNING person_id; 
                """, (f_name, l_name, email))
        person_id = cur.fetchone()[0]
        if phone:
            cur.execute("""
                INSERT INTO phone(person_id, phone_number)
                    VALUES(%s, %s);
                """, (person_id, phone))
        conn.commit()
        print("Клиент успешно добавлен!")
    conn.close()


def search_person(data_search):
    """
    Функция, позволяющая найти клиента по его данным
    (имени, фамилии, email-у или телефону)
    """
    with conn.cursor() as cur:
        if data_search.isdigit():
            cur.execute("""
                SELECT p.person_id, first_name, last_name, email, phone_number 
                    FROM person p
                    JOIN phone p2 ON p.person_id = p2.person_id
                    WHERE phone_number=%s;
                    """, (int(data_search),))
        else:
            cur.execute("""
                SELECT p.person_id, first_name, last_name, email, phone_number 
                    FROM person p
                    LEFT JOIN phone p2 ON p.person_id = p2.person_id
                    WHERE first_name=%s OR last_name=%s OR email=%s;
                    """, (data_search, data_search, data_search))
        print("Найдено:", cur.fetchall())
    conn.close()


def get_person_id(email):
    """
    Функция для поиска клиента по email
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT person_id FROM person WHERE email=%s;
            """, (email,))
        return cur.fetchone()
# нужен ли здесь conn.close()?


def phone_n_add(email):
    """
    Функция, позволяющая добавить телефон для существующего клиента
    """
    with conn.cursor() as cur:
        person_id = get_person_id(email)
        if person_id:
            cur.execute("""
                INSERT INTO phone(person_id, phone_number) VALUES(%s, %s); 
                """, (person_id, input("Введите телефон для добавления:")))
            conn.commit()
            print("Номер добавлен!")
        else:
            print("Клиент с таким email не найден.")
    conn.close()


def update_person(email):
    """
    Функция, позволяющая изменить данные о клиенте
    """
    with conn.cursor() as cur:
        person_id = get_person_id(email)
        if person_id:
            num_command = int(input("Выберите данные для изменения:\n"
                                    "имя - введите: 1;\n"
                                    "фамилию - введите: 2;\n"
                                    "email - введите: 3;\n"
                                    "телефон - введите: 4\n"
                                    "Введите:"))
            if num_command == 1:
                cur.execute("""
                    UPDATE person SET first_name=%s WHERE person_id=%s;
                    """, (input("Новое имя: "), person_id))
                conn.commit()
                print("Имя успешно изменено.")
            elif num_command == 2:
                cur.execute("""
                    UPDATE person SET last_name=%s WHERE person_id=%s;
                    """, (input("Новая фамилия: "), person_id))
                conn.commit()
                print("Фамилия успешно изменена.")
            elif num_command == 3:
                new_email = input("Новый email: ")
                temp_person_id = get_person_id(new_email)
                if temp_person_id:
                    print("Такой email уже используется.")
                else:
                    cur.execute("""
                        UPDATE person SET email=%s WHERE person_id=%s;
                        """, (new_email, person_id))
                    conn.commit()
                    print("email успешно изменен.")
            elif num_command == 4:
                cur.execute("""
                    UPDATE phone SET phone_number=%s WHERE person_id=%s;             
                    """, (input("Новый номер: "), person_id))
                conn.commit()
                print("Номер успешно изменен.")
        else:
            print("Клиент с таким email не найден.")
    conn.close()


def del_number(p_number):
    """
    Функция, позволяющая удалить телефон для существующего клиента
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT phone_number FROM phone WHERE phone_number=%s;
            """, (p_number,))
        if cur.fetchone():
            cur.execute("""
                DELETE FROM phone WHERE phone_number=%s;
                """, (p_number,))
            conn.commit()
            print("Номер удален.")
        else:
            print("Указанный номер не найден.")
    conn.close()


def del_person(email):
    """
    Функция, позволяющая удалить существующего клиента
    """
    with conn.cursor() as cur:
        person_id = get_person_id(email)
        cur.execute("""
            DELETE FROM phone WHERE person_id=%s;
            DELETE FROM person WHERE person_id=%s;
            """, (person_id, person_id))
        conn.commit()
        if person_id:
            print("Клиент удален.")
        else:
            print("Клиент с такой почтой не найден.")


if __name__ == '__main__':
    create_db()
    person_add(input("Введите имя:"), input("Введите фамилию:"),
               input("Введите email:"), input("Введите телефон:"))
    search_person(input("Введите запрос:"))
    phone_n_add(input("Введите email клиента:"))
    update_person(input("Введите email клиента:"))
    del_number(int(input("Введите телефон для удаления:")))
    del_person(input("Введите email клиента, которого хотите удалить:"))
