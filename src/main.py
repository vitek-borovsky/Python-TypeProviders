from sql_parsing.recordBuilder import RecordBuilder
from TypeProvider import SqlTypeProvider

import psycopg2

def run_raw(connection, querry):
    with connection.cursor() as c:
        c.execute(querry)
        c.fetchall()

def main():
    connection = psycopg2.connect(
        user="postgres",
        password="",
        # host="localhost",
        port="5432", # default port
        database="mydatabase"
    )
    querry0 = """
    seLECT C.CustomerID as CID
    FROM customers as C
    ;
    """

    querry1 = """
    seLECT Cart.CustomerID as CID
    FROM customercarts as Cart
    ;
    """

    # querry_wild = """
    # seLECT *
    # FROM employees
    # ;
    # """

    # querry_agregate = """
    # seLECT e1.col1, e1.col2, count(*)
    # FROM employees1 as e1
    # ;
    # """

    querry_join = """
        select Cus.Country as CCOUNT, Carts.CartName as CCNAME
        from customers as Cus
        join customercarts as Carts
        on Cus.CustomerID=Carts.CustomerID
    ;
    """

    querry_no_alias = """
        select customers.Country, customercarts.CartName
        from customers
        join customercarts
        on customers.CustomerID=customercarts.CustomerID
    ;
    """

    querry_nested = """
        select customers.Country, customercarts.CartName
        from customers
        join customercarts
        on customers.CustomerID= (Select count(*) From customers ) - 3
    ;
    """

    querry_complex =  """
        select Cus.Country, Carts.CartName as CCNAME
        from customers as Cus
        join customercarts as Carts
        on Cus.CustomerID=Carts.CustomerID
        where Cus.CustomerID > (Select count(*) From customers ) - 3
    ;
    """

    querry = querry_complex
    # run_raw(connection, querry)
    try:
        run_raw(connection, querry)
    except:
        print("querry invalid")
        return
    RecordBuilder.parse(connection, querry)
    connection.close()

if __name__ == '__main__':
    main()

