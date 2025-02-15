from typing import Any
import plotly.express as px
from plotly.graph_objects import Figure
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from data_handlers.database_handler import DatabaseHandler


class IndicatorProcessor:
    """Class responsible for processing the indicator data,
    either displaying it or computing something from it
    """
    
    def __init__(self) -> None:
        pass
    
    
    def indicator_line_plot(self, indicator_data: pd.DataFrame, 
                            year_col_name: str, indicator_col_name: str) -> Figure:
        """Creates a line plot for one indicator and one country

        Args:
            indicator_data (pd.DataFrame): indicator data for one country and one indicator
            year_col_name (str): name of the column where years of the entries are stored
            indicator_col_name (str): name of the column where indicator entries are stored

        Returns:
            Figure: line plot
        """
        if set(indicator_data.columns) != {year_col_name, indicator_col_name}:
            return Figure()
        
        return px.line(indicator_data, x=year_col_name, y=indicator_col_name)

    
    def linear_regression(self, data: pd.DataFrame, 
                          dependent_col_name: str) -> dict[str, Any]:
        """Computes linear regression with metrics table.
        Used for finding out how democracy index depends on individual indicators

        Args:
            data (pd.DataFrame): data with indicators and democracy index
            dependent_col_name (str): which column should be taken in linear regression 
                as the dependent one

        Returns:
            dict[str, Any]: dictionary of results:
                r_squared: float -> R^2 coefficient of the prediction
                coeffs: dict[str, float] -> regression coefficients for indicators
        """
        # https://realpython.com/linear-regression-in-python/
        x: np.ndarray = data.drop(columns=[dependent_col_name]).to_numpy()
        y: np.ndarray = data[dependent_col_name].to_numpy()
        
        model: LinearRegression = LinearRegression().fit(x, y)
        r_squared: float = model.score(x, y)
        coeffs: dict[str, float] = list(zip(
            data.drop(columns=[dependent_col_name]).columns,
            model.coef_
            ))

        return  {
            "r_squared" : r_squared,
            "coeffs" : coeffs
        }
        

    def normalized_linear_regression(
        self, data: pd.DataFrame, dependent_col_name: str
        ) -> dict[str, Any]:
        """Computes linear regression with normalized metrics table.
        Normalization is done by subtracting column mean and dividing by standard deviation.
        Used for finding out how democracy index depends on individual indicators

        Args:
            data (pd.DataFrame): data with indicators and democracy index
            dependent_col_name (str): which column should be taken in linear regression 
                as the dependent one

        Returns:
            dict[str, Any]: dictionary of results:
                r_squared: float -> R^2 coefficient of the prediction
                coeffs: dict[str, float] -> regression coefficients for indicators
        """
        return self.linear_regression(
            (data - data.mean())/data.std(),
            dependent_col_name 
        )
    
    
    def pca(self, data: pd.DataFrame, year: int,
            indicator_color_col: str, point_naming_col: str) -> Figure:
        """Displays PCA of data as a scatter plot, colors of the dots 
        are computed from `indicator_color_col`.

        Args:
            data (pd.DataFrame): data with indicators and democracy index
            year (int): from which year to take the values
            indicator_color_col (str): points will be colored based on this column
            point_naming_col (str): points will have names based on this column

        Returns:
            Figure: PCA scatter plot
        """
        x: pd.DataFrame = data.drop(columns=[indicator_color_col, point_naming_col])  
        y: pd.Series = data[indicator_color_col]  
        countries = data[point_naming_col]

        # https://builtin.com/machine-learning/pca-in-python
        x_scaled: np.ndarray = StandardScaler().fit_transform(x)

        pca: PCA = PCA(n_components=2)
        principal_components: np.ndarray = pca.fit_transform(x_scaled)

        pca_df: pd.DataFrame = pd.DataFrame(data=principal_components, columns=["PC1", "PC2"])

        pca_df = pd.concat([pca_df, y, x, countries], axis=1)

        return px.scatter(
            pca_df, x="PC1", y="PC2", 
            color=indicator_color_col, 
            hover_name=point_naming_col,
            hover_data={
                indicator: True if indicator not in {"PC1", "PC2", point_naming_col}
                    else False for indicator in pca_df.columns
                },
            title=f"PCA of World Bank indicators for year {year}\ncolored by indicator {indicator_color_col}")
        
    
    def globe_plot(self, data: pd.DataFrame, year: int,
                              color_col: str="DCI") -> Figure:
        """Choropleth of `color_col` of countries

        Args:
            data (pd.DataFrame): dataframe with democracy index for each country
            year (int): year to take democracy index from
            color_col (str, optional): column to determine colors of the countries
                Defaults to "DCI"

        Returns:
            Figure: choropleth
        """
        return px.choropleth(data,
                             locations="countryName",
                             locationmode="country names",
                             color=color_col,
                             hover_name="countryName",
                             hover_data={"countryName": False, color_col: True},
                             title=f"{color_col} of countries in {year}")
    

    def correlation_matrix(self, data: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        data = data.loc[:, data.columns.isin(cols)]
        return data.corr()
    

def exam() -> None:
    db: DatabaseHandler = DatabaseHandler("data/db.sqlite")
    ip: IndicatorProcessor = IndicatorProcessor()
    
    db.open_connection()
    data: pd.DataFrame = db.get_whole_metrics()
    relevant_cols_for_corr: list[str] = ["EDU", "GNI", "MIE", "RDE"]
    ip.correlation_matrix(data, relevant_cols_for_corr)
    
    db.close_connection()


def main() -> None:
    """Only for testing purposes"""
    db: DatabaseHandler = DatabaseHandler("data/db.sqlite")
    ip: IndicatorProcessor = IndicatorProcessor()
    
    db.open_connection()
        
    metrics: pd.DataFrame = db.get_whole_metrics()
    
    metrics = metrics[metrics["year"] == 2023]
    data = metrics.loc[:, ["DCI"]]
    data["countryName"] = metrics["countryName"].apply(
        lambda x: db.get_country_name_from_code(x) if x != "TUR" else "Turkey"
        )
    print(list(data["countryName"]))
    data.reset_index(inplace=True)
    ip.globe_plot(data)
    
    """metrics.drop(
        columns=["id", "countryCode", "year"],
        inplace=True
    )
    
    ip.normalized_linear_regression(
        metrics, "DCI"
    )"""
    
    """metrics = metrics[metrics["year"] == 2023]
    metrics.drop(
        columns=["id", "year"],
        inplace=True
    )
    metrics.reset_index(inplace=True)
    
    ip.pca(metrics, "DCI", "countryCode")"""
    
    db.close_connection()


if __name__ == "__main__":
    exam()
    # main()
