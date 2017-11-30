import MySQLdb.cursors


def interface():
    done = False
    while not done:
        print("Queries:")
        print("=========")
        print("0. Forgotten bag in car with AN (query 1)")
        print("1. Percent of busy taxis (query 3)")
        print("2. Double charged client (query 4)")
        print("3. Least used taxis (query 7)")
        print("4. Research on location of residence (query 8)")
        choice = input("Enter the number of the required query (0-4): ")
        try:
            choice = int(choice)
        except ValueError:
            print("Please provide a number between 0 and 4")
            continue
        if 0 <= choice <= 4:
            done = True
        else:
            print("Please provide a number between 0 and 4")
    execute(choice)


def execute(choice):
    query = str()
    title = str()
    variables = dict()
    if choice == 0:
        title = "Potential car IDs for customer_id 371 on 28.11.2017 (\"today\"):"
        query = """
        SELECT Car.car_id
        FROM Ordering
        LEFT JOIN Car ON Car.car_id = Ordering.car_id
        WHERE Ordering.date = "2017-11-28" AND Ordering.customer_id = 371 AND Car.color = "red" AND Car.plate_series LIKE "AN%";
        """
    elif choice == 2:
        title = "IDs of double charged orders for user 371"
        query = """
            SELECT Payment.order_id
            FROM Payment
            LEFT JOIN Ordering ON Ordering.order_id = Payment.order_id
            WHERE Ordering.customer_id = 371 AND Ordering.date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()
            GROUP BY Payment.order_id
            HAVING COUNT(Payment.order_id) > 1;
            """
    elif choice == 3:
        title = "IDs of 10% of least used cars:"
        query = """
        SET @totalCars = (SELECT COUNT(car_id)/10 as count FROM Car);

        PREPARE STMT FROM 'SELECT DISTINCT Car.car_id
        FROM Car
        LEFT JOIN Ordering ON Ordering.car_id = Car.car_id
        WHERE Ordering.date BETWEEN DATE_SUB(NOW(), INTERVAL 3 MONTH) AND NOW()   
        GROUP BY car_id
        ORDER BY count(*) ASC
        LIMIT ?';
        
        EXECUTE STMT USING @totalCars;
        """
    elif choice == 4:
        done = False
        inp = str()
        while not done:
            inp = str(input("Please enter a date in form of YYYY-MM-DD: "))
            done = True

        variables["input"] = inp
        title = "Research results:"
        query = """
        SELECT DISTINCT O.customer_id AS UserId, COUNT(C.charge_id) AS Amount
        FROM Ordering O, Charge C
        WHERE O.car_id = C.car_id 
        AND %(input)s <= O.date
        AND DATE_ADD(%(input)s, INTERVAL 1 MONTH) >= O.date 
        AND O.date = C.date
        GROUP BY O.customer_id;
        """
    db = MySQLdb.connect("localhost", "root", "mysql")
    x = db.cursor()
    queries = query.split(";")[:-1]

    if len(variables) == 0:
        variables = None

    x.execute("USE InnoProject3;")
    for c in range(len(queries) - 1):
        x.execute(queries[c], variables)
    x.execute(queries[-1], variables)
    print(title)
    out = str()
    for name in [i[0] for i in x.description]:
        out += name + " "
    print(out)
    for c in range(x.rowcount):
        row = x.fetchone()
        out = str()
        for c2 in range(len(row)):
            out += str(row[c2]) + " "
        print(out)

    db.close()


if __name__ == '__main__':
    interface()
