#TODO better name


class DatabaseDeamon:
    @staticmethod
    def __database_structure_querry_maker(table_name: str) -> str: # TODO robust against injection
        return f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{ table_name }'; """

    @staticmethod
    def querry(connection, table_name: str) -> dict[ str, str ]:
        querry = DatabaseDeamon.__database_structure_querry_maker(table_name)
        with connection.cursor() as cursor:
            cursor.execute(querry)
            list_view = cursor.fetchall()
        return { column_name : data_type for column_name, data_type in list_view }
