import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
import sqlite3
import csv
from pandas import read_csv
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import Lasso
from numpy import mean
from numpy import std
from numpy import absolute
from numpy import arange
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LassoCV

conn = sqlite3.connect('COVID.db')  # You can create a new database by changing the name within the quotes
c = conn.cursor() # The database will be saved in the location where your 'py' file is saved

 # Predicting values:
# Function for predicting future values :
def get_regression_predictions(input_features,intercept,slope):
    predicted_values = input_features*slope + intercept
    return predicted_values

def PredictDeaths(predictedCases):
    data = pd.read_csv('COVID.csv')
    data.head()
    # Let’s select some features to explore more :
    data = data[['NEWCASES','NEWDEATHS']]
    
    # Cases vs Deaths:
    plt.scatter(data['NEWCASES'] , data['NEWDEATHS'] , color='blue')
    plt.xlabel('NEWCASES')
    plt.ylabel('NEWDEATHS')
    # plt.show() 
    
    # Generating training and testing data from our data:
    # We are using 80% data for training.
    train = data[:(int((len(data)*0.7)))]
    test = data[(int((len(data)*0.7))):]
    
    # Modeling:
    # Using sklearn package to model data :
    regr = linear_model.LinearRegression()
    train_x = np.array(train[['NEWCASES']])
    train_y = np.array(train[['NEWDEATHS']])
    regr.fit(train_x,train_y)
    # The coefficients:
    print ('coefficients : ',regr.coef_) #Slope
    print ('Intercept : ',regr.intercept_) #Intercept
    # Plotting the regression line:
    plt.scatter(train['NEWCASES'], train['NEWDEATHS'], color='blue')
    plt.plot(train_x, regr.coef_*train_x + regr.intercept_, '-r')
    plt.xlabel('New Cases')
    plt.ylabel('Deaths')
    #plt.show()
    
    # Predicting emission for future car:
    newCases = predictedCases
    estimated_deaths = get_regression_predictions(newCases,regr.intercept_[0],regr.coef_[0][0])
    print ('Estimated Deaths :',estimated_deaths)
    
    # Checking various accuracy:
    from sklearn.metrics import r2_score
    test_x = np.array(test[['NEWCASES']])
    test_y = np.array(test[['NEWDEATHS']])
    test_y_ = regr.predict(test_x)
    print('Mean absolute error: %.2f' % np.mean(np.absolute(test_y_ - test_y)))
    print('Mean sum of squares (MSE): %.2f' % np.mean((test_y_ - test_y) ** 2))
    print('R2-score: %.2f' % r2_score(test_y_ , test_y) )
    return estimated_deaths
 

def PredictCases(dateToPredict):
    data = pd.read_csv('COVID.csv')
    data.head()
    # Let’s select some features to explore more :
    data = data[['DATE','NEWCASES']]
    
    # Cases vs Deaths:
    plt.scatter(data['DATE'] , data['NEWCASES'] , color='blue')
    plt.xlabel('DATE')
    plt.ylabel('NEWCASES')
    #plt.show() 
    
    # Generating training and testing data from our data:
    # We are using 80% data for training.
    train = data[:(int((len(data)*0.55)))]
    test = data[(int((len(data)*0.25))):]
    
    # Modeling:
    # Using sklearn package to model data :
    regr = linear_model.LinearRegression(normalize=True)
    train_x = np.array(train[['DATE']])
    train_y = np.array(train[['NEWCASES']])
    regr.fit(train_x,train_y)
    # The coefficients:
    print ('coefficients : ',regr.coef_) #Slope
    print ('Intercept : ',regr.intercept_) #Intercept
    # Plotting the regression line:
    plt.scatter(train['DATE'], train['NEWCASES'], color='blue')
    plt.plot(train_x, regr.coef_*train_x + regr.intercept_, '-r')
    plt.xlabel('DATE')
    plt.ylabel('NEW CASES')
    #plt.show()
    
    # Predicting emission for future car:
    newDate = dateToPredict
    estimated_Cases = get_regression_predictions(newDate,regr.intercept_[0],regr.coef_[0][0])
    print ('Estimated Cases :',estimated_Cases)
    
    # Checking various accuracy:
    from sklearn.metrics import r2_score
    test_x = np.array(test[['DATE']])
    test_y = np.array(test[['NEWCASES']])
    test_y_ = regr.predict(test_x)
    print('Mean absolute error: %.2f' % np.mean(np.absolute(test_y_ - test_y)))
    print('Mean sum of squares (MSE): %.2f' % np.mean((test_y_ - test_y) ** 2))
    print('R2-score: %.2f' % r2_score(test_y_ , test_y) )
    
    return estimated_Cases


def PredictCasesLasso(dateToPredict):
    data = pd.read_csv('COVID.csv')
    data.head()
    # Let’s select some features to explore more :
    data = data[['DATE','NEWCASES']]
    
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    model = LassoCV(alphas=arange(0, 1, 0.01), cv=cv, n_jobs=-1)
    # fit model
    model.fit(data[['DATE']], data[['NEWCASES']])
    # summarize chosen configuration
    print('alpha: %f' % model.alpha_)
        
    
    # evaluate model
    scores = cross_val_score(model, data[['DATE']], data[['NEWCASES']], scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
    # force scores to be positive
    scores = absolute(scores)
    print('Mean MAE: %.3f (%.3f)' % (mean(scores), std(scores)))
    # make a prediction
    estimated_Cases = model.predict([[dateToPredict]])
    # summarize prediction
    print('Estimated Cases: %.3f' % estimated_Cases)
    return estimated_Cases[0]

def PredictDeathsLasso(casesToPredict):
    data = pd.read_csv('COVID.csv')
    data.head()
    # Let’s select some features to explore more :
    data = data[['NEWCASES','NEWDEATHS']]
    
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    model = LassoCV(alphas=arange(0, 1, 0.01), cv=cv, n_jobs=-1)
    # fit model
    model.fit(data[['NEWCASES']], data[['NEWDEATHS']])
    # summarize chosen configuration
    print('alpha: %f' % model.alpha_)
    
    # evaluate model
    scores = cross_val_score(model, data[['NEWCASES']], data[['NEWDEATHS']], scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
    # force scores to be positive
    scores = absolute(scores)
    print('Mean MAE: %.3f (%.3f)' % (mean(scores), std(scores)))
    # make a prediction
    estimated_Deaths = model.predict([[casesToPredict]])
    # summarize prediction
    print('Estimated Deaths: %.3f' % estimated_Deaths)
    return estimated_Deaths[0]

startDate = 348
cases = PredictCasesLasso(startDate)
print('')
deaths = PredictDeathsLasso(cases)
print('')
print('')
print(str(round(cases, 2)) + ' New Cases and ' + str(round(deaths, 2)) + ' New Deaths Predicted For Texas Tomorrow')
print('')

# for i in range(50):
#     cases = PredictCases(startDate)
#     print('')
#     deaths = PredictDeaths(cases)
#     print('')
#     print('')
#     print(str(round(cases, 2)) + ' New Cases and ' + str(round(deaths, 2)) + ' New Deaths Predicted For Texas Tomorrow')
#     print('')
#     startDate += 1