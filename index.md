# Python visualizer of computer usage

## Input

**You have to replace "filepath.csv" with your real file path to CSV file.**

Example of edited file path:

```py
file_path = '/home/janezpavel/logs/usage_times.csv'
```

This script recieves input of CSV file with lines for each actions in form like `YYY-MM-DD HH:MM:SS, action`.

Example of input:

```csv
2025-03-22 16:04:12, startup
2025-03-22 16:42:30, lock
2025-03-22 16:42:30, unlock
2025-03-22 16:42:30, suspend
2025-03-22 16:42:30, resume
2025-03-22 16:42:30, shutdown
```

## Output
Output accuracy depends on terminal width - one unit can vary from 1 minute to 120 minutes in size.

* "." (dot) indicates the time of notuse

* "|" the time of use

* ":" time of partial use.

Additionaly:

* "'" (apostrophe) is used for the time between two starts of use - which means that a system crash most likely occurred during this period, resulting in the shutdown/sespension/locking not being recorded;

* "," (comma) for the time between two ends of use - shutdown/suspension/locking (which is quite unlikely).

Example of output:
```txt
1 unit = 15 min
2025-03-18 ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''':::........ 00:05
2025-03-19 ..........................................................:|::||||||||:::.......:|||||||||||:... 06:23
2025-03-20 ............................................................|||||||||::|||||:::::.......::::.... 05:17
2025-03-21 ................................................................:||||||||||||||:.:|||||||||||||: 07:09
2025-03-22 .....................................::..::::.:::::::::|||::|||||||:.:||||||::||:..:||||||| 08:39
Average usage: 06:53 per day
Total loged time: 27:33 in 4 days
```

You can choose your preferred symbols for visualization editing variable `states`:
```py
states = {
    "using" : "|",
    "notusing" : ".",
    "sus_using" : "'",
    "sus_notusing": ",",
    "both": ":"
    }
```
or choose preferred units sizes with editing variable `units`:
```py
units = [1, 2, 5, 10, 15, 20, 30, 40, 45, 60, 90, 120]
```

If you want visualize only logged activity, you would remove this section:
```py
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
```
Or if you want to close last logged day too, replace it with:
```py
if date is not None:
        graph, chars, pTMin, pAction, totDayTime, totTime = writePeriod(graph, chars, pTMin, 1440, pAction, action, totDayTime, totTime, unit)
        print(pDate, graph, f"{int(totDayTime // 60):02d}:{int(totDayTime % 60):02d}") #print line for previous day
```

## Logging activities
### Shutdown and startup
This works on [Linux Debian](https://www.debian.org/) with [systemd](https://systemd.io/).

In folder /etc/systemd/system create file, named for example "log-shutdown.service" (suffix ".service is needed) and there insert:
```c
[Unit]
Description=Log shutdown time
DefaultDependencies=no
Before=shutdown.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo "$$(date +%%Y-%%m-%%d\ %%H:%%M:%%S), shutdown" >> filepath.csv'

[Install]
WantedBy=halt.target poweroff.target reboot.target
```
Create file, named for example "log-startup.service" (suffix ".service is needed) and there insert:
```c
[Unit]
Description=Log startup time

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo "$$(date +%%Y-%%m-%%d\ %%H:%%M:%%S), startup" >> filepath.csv'

[Install]
WantedBy=multi-user.target
```

### Lock/unlock
If using [slock (Simple X display locker of Suckless.org)](https://tools.suckless.org/slock/):

At start of file "slock.c", insert
```c
#include <time.h>
```
, which enables use of time/localtime/strftime functions.

In `main`function, after
```c
if (nlocks != nscreens)
  return 1;
```
, which checks if everything is locked, insert
```c
{
  char command[512];
  char date_str[20]; // Buffer to store the date
  time_t now = time(NULL);
  struct tm *tm_info = localtime(&now);
    
  // Format the current date and time
  strftime(date_str, sizeof(date_str), "%Y-%m-%d %H:%M:%S", tm_info);
    
  // Create the command to log the locking time
  snprintf(command, sizeof(command), "echo \"%s, lock\" >> $filepath.csv", date_str);
    
  // Execute the command
  system(command);
}
```
and after
```c
readpw(dpy, &rr, locks, nscreens, hash);
```
, which waits for correct password, insert:
```c
{
  char command[512];
  char date_str[20]; // Buffer to store the date
  time_t now = time(NULL);
  struct tm *tm_info = localtime(&now);

  // Format the current date and time
  strftime(date_str, sizeof(date_str), "%Y-%m-%d %H:%M:%S", tm_info);

  // Create the command to log the unlocking time
  snprintf(command, sizeof(command), "echo \"%s, unlock\" >> $filepath.csv", date_str);
    
  // Execute the command
  system(command);
}
```
