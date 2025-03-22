# Python visualizer of computer usage

## Input

This script recieves input of CSV file of actions in form like `YYY-MM-DD HH:MM:SS, action`.

Example of input:

```csv
2025-03-22 16:04:12, startup

2025-03-22 16:42:30, shutdown
```

You have to replace "filepath" in 3rd line of script with your real file path to CSV file.

Example of edited file path:

```py
csvfile = open('/home/janezpavel/logs/usage_times.csv', 'r')
```

## Output

Output accuracy depends on terminal width - on unit can be from 1 minute to 120 minutes large.

Default "." (dot) indicates the time of non-use, "|" the time of use.

Additionally, "'" (apostrophe) is used for the time between two starts of use - which means that a system crash most likely occurred during this period, resulting in the shutdown/sespension/locking not being recorded; and "," (comma) for the time between two ends of use - shutdown/suspension/locking (which is quite unlikely).

Example of output:
```
1 unit = 15 min
2025-03-18 ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''':::........ 00:05
2025-03-19 ..........................................................:|::||||||||:::.......:|||||||||||:... 06:23
2025-03-20 ............................................................|||||||||::|||||:::::.......::::.... 05:17
2025-03-21 ................................................................:||||||||||||||:.:|||||||||||||: 07:09
2025-03-22 .....................................::..::::.:::::::::|||::|||||||:.:||||||::||:..:||||||| 08:39
Average usage: 06:53 per day
Total loged time: 27:33 in 4 days
```
