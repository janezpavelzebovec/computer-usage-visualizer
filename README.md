# Python visualizer of computer usage

## Input
This script recieves input of CSV file of actions in form like `YYY-MM-DD HH:MM:SS, action`.

Example of input:

```csv
2025-03-22 16:04:12, startup

2025-03-22 16:42:30, shutdown
```

You have to replace "filepath" (in 3rd line of script) with your real file path to CSV file.

Example of edited file path:

```py
csvfile = open('/home/janezpavel/logs/usage_times.csv', 'r')
```

## Output
Output accuracy depends on terminal width - on unit can be from 1 minute to 120 minutes large.

Default "." (dot) indicates the time of not-use, "|" the time of use, and ":" time of partiall use.

Additionally, "'" (apostrophe) is used for the time between two starts of use - which means that a system crash most likely occurred during this period, resulting in the shutdown/sespension/locking not being recorded; and "," (comma) for the time between two ends of use - shutdown/suspension/locking (which is quite unlikely).

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

## Logging activities
### Shutdown and startup
This works on [Linux Debian](https://www.debian.org/) with [systemd](https://systemd.io/).

In folder /etc/systemd/system create file, named for example "log-shutdown.service" (suffix ".service is needed) and there include:
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
Create file, named for example "log-startup.service" (suffix ".service is needed) and there include:
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

At start of file "slock.c", include
```c
#include <time.h>
```
, which enables use of time/localtime/strftime functions.
In `main`function, after
```c
if (nlocks != nscreens)
  return 1;
```
, which checks if everything is locked, include
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
, which waits for correct password, include:
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

