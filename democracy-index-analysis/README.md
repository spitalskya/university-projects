# Analysis of the Democracy Index

This project focuses on analyzing the *Democracy Index* (DCI) from *The Economist Intelligence Unit*. It investigates the correlation between the DCI and various statistics from countries between 2010 and 2023.

## Key Components

1. **Data**: The project correlates the DCI with six indicators from the World Bank:
   - EDU: Percentage of students continuing to secondary education
   - GDP: GDP per capita in USD
   - GNI: Gini index (income inequality)
   - LEX: Life expectancy at birth
   - MIE: Military expenditure as a percentage of GDP
   - RDE: Research and development expenditure as a percentage of GDP
2. **Data Cleaning**: Missing values are filled using a strategy based on proximity and average values for each year.
3. **Analysis**:
   - **Linear Regression**: Analyzes how DCI can be approximated as a linear combination of the indicators.
   - **Geographical Analysis**: Maps the DCI across different countries for 2010 and 2023.
4. **Flask Application**: A web app to visualize data, explore trends interactively, and perform PCA visualizations.
   - can be run by `make app`

## Conclusion

This project provides a comprehensive analysis of how various factors influence democracy rankings and presents the findings in an accessible web application. The Flask app allows interactive exploration of data trends and PCA visualizations.

A more detailed description is available in the [report](report/report.pdf).  
