"""
File: covid_vax_trend.py
-------------------------
This program wil plot the daily trends of COVID vaccinations 
for a given state, or all states, in the United States of America,
for a given date range entered by the user.

The source file is the csv file located at:
    https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-Jurisdi/unsk-b7fc/data
This file has been downloaded as covid_vax.csv
"""

import csv

# for making graphs
import seaborn as sns
import matplotlib.pyplot as plt

#for converting string date into date value
from datetime import datetime, timedelta

#Establish data filename
FILENAME = "vax_data.csv"

def get_state():
    """
    Gets a state within the United States and territories from the user, 
    but doesn't check that the user types in valid state names. 
    Returns the desired state
    """
    state = input("Enter a two letter state abbreviation, or 'all'. Press enter to finish: ").strip().lower()
    return state

def get_vaxed(state, start_date, end_date):
    #Create empty vaccination dictionary
    vaxed = {}

    with open(FILENAME) as f:
        reader = csv.DictReader(f)

        for line in reader:
            location = line['Location'].lower()

            #if the state matches the user input then retrieve the vaccinations adminstered for that state by date
            #if the user enters 'all', the vaccinations administered are aggregated by date
            if location == state or state == 'all':
                #convert csv date text into a date object, 
                #so that the dictionary sorts properly
                    #with help from 
                        #https://stackoverflow.com/questions/9504356/convert-string-into-date-type-on-python
                        #user 'Fred'
                vax_date = convert_string_to_date(line['Date']) 
                #Check if the line date is within the starting or ending date range
                if vax_date >= start_date and vax_date <= end_date:
                    administered = int(line['Administered'])
                    #if the date is not in the vaxed dictionary then add it and the administered value
                    #otherwise, increment the value administered for that date for all locations
                    if vax_date not in vaxed:
                        vaxed[vax_date] = administered
                    else:
                        vaxed[vax_date] += administered
        #sorts the dictionary by date ordered
        #dictionary sorting code from 
            #https://stackoverflow.com/questions/9001509/how-can-i-sort-a-dictionary-by-key
            #Amit Prafulla
        vaxed = dict(sorted(vaxed.items(), key = lambda x:x[0]))
    return vaxed

def get_previous_day_vaxed(state, start_date):
    previous_day_vaxed = get_vaxed(state, start_date + timedelta(days=-1), start_date + timedelta(days=-1))
    if start_date == datetime(2020, 1, 1, 0, 0):
        previous_day_vaxed = 0
    else:
        previous_day_vaxed = previous_day_vaxed[start_date + timedelta(days=-1)]
    return previous_day_vaxed


def get_vaxed_daily(dict, previous_day):
    vaxed_daily={}

    print_daily = input("Print daily vaccinations? (y/n)").lower()
    if print_daily == "y":
        print("The vaccinations administered by day are:")

    for key in dict:
        #Subtracts the previous day's total from today's total to yield the daily value
        vaxed_daily[key] = dict[key] - previous_day
        
        if print_daily == "y":
            print(key.strftime("%m/%d/%Y") +": " + str(vaxed_daily[key]))
        previous_day = dict[key]

    #Changes the formatting of the key from datetime to str YYYY/MM/DD for better plotting display
    new_d={}
    #Calculates the first and last date in the dictionary.
    #if they are in the same year, the year is left off of the new ditionary
    #this was done to make the x axis on the plot more legible

    first_key = list(vaxed_daily.keys())[0]
    last_key = list(vaxed_daily.keys())[-1]
    
    for key in vaxed_daily:
        if first_key.year == last_key.year:
            #if the dictionary contains dates in the same year, drop the year from the dictionary
            new_d[key.strftime("%-m/%-d")] = vaxed_daily[key]
        else:
            new_d[key.strftime("%Y/%-m/%-d")] = vaxed_daily[key]
    vaxed_daily = new_d
    return vaxed_daily

def make_bar_plot(count_map):
    """
    Turns a dictionary (where values are numbers) into a bar plot.
    Labels gives the order of the bars! Uses a package called seaborn
    for making graphs.

    Code attributed to Lesson 14, Chris Piech
    """
    # turn the counts into a list
    counts = []
    # loop over the labels, in order
    for label in count_map:
        counts.append(count_map[label])
    # format the data in the way that seaborn wants
    data = {
        'x':list(count_map.keys()),
        'y':counts
    }
    sns.barplot(x = 'x',y = 'y', data= data)
    plt.savefig("plot.png")

def convert_string_to_date(str_date):
    month, day, year = map(int, str_date.split('/'))
    convert_string_to_date = datetime(year, month, day)
    return convert_string_to_date

def main():
    #Prompts the user for a state of their choice
        state = get_state()
        if state == "all":
            state_text = "for ALL of the United States"
        else:
            state_text = "for the state of " + state.upper()

    #Prompts the user for a starting and ending date range
        start_date = str(input("Enter the desired starting date (in mm/dd/yyyy), or 'all' for all dates: ")).lower()
        if start_date != "all":
            start_date = convert_string_to_date(start_date)
            end_date = convert_string_to_date(str(input("Enter the desired ending date (in mm/dd/yyyy): ")))
        else:
            start_date = convert_string_to_date("01/01/2020")
            end_date = convert_string_to_date("12/31/9999")

    #Retrieves and calculates the number vaccinated
    #Returns a dictionary of dates and cumulative vaccinations
        vaxed = get_vaxed(state, start_date, end_date)

    #Obtains the previous day's total vaccinations
        previous_day_vaxed = get_previous_day_vaxed(state, start_date)
        #previous_day_vaxed = list(previous_day_vaxed.values())[-1]

    #Calculates the daily incremental vaccinated
        vaxed_daily = get_vaxed_daily(vaxed, previous_day_vaxed)
        print("Total vaccinations for the date range for " + state_text + ": " + str(sum(vaxed_daily.values())))
    
    #Plots the vaxed daily results
        make_bar_plot(vaxed_daily)

if __name__ == '__main__':
    main()
