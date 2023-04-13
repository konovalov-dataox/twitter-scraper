class NoDbConnect(Exception):
    def __init__(self, db_locator: str):
        self._db_locator: str = db_locator

    def __repr__(self):
        return f"Can't connect to database server by locator {self._db_locator}"

    def __str__(self):
        return f"Can't connect to database server by locator {self._db_locator}"


class EmptyTableName(Exception):
    def __repr__(self):
        return f"Destination error log table name is empty!"

    def __str__(self):
        return f"Destination error log table name is empty!"


class TableCreate(Exception):

    def __init__(self, table_name: str):
        self._table_name: str = table_name

    def __repr__(self):
        return f"Can't create table {self._table_name}"

    def __str__(self):
        return f"Can't create table {self._table_name}"


class TablePartitionCreate(Exception):

    def __init__(self, table_name: str):
        self._table_name: str = table_name

    def __repr__(self):
        return f"Can't create partition for table {self._table_name}"

    def __str__(self):
        return f"Can't create partition for table {self._table_name}"


class TableNotFound(Exception):

    def __init__(self, table_name: str):
        self._table_name: str = table_name

    def __repr__(self):
        return f"Can't found just created table {self._table_name} in list!"

    def __str__(self):
        return f"Can't found just created table {self._table_name} in list!"


class InsertLogMessage(Exception):
    pass
