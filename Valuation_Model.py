import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Load the data from csv file
data = pd.read_csv('sp500_snapshot.csv')

# Make a new EV/EBITDA column
data['ev_ebitda'] = data['enterprise_value'] / data['ebitda']
data = data[(data['ebitda'] > 0) & (data['ev_ebitda'].between(2, 60))].copy()

# Make the dependent vairable log(EV/EBITDA)
data['y'] = np.log(data['ev_ebitda'])

# Select the variables to be used
data['size'] = np.log(data['revenue']) # Take log(Revenue) to make different sized companies more comparebale
data['capex_revenue'] = data['capex'] / data['revenue']
data['net_debt_assets'] = (data['total_debt'] - data['cash']) / data['total_assets']
numeric_features = ['size', 'revenue_growth', 'ebitda_margin', 'operating_margin', 'return_on_assets', 'capex_revenue', 'net_debt_assets']

# Clean data
data = data.dropna(subset=numeric_features + ['y']).reset_index(drop=True)
data = data.drop_duplicates(subset=['revenue', 'ebitda']).reset_index(drop=True)

# Make a new column for each sector and assign dummy variables
sector_columns = pd.get_dummies(data['sector'], dtype=float)
X = pd.concat([data[numeric_features], sector_columns], axis=1)
y = data['y']

# Make blank array for each method
pred_rf_model = np.zeros(len(data))
pred_ridge_model = np.zeros(len(data))
pred_median = np.zeros(len(data))
pred_sector = np.zeros(len(data))

# Set up k fold
folds = KFold(n_splits=5, shuffle=True, random_state=0)

# Set up random forest model (found the optimal parameters seperately)
def make_rf_model():
    return RandomForestRegressor(n_estimators=500, min_samples_leaf=1, random_state=1)

# Set up ridge model (found optimal alpha value seperately)
def make_ridge_model():
    return make_pipeline(StandardScaler(), Ridge(alpha=2000)) 

# Select the training and test samples
for training_sample, testing_sample in folds.split(data):
    train = data.iloc[training_sample]
    test = data.iloc[testing_sample]

    # Random forest model
    model = make_rf_model()
    model.fit(X.iloc[training_sample], y.iloc[training_sample])
    pred_rf_model[testing_sample] = model.predict(X.iloc[testing_sample])

    # Ridge model
    model = make_ridge_model()
    model.fit(X.iloc[training_sample], y.iloc[training_sample])
    pred_ridge_model[testing_sample] = model.predict(X.iloc[testing_sample])

    # Median value
    pred_median[testing_sample] = train['y'].median()

    # Median sector value
    sector_median = train.groupby('sector')['y'].median()
    pred_sector[testing_sample] = test['sector'].map(sector_median).fillna(train['y'].median())

# Comapre results between methods and print
def compare(method, pred):
    prediction_error = np.abs(np.exp(pred) - data['ev_ebitda']) / data['ev_ebitda']
    print(f'{method:<36} Median Prediction Error Percentage: {round((prediction_error.median()*100),2)}%    R2: {round((r2_score(y, pred)),2)}')

print('Results from running on test sample:')
compare('Median for each company', pred_median)
compare('Sector median for each company', pred_sector)
compare('Random forest model', pred_rf_model)
compare('Ridge model', pred_ridge_model)

# Print graph for the random forest model
print ('')
plt.scatter(y, pred_rf_model, s=10)
lims = [y.min(), y.max()]
plt.plot(lims, lims, color='black')
plt.xlabel('Actual log(EV/EBITDA)')
plt.ylabel('Predicted log(EV/EBITDA)')
plt.title('Predicted vs Actual (Random Forest)')
plt.show()

#  Seeing the biggest factors the random forest model takes into consideration
temp_model = make_rf_model().fit(X, y)
if hasattr(temp_model, 'feature_importances_'):
    importance = pd.Series(temp_model.feature_importances_, index=X.columns)
    print('\nMost important factors in model: ')
    print(importance.sort_values(ascending=False).head(10).round(3).to_string())

# Comparing model prediction to actual EV/EBITDA
data['pred_ev_ebitda'] = np.exp(pred_rf_model)
data['log_gap'] = pred_rf_model - data['y']

show = ['ticker', 'sector', 'ev_ebitda', 'pred_ev_ebitda', 'log_gap']

print('\nMost undervalued vs model:')
print(data.sort_values('log_gap', ascending=False)[show].head(15).round(2).to_string(index=False))
print('\nMost expensive vs model:')
print(data.sort_values('log_gap')[show].head(5).round(2).to_string(index=False))
