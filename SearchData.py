
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('COVID.db')  # You can create a new database by changing the name within the quotes
c = conn.cursor() # The database will be saved in the location where your 'py' file is saved

def SelectCounty(state,county, days):
    c.execute("SELECT * FROM COUNTIES WHERE STATE = ? AND COUNTY = ? ORDER BY pk_id DESC LIMIT ?",("{}".format(state.lower()),"{}".format(county),"{}".format(days)))
    rows = c.fetchall()
    
    for rows in rows:
        index = 0  
        print('')
        for item in rows:
            if index == 1:
                print('County: ' + str(item))
            elif index == 2:
                print('New Cases: ' + str(item))
            elif index == 3:
                print('New Deaths: ' + str(item))
            elif index == 4:
                print('Total Cases: ' + str(item))
            elif index == 5:
                print('Total Deaths: ' + str(item))
            elif index == 6:
                print('Updated: ' + str(item))
            index += 1


def SelectState(state,days):
    c.execute("SELECT * FROM STATES WHERE STATE = ? ORDER BY generated_id DESC LIMIT ?",("{}".format(state),"{}".format(days)))
    rows = c.fetchall()
    yAxis = []
    xAxis = []
    for row in rows:
        index = 0  
        print('')
        for item in row:
            if index == 1:
                print('State: ' + str(item))
            elif index == 2:
                print('Total Cases: ' + str(item))
            elif index == 3:
                print('New Cases: ' + str(item))
                yAxis.append(int(item.replace(',','').replace('','0')))
            elif index == 4:
                print('Total Deaths: ' + str(item))
            elif index == 5:
                print('New Deaths: ' + str(item))
            elif index == 6:
                print('Updated: ' + str(item))
                xAxis.append(item)
            index += 1
    # fig, ax = plt.subplots()  # Create a figure containing a single axes.
    # ax.plot(xAxis[::-1], yAxis[::-1])
    # fig.show()# Plot some data on the axes.
loop = True
while loop:
    try:
        print('')
        whichState = input('What State? ')
        whichState = whichState[0].upper() + whichState[1:]
        
        if whichState.lower() == 'close':
            break;
        
        stateDays = input('How many days? ')
        whichCounty = input('What County? ')
        countyDays = input('How many days? ')
        print('')
        
        if whichCounty == '':
            SelectState(whichState, stateDays)
        else:
            SelectCounty(whichState,whichCounty, countyDays)
    except Exception as e:
        print('Incorrect State, try again.')
        