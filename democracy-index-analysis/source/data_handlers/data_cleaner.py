from typing import Any, Optional
import os
import json
import pandas as pd


class WorldBankDataCleaner:
    """Class responsible for cleaning the datasets sourced from World Bank"""
        
    data: pd.DataFrame
    
    # json file that contains necessary information about cleaning process
    clean_config: dict[str, Any]
    
    # codes of countries in democracy index dataset - will keep only those
    democracy_index_country_codes: set[str]     

    # names of non-numeric columns to keep
    columns_to_keep: list[str] = ["Country Name", "Country Code", "Indicator Name"]
    
    
    def __init__(self, directory_path: str, country_codes: set[str]) -> None:
        """Load the raw World bank dataset and the codes of countries that we want to keep 

        Args:
            directory_path (str): path to the directory with raw dataset
            country_codes (set[str]): codes of relevant countries for democratic index
        """
        
        self.democracy_index_country_codes = country_codes
        
        with open(f"{directory_path}/clean_config.json", "r") as config_file:
            self.clean_config = json.load(config_file)
        
        self.data = pd.read_csv(
            f"{directory_path}/{self.clean_config["file"]}",
            skiprows=self.clean_config["skip_top"])
             
    
    def clean(self) -> None:
        """Calls the individual steps of the data cleaning process"""
        self._filter_indicator()
        self._filter_democracy_index_countries()
        self._filter_columns()
        self._filter_years()
        self._fill_missing()
        
        self.data.reset_index(drop=True, inplace=True)

    
    def _filter_columns(self) -> None:
        """Keeps only relevant columns in the dataset:
        either those in `self.data.columns` or columns corresponding to years
        """
        self.data = self.data[
            [col for col in self.data.columns if col in self.columns_to_keep or col.isdigit()]
            ]

    
    def _filter_years(self) -> None:
        """Drops the columns corresponding to years in the dataset 
        that are before the set value in the config file
        """
        self.data = self.data[
            [col for col in self.data.columns 
                if not(col.isdigit() and int(col) < self.clean_config["from_year"])]
            ]
    
    
    def _filter_indicator(self) -> None:
        """If the dataset contained more than one indicator, 
        leave only the one set in the config file
        """
        self.data = self.data[self.data["Indicator Code"] == self.clean_config["indicator"]]
    
    
    def _filter_democracy_index_countries(self) -> None:
        """Drop all rows corresponding to countries or regions 
        not relevant for the democratic index
        """
        self.data = self.data[self.data["Country Code"].isin(self.democracy_index_country_codes)]
        
    
    def _fill_missing(self) -> None:
        """Fill missing values in the dataset:
        if the row contains not NaN values, fill with year-wise closest value
        else fill with defined statistic of the column (min/max/avg)
        """
        def fill_with_closest_not_nan_values(row: pd.Series) -> pd.Series:
            """If NaN entry is found in columns corresponding to years,
            fill it with closest (year-wise) value.
            Not NaN values and values from other columns are not changed
            
            Args:
                row (pd.Series): row od DataFrame where the NaNs should be filled

            Returns:
                pd.Series: row with filled NaN values
            """
            
            filled_values: list[int] = []       # replacement for the row
            
            for i, value in enumerate(row):
                # if value is not NaN or the column is not corresponding to year data, continue 
                if not pd.isna(value) or not row.index[i].isdigit():
                    filled_values.append(value)
                    continue
                
                fill: Optional[float] = None            # fill for the NaN
                fill_distance: float = float("inf")     # year difference of the NaN and fill entry
                
                # iterate through current row
                for j, fill_adept in enumerate(row):
                    if (row.index[j].isdigit()            # column needs to correspond to a year
                        and abs(i - j) < fill_distance    # difference of years needs to be smaller
                        and not pd.isna(fill_adept)):     # don't fill with NaNs
                        # change the values
                        fill_distance = abs(i - j)
                        fill = fill_adept
                        
                if fill:        # found a valid fill value
                    filled_values.append(fill)
                else:           # leave NaN (whole row is NaNs)
                    filled_values.append(value)

            return pd.Series(filled_values, index=row.index)
        
        
        # replace NaNs with closest viable value to them
        for index, row in self.data.iterrows():        
            if any(row.isna()):
                self.data.loc[index] = fill_with_closest_not_nan_values(row)
        
        # if whole row was NaNs, replace with no_data_fill value from column
        for col in self.data.columns:
            if not col.isdigit():   # ignore not year columns
                continue
            
            fill_value: float = 0
            if self.clean_config["no_data_fill"] == "min":
                fill_value = self.data[col].min()
            elif self.clean_config["no_data_fill"] == "max":
                fill_value = self.data[col].max()
            elif self.clean_config["no_data_fill"] == "avg":
                fill_value = self.data[col].mean()
            
            self.data[col] = self.data[col].fillna(fill_value)
    
    
    def write(self, clean_data_dir: str) -> None:
        """Write the clean dataset to a csv

        Args:
            clean_data_dir (str): directory where to write the dataset
        """
        self.data.to_csv(
            f"{clean_data_dir}/{self.clean_config["name"]}.csv",
            index=False
            )


def get_all_raw_data_directories(raw_data_parent_dir: str) -> list[str]:
    """Get all directories where raw World bank datasets are stored

    Args:
        raw_data_parent_dir (str): directory with directories for world bank datasets

    Returns:
        list[str]: list of directories where raw World bank datasets are stored
    """
    return [f"{raw_data_parent_dir}/{dir}" for dir in os.listdir(raw_data_parent_dir) 
            if os.path.isdir(os.path.join(raw_data_parent_dir, dir))]


def democracy_index_fill_nans(democracy_index_df: pd.DataFrame, write_path: str) -> None:
    """Function to fill NaNs in democracy index dataset.
    Also, if country does not have entry for one of the years between 2010-2023, create one.

    Args:
        democracy_index_df (pd.DataFrame): dataframe with democracy index data
        write_path (str): path to the csv where to store the filled dataset
    """
    
    def get_closest_valid_democracy_index(country_code: str, year: int) -> float:
        """Returns the closest (year-wise) democracy index entry for the provided country and year.

        Args:
            country_code (str): code of the country to filter
            year (int): year to find entries close to

        Returns:
            float: closest democracy index
        """
        closest_democracy_index: Optional[float] = None     # value to return
        year_difference: float = float("inf")   # year difference of `year` and year of value above
        
        for _, row in data.iterrows():
            if (row[country_code_col_name] == country_code          # same country
                and abs(year - row[year_col_name]) < year_difference    # closer to the provided year
                and not pd.isna(row[democracy_index_col_name])          # is not NaN
                ):
                # replace the return value
                year_difference = abs(year - row[year_col_name])
                closest_democracy_index = row[democracy_index_col_name]
                
        if closest_democracy_index:
            return closest_democracy_index
        return 0        # if all values for country were NaN, return 0
        
        
    data: pd.DataFrame = democracy_index_df.copy()
    
    # store which years are in the raw dataset for every country
    # the key is country name and country code
    found_entries: dict[tuple[str, str], set[int]] = {}
    
    # names of the columns
    country_name_col_name: str = "Entity"
    country_code_col_name: str = "Code"
    year_col_name: str = "Year"
    democracy_index_col_name: str = "Democracy score"
    
    fill: float
    for index, row in data.iterrows():
        country_name: str = row[country_name_col_name]
        country_code: str = row[country_code_col_name]
        year: int = row[year_col_name]
        
        # add value to the found entries
        if (country_name, country_code) not in found_entries:
            found_entries[(country_name, country_code)] = set()
        found_entries[(country_name, country_code)].add(year)
        
        # if the democracy index is not NaN, continue
        if not pd.isna(row[democracy_index_col_name]):
            continue
        
        # else, replace it with the closest year-wise democracy index for the country
        fill = get_closest_valid_democracy_index(
            country_code, year
            )
        data.loc[index, democracy_index_col_name] = fill
    
    # if country does not have an entry for all of the years from 2010 to 2023, add them
    studied_years: set[int] = set(range(2010, 2024))
    for country_name, country_code in found_entries:
        missing_years: set[int] = studied_years - found_entries[(country_name, country_code)]
        
        for missing_year in missing_years:
            fill = get_closest_valid_democracy_index(country_code, missing_year)
            
            # construct the missing row
            missing_row: pd.DataFrame = pd.DataFrame({
                country_name_col_name: country_name,
                country_code_col_name: country_code,
                year_col_name: missing_year,
                democracy_index_col_name: fill    
            }, index=[len(data)])
            
            # add it to the dataset
            data = pd.concat([data, missing_row], ignore_index=True)
    
    # write the cleaned dataset
    data.to_csv(write_path, index=False)
    

def main() -> None:
    democracy_index_df: pd.DataFrame = pd.read_csv("data/raw/democracy-index-eiu.csv")
    democracy_index_countries: set[str] = set(democracy_index_df["Code"])

    # directory for the cleaned data
    clean_data_dir: str = "data/clean"
    
    # clean the democracy index dataset
    democracy_index_indicator_name: str = "democracy-index-eiu"
    democracy_index_fill_nans(
        democracy_index_df, 
        f"{clean_data_dir}/{democracy_index_indicator_name}.csv")
    
    # clean the world bank dataset
    world_bank_data_dirs: list[str] = get_all_raw_data_directories("data/raw")
    for data_dir in world_bank_data_dirs:
        w: WorldBankDataCleaner = WorldBankDataCleaner(data_dir, democracy_index_countries)
        w.clean()
        w.write(clean_data_dir)


if __name__ == "__main__":
    main()
