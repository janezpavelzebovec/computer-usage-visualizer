import os
import datetime

csvfile = open('/filepath', 'r')

if os.stat('filepath').st_size == 0:
    sys.exit("Error - CSV file is empty!")

columns = os.get_terminal_size().columns #get width of terminal

columnsG = columns - 17 #17 character beside graph (date, total time in day)
units = [1, 2, 5, 10, 15, 20, 30, 40, 45, 60, 90, 120]
for u in units:
    n_required = 1440 / u
    if n_required <= columnsG:
        unit = u
        break

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

for line in csvfile:
    timestamp, action = line.split(",")
    action = action.strip()
    date, time = timestamp.split(" ")
    hh, mm, ss = list(map(int, time.split(":")))

    if date != pDate and pDate is not None: #if we get to new date, before starting new day, we must finish previous one:

        tFullUnits = 1440 // unit #time of end of day in full units

        perFullUnits = tFullUnits - chars #number of full units for period before current action minus number of characters already written in graph
        chars += perFullUnits

        if action in ["startup", "resume", "unlock"]: #if current action (first action of day after closing one)
            if pAction in ["shutdown", "suspend", "lock"]: #it's expected to be so
                graph += "." * perFullUnits 
            else: #it's suspicious - there was probably some crashing in that period, so that computer wasn't shutdown in right way
                graph += "," * perFullUnits

        elif action in ["shutdown", "suspend", "lock"]: #if current action (first action of day after closing one)
            if pAction in ["startup", "resume", "unlock"]: #it's expected to be so
                duration = 1440 - pTMin #duration of period since previous (last action in closing day) to end of day in minutes
                totDayTime += duration
                totTime += duration
                graph += "|" * perFullUnits
            else: #it's suspicious - computer was shutdown/suspended/locked without being started/resumed/unlocked before that
                graph += "'" * perFullUnits

        print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") #print line for previous day
        chars = 0
        totDayTime = 0
        days += 1
        graph = ""

    tMin = int(hh * 60 + mm) #time of current action in minutes
    tFullUnits = tMin // unit #time in number of full units
    tLess = tMin % unit #time over full unit - time less than one unit

    if chars >= tFullUnits:
        perFullUnits = 0
    else:
        perFullUnits = tFullUnits - chars #number of full units for period before current action
    chars += perFullUnits

    if tLess != 0:
        chars += 1

    if action in ["startup", "resume", "unlock"]:
        if pAction in ["shutdown", "suspend", "lock"]:
            graph += "." * perFullUnits
            if tLess != 0:
                graph += ":"
        else:
            graph += "," * perFullUnits
            if tLess != 0:
                graph += ";"

    elif action in ["shutdown", "suspend", "lock"]:
        if pAction in ["startup", "resume", "unlock"]:
            duration = tMin - pTMin
            totDayTime += duration
            totTime += duration
            graph += "|" * perFullUnits
            if tLess != 0:
                graph += ":"
        else:
            graph += "'" * perFullUnits
            if tLess != 0:
                graph += ":"

    ## Preparation for next line of CSV
    pDate = date
    pTMin = tMin
    pAction = action

csvfile.close()

## We went through all lines of CSV - finishing line of current day
if date is not None:
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    if date != pDate: #we need to finish previous day first
        tFullUnits = 1440 // unit #time of end of day in full units

        perFullUnits = tFullUnits - chars #number of full units for period before current action minus number of characters already written in graph
        chars += perFullUnits

        if action in ["startup", "resume", "unlock"]: #if current action (first action of day after closing one)
            if pAction in ["shutdown", "suspend", "lock"]: #it's expected to be so
                graph += "." * perFullUnits 
            else: #it's suspicious - there was probably some crashing in that period, so that computer wasn't shutdown in right way
                graph += "," * perFullUnits

        elif action in ["shutdown", "suspend", "lock"]: #if current action (first action of day after closing one)
            if pAction in ["startup", "resume", "unlock"]: #it's expected to be so
                duration = 1440 - pTMin #duration of period since previous (last action in closing day) to end of day in minutes
                totDayTime += duration
                totTime += duration
                graph += "|" * perFullUnits
            else: #it's suspicious - computer was shutdown/suspended/locked without being started/resumed/unlocked before that
                graph += "'" * perFullUnits

        print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") #print line for previous day
        chars = 0
        totDayTime = 0
        days += 1
        graph = ""

    now = datetime.datetime.now()
    nowTMin = now.hour * 60 + now.minute
    
    tFullUnits = nowTMin //unit

    perFullUnits = tFullUnits - chars
    
    if pAction in ["shutdown", "suspend", "lock"]:
        graph += "." * perFullUnits

    elif pAction in ["startup", "resume", "unlock"]:
        duration = nowTMin - pTMin
        totDayTime += duration
        totTime += duration
        graph += "|" * perFullUnits

    print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") # Print day to now

aveTime = totTime / days
print(f"Average usage: {int(aveTime // 60):02d}:{int(aveTime % 60):02d} per day")
print(f"Total loged time: {int(totTime // 60):02d}:{int(totTime % 60):02d} in {days} days")

