# Slovak election prediction

*contributors: Tomáš Antal, Erik Božík, Teo Pazera, Andrej Špitalský, Tomáš Varga*

Report of our work can be found in the [report](tex/report.pdf).

## Introduction

This project aims to predict Slovak election results based on polling data, party dynamics, and socio-economic indicators in Slovakia. We use historical polling data, socio-economic indicators, and political alignments to create a predictive model.

## Data

1. **Polling Data**: We gathered historical polling data from 2010 to 2024, primarily from the FOCUS agency, and supplemented with data from other agencies where necessary. Data extraction was automated using Python tools like Selenium and Docling.
2. **Election Results**: Results from previous Slovak elections (2012, 2016, 2020, 2023) were obtained from the Slovak Statistical Office.
3. **Socio-economic Indicators**: Data on unemployment, GDP, poverty risk, and other factors were sourced from the DATAcube portal.
4. **Political Compass**: We obtained data on party positions (e.g., liberalism-conservatism, left-right) from the 2023 Election Compass.

## Data Preprocessing

- Data is cleaned and preprocessed, with missing or inconsistent values handled using interpolation and manual correction.
- The training set is filtered to include parties with significant polling results (once at least 1.5%).

## Model Implementation

- We implemented several algorithms for classifying predicting election outcomes:
  - **Logistic Regression**
  - **Ensemble Learning** for combining classifiers
  - **Time-series Prediction** with ARIMA and exponential smoothing
  - **(Regularized) linear regression**
- Hyperparameters like choice of model and its weights and thresholds are fine-tuned through cross-validation.

## Results

- The trained model provides predictions for future elections based on historical polling data and socio-economic factors.
