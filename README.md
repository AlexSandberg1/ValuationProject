# S&P Valuation Project

**Overview**
- This is a machine learning model that was built in Python which aims to estimate the value of S&P 500 companies.
- The main method is a Random Forest model which estimates a EV/EBITDA value for each company.
- To run the code you first need to run the 'Download_Data' file which generates the csv file from Yahoo Finance data.

**Results**
- Four different methods were used to create estimates: simply using the median value, using the sector median value, using a Ridge model, and using the Random Forest model. The results from each are shown below:

| Method | Median prediction error | R² |
|---|---|---|
| Same multiple for every company | 26.2% | 0.00 |
| Sector median multiple | 28.6% | 0.09 |
| Ridge regression | 25.2% | 0.05 |
| **Random forest** | **21.3%** | **0.33** |

- For the Random Forest model, this is an additional graph showing the predictions agaisnt the actual values

 ![Predicted vs Actual EV/EBITDA](images/Random_Forest_Graph.png)

 - According to the model, these where the companies which are most undervalued:

| Ticker | Sector | Actual EV/EBITDA | Predicted EV/EBITDA | Log gap |
|---|---|---|---|---|
| EXE | Energy | 3.81 | 11.57 | 1.11 |
| APA | Energy | 4.00 | 11.04 | 1.02 |
| CF | Materials | 5.93 | 16.34 | 1.01 |
| FOXA | Communication Services | 7.75 | 21.19 | 1.01 |
| MOS | Materials | 6.87 | 18.17 | 0.97 |
| APTV | Consumer Discretionary | 4.34 | 10.69 | 0.90 |
| NEM | Materials | 6.12 | 14.55 | 0.87 |
| CNC | Health Care | 5.53 | 12.71 | 0.83 |
| HPQ | Information Technology | 6.93 | 15.78 | 0.82 |
| SNDK | Information Technology | 7.48 | 16.99 | 0.82 |
| INCY | Health Care | 10.18 | 21.41 | 0.74 |
| LULU | Consumer Discretionary | 5.30 | 11.13 | 0.74 |
| OMC | Communication Services | 7.30 | 15.13 | 0.73 |
| MU | Information Technology | 8.85 | 18.06 | 0.71 |
| BMY | Health Care | 8.77 | 17.48 | 0.69 |

**Data**
