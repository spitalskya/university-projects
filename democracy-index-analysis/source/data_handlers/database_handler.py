from datetime import datetime
import sqlite3
from typing import Optional, Any
from pandas import DataFrame, read_sql_query
from urllib.request import pathname2url


class DatabaseHandler:
    """Class that is responsible for interacting with the database."""
    
    _db_file_name: str
    _conn: sqlite3.Connection | None       # connection to the database
    _cursor: sqlite3.Cursor | None         # cursor to the database
    
    studied_years: list[int] = list(range(2010, 2024))
    indicators_table_name: str = "indicators"
    countries_table_name: str = "countries"
    metrics_table_name: str = "metrics"
    
    
    def __init__(self, db_file_name: str) -> None:
        """Checks if can connect to the provided database.

        Args:
            db_file_name (str): name of the database file

        Raises:
            sqlite3.OperationalError: if connection to the database could not have been established
                probably because of missing database file
        """
        
        # try to establish connection with provided database file
        # if the file doesn't exist (or there occurs another error), throw sqlite3.OperationalError
        # The following code block was copied (and slightly adapted) from Stack Overflow:
        # https://stackoverflow.com/a/12932782
        # Original author: Martijn Pieters
        # Retrieved on: 22.3.2024
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(db_file_name))
            self._conn = sqlite3.connect(dburi, uri=True)
            self._conn.close()
        except sqlite3.OperationalError:
            # logging.exception(f"Couldn't connect to database {db_file_name}")
            raise sqlite3.OperationalError()
        
        self._db_file_name = db_file_name
        self._conn = None
        self._cursor = None
    
    
    def get_indicator_of_country(self, country_name: str, indicator_code: str) -> DataFrame:
        """Returns indicator values for the provided country

        Args:
            country_name (str): country to retrieve indicator from
            indicator_code (str): indicator to retrieve

        Returns:
            DataFrame: indicator values for provided country
        """        
        self._check_connected()
        
        country_code: str = self.get_country_code_from_name(country_name)
        
        indicator_values: dict[str, list[Any]] = {
            "Year": [],
            indicator_code: []
        }
        
        self._cursor.execute(
            f"""
            SELECT year, {indicator_code} FROM {self.metrics_table_name}
                WHERE countryCode = ?;
            """,
            (country_code,)
        )
        
        # create a DataFrame from the fetched values
        fetched_values: list[tuple[Any]] = self._cursor.fetchall()
        for fetched_value in fetched_values:
            if len(fetched_value) != 2: 
                continue
            
            year: Optional[int] = fetched_value[0]
            indicator_value: Optional[float] = fetched_value[1]
            if None in {year, indicator_value}:
                continue
            
            indicator_values["Year"].append(year)
            indicator_values[indicator_code].append(indicator_value)
            
        data: DataFrame = DataFrame(indicator_values)
        
        return data
    
    
    def get_country_code_from_name(self, country_name: str) -> str:
        """Converts country name to its code

        Args:
            country_name (str): country name to be converted

        Returns:
            str: resulting country code
        """
        self._check_connected()
        
        self._cursor.execute(
            f"SELECT countryCode FROM {self.countries_table_name} WHERE countryName = ?;",
            (country_name,))
        country_name: Optional[tuple[str]] = self._cursor.fetchone()
        if country_name:
            return country_name[0]
        return ""
    
    
    def get_country_name_from_code(self, country_code: str) -> str:
        """Converts country code to its name

        Args:
            country_code (str): country code to be converted

        Returns:
            str: resulting country name
        """
        self._check_connected()
        
        self._cursor.execute(
            f"SELECT countryName FROM {self.countries_table_name} WHERE countryCode = ?;",
            (country_code,))
        country_name: Optional[tuple[str]] = self._cursor.fetchone()
        if country_name:
            return country_name[0]
        return ""
    
    
    def get_indicator_code_from_name(self, indicator_name: str) -> str:
        """Converts indicator name to its code

        Args:
            indicator_name (str): indicator name to be converted

        Returns:
            str: resulting country code
        """
        self._check_connected()
        
        self._cursor.execute(
            f"SELECT indicatorCode FROM {self.indicators_table_name} WHERE indicatorName = ?;",
            (indicator_name,))
        indicator_code: Optional[tuple[str]] = self._cursor.fetchone()
        if indicator_code:
            return indicator_code[0]
        return ""
    
    
    def get_indicator_name_human_from_code(self, indicator_code: str) -> str:
        """Converts indicator code to its name in readable form

        Args:
            indicator_code (str): indicator code to be converted

        Returns:
            str: resulting indicator name
        """
        self._check_connected()
        
        self._cursor.execute(
            f"SELECT indicatorNameHuman FROM {self.indicators_table_name} WHERE indicatorCode = ?;",
            (indicator_code,))
        indicator_name: Optional[tuple[str]] = self._cursor.fetchone()
        if indicator_name:
            return indicator_name[0]
        return ""
    
    
    def get_all_countries(self) -> list[str]:
        """Get list of all country names

        Returns:
            list[str]: country names
        """
        self._check_connected()
        
        self._cursor.execute(f"SELECT countryName from {self.countries_table_name}")
        
        return [country[0] for country in self._cursor.fetchall() if country]
    
    
    def get_all_indicator_codes(self) -> list[str]:
        """Get list of all indicator codes

        Returns:
            list[str]: indicator codes
        """
        self._check_connected()
        
        self._cursor.execute(f"SELECT indicatorCode from {self.indicators_table_name}")
        
        return [code[0] for code in self._cursor.fetchall() if code]
    
    
    def get_whole_metrics(self) -> DataFrame:
        """Returns whole metrics table as a DataFrame

        Returns:
            DataFrame: metrics table in DataFrame form
        """
        self._check_connected()
        
        data: DataFrame = read_sql_query(
            f"SELECT * FROM {self.metrics_table_name}",
            self._conn
            )
        
        return data
    
    
    def get_indicator_legend(self) -> list[dict[str, str]]:
        """Returns indicator conversion table from code to readable name

        Returns:
            list[dict[str, str]]: indicator conversion table
        """
        self._check_connected()
        
        self._cursor.execute(
            f"SELECT indicatorCode, indicatorNameHuman FROM {self.indicators_table_name};"
            )
        
        legend: list[dict[str, str]] = [
            {"code": pair[0], "name": pair[1]} for pair in self._cursor.fetchall()
            if pair is not None and len(pair) == 2    
        ]
        
        return legend
    
    
    def open_connection(self) -> None:
        """Try to connect to the DB provided in the constructor

        Raises:
            sqlite3.OperationalError: if connection to the database could not have been established
        """
        
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(self._db_file_name))
            self._conn = sqlite3.connect(dburi, uri=True)
            self._cursor = self._conn.cursor()
        except sqlite3.OperationalError:
            # logging.exception(f"Couldn't connect to database {db_file_name}")
            raise sqlite3.OperationalError()
        

    def close_connection(self) -> None:
        """Closes the connection to the DB"""
        
        if self._conn:
            self._conn.close()
        self._conn = None
        self._cursor = None
    
    
    def _check_connected(self) -> None:
        """Checks whether the connection to the DB is established

        Raises:
            sqlite3.OperationalError: when the connection is not established
        """
        
        if not self._conn:
            raise sqlite3.OperationalError("Not connected to the database")


def main() -> None:
    """Just for testing purposes"""
    db: DatabaseHandler = DatabaseHandler("data/db.sqlite")
    db.open_connection()
    
    print(db.get_all_countries())
    #print(db.get_indicator_of_country("Uzbekistan", "GNI"))
    #db.get_all_countries()
    #db.get_whole_metrics()
    db.close_connection()


if __name__ == "__main__":
    main()
