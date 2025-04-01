# usage_logger.py
# Author: Janez Pavel Žebovec
# Date: 2025-03-29
# Description: Program for visualization of computer usage on base of CSV loggins.

import os
import datetime

# Dictionaries ===========================================================================================================================

actions = {
    "startup" : {"implied_state": "notusing", "sus_previous_state": ["startup","resume", "suspend", "lock", "unlock", None],},
    "shutdown" : {"implied_state": "using", "sus_previous_state": ["shutdown", None],},
    "resume" : {"implied_state": "notusing", "sus_previous_state": ["shutdown", "resume", None],},
    "suspend" : {"implied_state": "using", "sus_previous_state": ["shutdown", "suspend", "lock", None],},
    "unlock" : {"implied_state": "notusing", "sus_previous_state": ["shutdown", "unlock", None],},
    "lock" : {"implied_state": "using", "sus_previous_state": ["shutdown", "suspend", "lock", None],},
    }

states = {
    "using" : "|",
    "notusing" : ".",
    "sus_using" : "'",
    "sus_notusing": ",",
    "both": ":"
    }

units = [1, 2, 5, 10, 15, 20, 30, 40, 45, 60, 90, 120] #available sizes of units

# Functions ====================================================================================================================================================

def writePeriod(graph, chars, pTMin, tMin, pAction, action, totDayTime, totTime, unit):

    perFullUnits = max(0, tMin // unit - chars) #number of full units for period before current action - 0/negative is in case the time difference between times is too small for unit
    chars += perFullUnits

    if pAction in actions[action]["sus_previous_state"]: #if previous action is on list of suspicious previous action of current action
        state = "sus_" + actions[action]["implied_state"] #it's suspicious - there was probably some crashing in that period
    else:
        state = actions[action]["implied_state"]

    graph += states[state] * perFullUnits
    
    if state == "using":
        duration = tMin - pTMin
        totDayTime += duration
        totTime += duration

    if tMin % unit: #time over full unit - time less than one unit
        chars += 1
        graph += states["both"]

    pTMin = tMin
    return graph, chars, pTMin, pAction, totDayTime, totTime

#====================================================================================================================================================

file_path = 'filepath.csv'

if os.stat(file_path).st_size == 0: #check if CSV file is empty
    sys.exit("Error - CSV file is empty!")

columnsG = os.get_terminal_size().columns - 17 #get width of terminal minus 17 character beside graph (for date nad total day usage)
unit = next((u for u in units if 1440 / u <= columnsG), max(units)) #number of units per day must be equal or smaller than width of terminal (minus 17), to fit in; if none is big enough, use biggest unit
print("1 unit =", unit, "min")

graph = ""
days = 0 #days of usage
chars = 0 #number of characters in graph already

totDayTime = 0 #total time of usage for current day
totTime = 0 #total time of all logged usage

date = None

pAction = None #previous action
pDate = None #previous date
pTMin = 0 #time of previous action in minutes

with open(file_path, 'r') as csvfile: #open CSV file with logged times and actions
    for line in csvfile:
        timestamp, action = map(str.strip, line.split(",")[:2])
        date, time = timestamp.split()
        hh, mm, ss = map(int, time.split(":"))

        if date != pDate and pDate is not None: #if we get to new date, before starting new day, we must finish previous one:

            graph, chars, pTMin, pAction, totDayTime, totTime = writePeriod(graph, chars, pTMin, 1440, pAction, action, totDayTime, totTime, unit)

            print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") #print line for previous day
            chars = 0
            totDayTime = 0
            days += 1
            graph = ""
            pTMin = 0

        tMin = int(hh * 60 + mm) #time of current action in minutes
        tFullUnits = tMin // unit #time in number of full units
        tLess = tMin % unit #time over full unit - time less than one unit

        graph, chars, pTMin, pAction, totDayTime, totTime = writePeriod(graph, chars, pTMin, tMin, pAction, action, totDayTime, totTime, unit)

        ## Preparation for next line of CSV
        pDate = date
        pAction = action

#Remove this section, if you don't want only visualize logged usage (without current) - you would maybe just want to close last logged day with that section-------------
## We went through all lines of CSV - finishing line of current day
if date is not None:
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    if date != pDate: #if we are of not-yet-logged date, we need to finish previous day first (it's possible only if you stay on computer too late in night)
        graph, chars, pTMin, pAction, totDayTime, totTime = writePeriod(graph, chars, pTMin, 1440, pAction, action, totDayTime, totTime, unit)

        print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") #print line for previous day
        chars = 0
        totDayTime = 0
        days += 1
        graph = ""

    now = datetime.datetime.now() #get current time
    nowTMin = now.hour * 60 + now.minute #current time in minutes

    graph, chars, pTMin, pAction, totDayTime, totTime = writePeriod(graph, chars, pTMin, nowTMin, pAction, "shutdown", totDayTime, totTime, unit)

    print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") # Print day to noW

    if date != pDate:
        duration = nowTMin - pTMin
        totTime -= duration #to use only closed days for calculating average usage per day
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

aveTime = totTime / days
print(f"Average usage: {int(aveTime // 60)} hours and {int(aveTime % 60)} minutes per day")
print(f"Total loged time: {int((totTime) // 60)} hours and {int(totTime % 60)} minutes in {days} days")
