# Solvency prediction with Quasi-Newton logistic regression

A more detailed description is available in the [report](report.pdf).  

## Project Overview

This project focuses on binary classification using logistic regression optimized via quasi-Newton and gradient-based methods. The goal is to predict client solvency based on three financial indicators.

Team members: Tomáš Antal, Erik Božík, Róbert Kendereš Teo Pazera, Andrej Špitalský

## Problem Statement

We aim to minimize a specific objective function using optimization techniques, applying the resulting model to predict client solvency. The dataset consists of 699 clients, each described by:

- Months since account opening
- Savings-to-investment ratio
- Years in current job
- Binary solvency label (1 = solvent, 0 = not solvent)

## Optimization Methods Implemented

1. **Quasi-Newton Methods**:

   - **BFGS** (Broyden-Fletcher-Goldfarb-Shanno)
   - **DFP** (Davidon-Fletcher-Powell)
   - Both with optimal and backtracking step size selection.

2. **Gradient Methods**:

   - With **optimal step size** (found via bisection)
   - With **constant step size**

## Results

- The most significant predictors of solvency were **savings-to-investment ratio** and **years in current job**.
- The **months since account opening** had a negative correlation with solvency.
- The convergence of different methods was visualized to compare performance and efficiency.
- A flexible logistic regression model was developed to allow optimization via either quasi-Newton or gradient methods.

## Performance Comparison

| Method                   | Step Size | Iterations | Time (s) |
| ------------------------ | --------- | ---------- | -------- |
| BFGS      | Backtracking  | ~10        | 0.0067   |
| BFGS        | Bisection   | ~10         | 0.0074   |
| DFP       | Backtracking  | ~10         | 0.0031   |
| DFP       | Bisection   | ~10      | 0.0069   |
| Gradient descent  | Bisection | \~5000     | 6.1772   |
| Gradient descent  | Constant     | >10,000    | 0.8142   |
