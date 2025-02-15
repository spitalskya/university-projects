import pandas as pd
import plotly.express as px
from data_handlers.database_handler import DatabaseHandler
from processing.indicator_processor import IndicatorProcessor

db: DatabaseHandler = DatabaseHandler("data/db.sqlite")
ip: IndicatorProcessor = IndicatorProcessor()


def globe_plot(year: int, color_col: str="DCI") -> None:
    data: pd.DataFrame = db.get_whole_metrics()
        
    data = data[data["year"] == year]
    democracy_index_data = data.loc[:, [color_col]]
    democracy_index_data["countryName"] = data["countryCode"].apply(
        lambda code: db.get_country_name_from_code(code) if code != "TUR" else "Turkey"
        )
    democracy_index_data.reset_index(inplace=True)
    
    ip.globe_plot(
        democracy_index_data, year, color_col
        ).show()


def multiple_line_plot(data: pd.DataFrame, y_col: str) -> None:
    px.line(data, 
            x="year", y=y_col, color="countryCode").show()


def main() -> None:
    db.open_connection()
    
    
    data: pd.DataFrame = db.get_whole_metrics()

    print(data.describe())
    
    globe_plot(2010)
    globe_plot(2023)

    globe_plot(2010, "GNI")
    globe_plot(2021, "GNI")
    
    data_filtered = data[data["countryCode"].isin(["FRA", "SVK"])]
    multiple_line_plot(data_filtered, "MIE")

    db.close_connection()

if __name__ == "__main__":
    main()
    