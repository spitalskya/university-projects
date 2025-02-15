from typing import Optional, Any
from flask import Flask, render_template, request
from plotly.graph_objects import Figure
from pandas import DataFrame
from data_handlers.database_handler import DatabaseHandler
from processing.indicator_processor import IndicatorProcessor 


app = Flask(__name__)

db_handler: DatabaseHandler = DatabaseHandler("data/db.sqlite")
ip: IndicatorProcessor = IndicatorProcessor()

year_for_pca: int = 2023


def get_countries_for_current_page(
    search_query: str, page: int, countries_per_page: int = 20
    ) -> tuple[list[str], int]:
    """Returns list of countries to be displayed on the current page

    Args:
        search_query (str): query to filter only countries that contains this string
        page (int): number of the current page
        countries_per_page (int, optional): how many countries to display
            Defaults to 20

    Returns:
        tuple[list[str], int]: pair of values
            list[str] : countries to be displayed
            int: total pages after search filter
    """    
    countries: list[str] = sorted(db_handler.get_all_countries())
    
    filtered_countries: list[str] = [country for country in countries if search_query.lower() in country.lower()]
    
    start_index: int = (page - 1) * countries_per_page
    end_index: int = min(start_index + countries_per_page, len(filtered_countries))

    current_countries_on_page: list[str] = filtered_countries[start_index:end_index]

    total_pages: int = len(filtered_countries) // countries_per_page + 1

    return (current_countries_on_page, total_pages)


def linear_regression_coeffs(drop_columns: list[str]=[]) -> dict[str, Any]:    
    """Returns dictionary with regression coefficients for both normalized
    and not normalized linear regression.

    Returns:
        dict[str, Any]: regression coefficients
            "indicators" (list[str]) : codes of indicators
            "values_orig" (list[float]) : coefficients for not normalized regression
            "values_norm" (list[float]) : coefficients for normalized regression
            "r2_orig" (float) : coefficient of determination for not normalized regression
            "r2_norm" (float) : coefficient of determination for normalized regression
    """
    data: DataFrame = db_handler.get_whole_metrics()
    data.drop(columns=["id", "year", "countryCode"], inplace=True)
    data.drop(columns=drop_columns, inplace=True)
    
    democracy_index_col_name: str = db_handler.get_indicator_code_from_name(
        "democracy-index-eiu"
    )
    
    result: dict[str, list[str] | list[float]] = {}
    
    lin_reg: dict[str, Any] = ip.linear_regression(data, democracy_index_col_name)
    coeffs = lin_reg["coeffs"]
    result["indicators"] = [pair[0] for pair in coeffs]
    result["values_orig"] = [float(f"{pair[1]:.3e}") for pair in coeffs]
    result["r2_orig"] = float(f"{lin_reg["r_squared"]:.3e}")
    
    lin_reg_norm: dict[str, Any] = ip.normalized_linear_regression(data, democracy_index_col_name)
    coeffs_norm = lin_reg_norm["coeffs"]
    result["values_norm"] = [float(f"{pair[1]:.3e}") for pair in coeffs_norm]
    result["r2_norm"] = float(f"{lin_reg_norm["r_squared"]:.3e}")
    
    return result


def pca_html(year: int, columns: Optional[list[str]] = None) -> str:
    """Creates a PCA html text to be displayed

    Args:
        year (int): year for the PCA
        columns (Optional[list[str]], optional): columns to use in PCA
            Defaults to None -> all columns

    Returns:
        str: PCA html
    """    
    data: DataFrame = db_handler.get_whole_metrics()
    
    # create column with names
    data["countryName"] = data["countryCode"].apply(
        lambda code: db_handler.get_country_name_from_code(code)
        )
    
    # drop irrelevant columns
    data = data[data["year"] == year].drop(
        columns=["id", "year", "countryCode"]
        ).reset_index(drop=True)
    
    # leave only desired columns
    if columns:
        data = data.loc[:, columns + ["DCI", "countryName"]]
    
    # compute PCA
    return ip.pca(
        data, year=year, indicator_color_col="DCI", point_naming_col="countryName"
        ).to_html(full_html=False)
        

def globe_html(year: int, color_col: str) -> str:
    """Generate choropleth with countries colored by their democracy index
    in `year`

    Args:
        year (int): year for the democracy index data
        color_col (str): indicator to color the countries by

    Returns:
        str: html of the choropleth
    """
    data: DataFrame = db_handler.get_whole_metrics()
        
    # filter years
    data = data[data["year"] == year]
    
    # keep only column relevant for coloring
    filtered_data = data.loc[:, [color_col]]
    
    # add column with country names
    # Turkey has different names in World Bank data and in plotly
    filtered_data["countryName"] = data["countryCode"].apply(
        lambda code: db_handler.get_country_name_from_code(code) if code != "TUR" else "Turkey"
        )
    filtered_data.reset_index(inplace=True, drop=True)
    
    return ip.globe_plot(
        filtered_data, year, color_col
        ).update_layout(
            width=800, height=600
        ).to_html(full_html=False)


def get_indicator_legend() -> list[dict[str, str]]:
    """Returns indicator code to name conversion table

    Returns:
        list[dict[str, str]]: conversion table
    """    
    return db_handler.get_indicator_legend()


def get_correlation_matrix() -> str:
    corr: DataFrame = ip.correlation_matrix(db_handler.get_whole_metrics(), 
                          ["EDU", "GDP", "GNI", "LEX", "MIE", "RDE"])
    return corr.to_html()


@app.before_request
def before_request():
    db_handler.open_connection()


@app.teardown_request
def teardown_request(exception):
    db_handler.close_connection()


@app.route('/', methods=['GET', 'POST'])
def home():  
    global year_for_pca
    
    # get values from forms
    year_for_globe_plot: int = 2023
    indicator_globe: str = "DCI"
    if request.method == "POST":
        if "year_globe" in request.form:
            year_for_globe_plot = int(request.form["year_globe"]) 
        if "indicator_globe" in request.form:
            indicator_globe = request.form["indicator_globe"]
        if "year_pca" in request.form:
            year_for_pca = int(request.form["year_pca"]) 

    # get values from search query and pagination
    search_query = request.args.get("q", "")
    page = request.args.get("page", default=1, type=int)
    countries, total_pages = get_countries_for_current_page(search_query, page)

    corr_drop_columns: list[str] = ["GDP", "LEX"]
    
    return render_template('index.html', 
                           countries=countries,
                           indicator_legend=get_indicator_legend(),
                           studied_years=range(2010, 2024),
                           coeffs_lin_reg=linear_regression_coeffs(),
                           corr_drop=corr_drop_columns,
                           coeffs_lin_reg_corr=linear_regression_coeffs(corr_drop_columns),
                           globe=globe_html(year_for_globe_plot, indicator_globe),
                           indicator_codes=db_handler.get_all_indicator_codes(),
                           pca=pca_html(year_for_pca),
                           corr=get_correlation_matrix(),
                           selected_year_pca=year_for_pca,
                           search_query=search_query,
                           current_page=page,
                           total_pages=total_pages)


@app.route('/country/<country_name>/')
def country(country_name):
    
    indicator_codes = db_handler.get_all_indicator_codes()
    
    # create plot for every indicator for `country_name`
    plots: list[dict[str, str | Figure]] = []
    for code in indicator_codes:
        data: DataFrame = db_handler.get_indicator_of_country(country_name, code)
        plots.append({
            "name": db_handler.get_indicator_name_human_from_code(code),
            "fig": ip.indicator_line_plot(data, "Year", code).to_html(full_html=False)
        })
    
     
    return render_template('country.html',
                           country_name=country_name,
                           plots=plots
                           )


@app.route('/pca_interactive/', methods=['GET', 'POST'])
def pca_interactive():
    indicator_legend: list[dict[str, str]] = get_indicator_legend()
    
    # democratic index should not be used to compute PCA
    indicator_legend.remove({"code": "DCI", "name": "Democracy index eiu"})
    
    # extract year and columns to use in PCA, default 2023 and all columns
    year: int = 2023
    columns: list[str] = [indicator["code"] for indicator in indicator_legend]
    if request.method == "POST":
        year = int(request.form["year"]) 
        tmp: list[str] = request.form.getlist("indicator_select")
        if len(tmp) >= 2:
            columns = tmp
        
    pca: str = pca_html(year, columns)
    
    return render_template('pca_interactive.html',
                           studied_years=range(2010, 2024),
                           indicators=indicator_legend,
                           selected_year=year,
                           pca=pca
                           )
