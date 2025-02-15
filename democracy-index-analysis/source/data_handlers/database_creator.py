from typing import Optional
from urllib.request import pathname2url
import sqlite3
import pandas as pd


class DatabaseCreator:
    """Class responsible for the creation of the database"""
    
    path_to_db: str
    country_code_to_name: dict[str, str]
    
    _conn: Optional[sqlite3.Connection]
    _cursor: Optional[sqlite3.Cursor]
    
    
    indicator_to_code: dict[str, str] = {
        "democracy-index-eiu" : "DCI",
        "education" : "EDU",
        "GDP" : "GDP",
        "gini-index" : "GNI",
        "life-expectancy" : "LEX",
        "military-expenditure" : "MIE",
        "research-and-development-expenditure" : "RDE"  
    }
    
    indicators_table_name: str = "indicators"
    countries_table_name: str = "countries"
    metrics_table_name: str = "metrics"
    
    
    def __init__(self, path_to_db: str) -> None:
        """Sets necessary fields

        Args:
            path_to_db (str): path to the database to connect to
        """
        self.path_to_db = path_to_db
        self.country_code_to_name = {}
        self._conn = None
        self._cursor = None
        
    
    def load_country_code_to_name_conversion(self, world_bank_data_csv: str) -> None:
        """Create conversion dictionary from country code to country name

        Args:
            world_bank_data_csv (str): dataset from the world bank to extract conversion from
        """
        data: pd.DataFrame = pd.read_csv(world_bank_data_csv)
        
        country_code_col_name: str = "Country Code"
        country_name_col_name: str = "Country Name"
        
        self.country_code_to_name = dict(zip(
            data[country_code_col_name], 
            data[country_name_col_name]
            ))
    
    
    def create_tables(self) -> None:
        """Create all the necessary tables"""
        self._create_countries_table()
        self._fill_countries_table()
        
        self._create_indicators_table()
        self._fill_indicators_table()
        
        self._create_metrics_table()
        self._fill_metrics_table()
    
    
    def add_world_bank_dataset(self, path_to_csv: str, indicator_name: str) -> None:
        """Adds data from the World bank to the database

        Args:
            path_to_csv (str): path to the world bank dataset csv
            indicator_name (str): name of the indicator that is in the dataset
        """        
        
        self._connect()
        
        data: pd.DataFrame = pd.read_csv(path_to_csv)
        indicator_code: str = self.indicator_to_code[indicator_name]
        
        country_code_col_name: str = "Country Code"
        for _, row in data.iterrows():
            country_code: str = row[country_code_col_name]
            
            year_col: str
            for year_col in data.columns:
                # update only necessary values
                if not year_col.isdigit():
                    continue
                
                self._cursor.execute(
                    f"""
                    UPDATE metrics 
                    SET {indicator_code} = ?
                    WHERE countryCode = ? AND year = ?;
                    """,
                    (row[year_col], country_code, int(year_col)))
        
        self._conn.commit()
        self._disconnect()
        
        
    def add_democracy_index_dataset(self, path_to_csv: str, indicator_name: str) -> None: 
        """Adds democracy index data to the database

        Args:
            path_to_csv (str): path to the democracy index dataset csv
            indicator_name (str): name of the indicator that is in the dataset
        """   
        self._connect()
        
        data: pd.DataFrame = pd.read_csv(path_to_csv)
        indicator_code: str = self.indicator_to_code[indicator_name]
        
        country_code_col_name: str = "Code"
        year_col_name: str = "Year"
        democracy_index_col_name: str = "Democracy score"
        
        for _, row in data.iterrows():
            country_code: str = row[country_code_col_name]
            year: int = row[year_col_name]
            democracy_index: float = row[democracy_index_col_name]
            
            # update only necessary values
            if country_code not in self.country_code_to_name:
                continue
            self._cursor.execute(
                f"""
                UPDATE metrics 
                SET {indicator_code} = ?
                WHERE countryCode = ? AND year = ?;
                """,
                (democracy_index, country_code, year))
                
        self._conn.commit()
        self._disconnect()
    
    
    def _create_countries_table(self) -> None:
        """Creates conversion table for countries"""
        self._connect()
        
        self._cursor.execute(f"DROP TABLE IF EXISTS {self.countries_table_name};")
        self._cursor.execute(
            f"""
            CREATE TABLE {self.countries_table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                countryCode TEXT,
                countryName TEXT
                );
            """)

        self._conn.commit()
        self._disconnect()
    
    
    def _create_indicators_table(self) -> None:
        """Creates conversion table for indicators"""
        self._connect()
        
        self._cursor.execute(f"DROP TABLE IF EXISTS {self.indicators_table_name};")
        self._cursor.execute(
            f"""
            CREATE TABLE {self.indicators_table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicatorCode TEXT,
                indicatorName TEXT,
                indicatorNameHuman TEXT
                );
            """)

        self._conn.commit()
        self._disconnect()
    
    
    def _create_metrics_table(self) -> None:
        """Creates table for data from all collected indicators"""
        self._connect()
        
        self._cursor.execute(f"DROP TABLE IF EXISTS {self.metrics_table_name};")
        self._cursor.execute(
            f"""
            CREATE TABLE {self.metrics_table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                countryCode TEXT,
                year INTEGER,
                {self.indicator_to_code["democracy-index-eiu"]} REAL,
                {self.indicator_to_code["education"]} REAL,
                {self.indicator_to_code["GDP"]} REAL,
                {self.indicator_to_code["gini-index"]} REAL,
                {self.indicator_to_code["life-expectancy"]} REAL,
                {self.indicator_to_code["military-expenditure"]} REAL,
                {self.indicator_to_code["research-and-development-expenditure"]} REAL
                );
            """)

        self._conn.commit()
        self._disconnect()
    
    
    def _fill_countries_table(self) -> None:
        """Fills the conversion table for countries"""
        self._connect()
  
        for code, name in self.country_code_to_name.items():
            self._cursor.execute(
                f"""
                INSERT INTO {self.countries_table_name} 
                    (countryCode, countryName) VALUES (?, ?);
                """,
                (code, name)
                )

        self._conn.commit()
        self._disconnect()
    
    
    def _fill_indicators_table(self) -> None:
        """Fills the conversion table for indicators"""
        self._connect()
        
        for indicator, code in self.indicator_to_code.items():
            indicator_human_form: str = indicator.replace("-", " ")
            indicator_human_form = indicator_human_form[0].upper() + indicator_human_form[1:]
            
            self._cursor.execute(
                f"""
                INSERT INTO {self.indicators_table_name} 
                    (indicatorName, indicatorNameHuman, indicatorCode) VALUES (?, ?, ?);
                """,
                (indicator, indicator_human_form, code)
                )
            
        self._conn.commit()
        self._disconnect()
    
    
    def _fill_metrics_table(self) -> None:
        """Fills the metrics table with country codes and years,
        data are added through methods `add_world_bank_dataset` 
        and `add_democracy_index_dataset` 
        """
        
        self._connect()
        
        studied_years: range = range(2010, 2024)
        for country_code in self.country_code_to_name:
            for year in studied_years:
                self._cursor.execute(
                    f"""
                    INSERT INTO {self.metrics_table_name} (countryCode, year) VALUES (?, ?);
                    """,
                    (country_code, year)
                    )
                
        self._conn.commit()
        self._disconnect()
    
    
    def _connect(self) -> None:
        """Connect to the database

        Raises:
            sqlite3.OperationalError: if the database file does not exist
        """
        # try to establish connection with provided database file
        # if the file doesn't exist (or there occurs another error), throw sqlite3.OperationalError
        # The following code block was copied (and slightly adapted) from Stack Overflow:
        # https://stackoverflow.com/a/12932782
        # Original author: Martijn Pieters
        # Retrieved on: 22.3.2024
        try:
            dburi = f'file:{pathname2url(self.path_to_db)}?mode=rw'
            self._conn = sqlite3.connect(dburi, uri=True)
            self._cursor = self._conn.cursor()
        except sqlite3.OperationalError as exc:
            raise sqlite3.OperationalError(
                f"Couldn't connect to database {self.path_to_db}"
                ) from exc
    
    
    def _disconnect(self) -> None:
        """Disconnect from the database"""
        if self._conn:
            self._conn.close()
        self._conn = None
        self._cursor = None
    

def main() -> None:
    """Creates the database"""
    dc: DatabaseCreator = DatabaseCreator("data/db.sqlite")
    dc.load_country_code_to_name_conversion("data/clean/education.csv")
    dc.create_tables()
    
    democracy_index_indicator_name: str = "democracy-index-eiu"
    dc.add_democracy_index_dataset(
        f"data/clean/{democracy_index_indicator_name}.csv", democracy_index_indicator_name
        )
    
    world_bank_indicators: list[str] = [
        "education", "GDP", "gini-index", "life-expectancy", 
        "military-expenditure", "research-and-development-expenditure"
        ]
            
    for indicator in world_bank_indicators:
        dc.add_world_bank_dataset(f"data/clean/{indicator}.csv", indicator)


if __name__ == "__main__":
    main()
