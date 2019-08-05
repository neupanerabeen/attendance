import pandas as pd
import sys
from datetime import *
import xlrd
from functools import reduce

# evening entry min ts
EVENING_ENTRY_MIN_HR = 12
EVENING_ENTRY_MAX_HR = 15
EVENING_EXIT_MIN_HR = 20
EVENING_EXIT_MAX_HR = 23


# morning entry min ts
MORNING_ENTRY_MIN_HR = 5
MORNING_ENTRY_MAX_HR = 9
MORNING_EXIT_MIN_HR = 12
MORNING_EXIT_MAX_HR = 16

# night entry min ts
# note that for night shift, entry is at higher time stamp. so negleting the ts and calculating the min/max ts for each day.
# mondays are exception here
NIGHT_ENTRY_MIN_HR = 4
NIGHT_ENTRY_MAX_HR = 9
NIGHT_EXIT_MIN_HR = 21
NIGHT_EXIT_MAX_HR = 23


input_file = "SNS.xls"
output_file = "SNS_report.csv"

try:
	input_file = sys.argv[1]
except:
	pass

try:
	output_file = sys.argv[2]
except:
	pass

print("reading input file: {}".format(input_file))


#  reading input file into a dataframe
try:
	in_df = pd.read_excel(input_file)[["Name", "Time"]]
except FileNotFoundError:
	print("{} file not found".format(input_file))
	print("exiting now...")
	exit(-1)

def normalize_time(t):
	in_time = datetime.strptime(t, "%I:%M %p")
	return datetime.strftime(in_time, "%H:%M")



# splitting day and time for each entries
in_df["Date"] = in_df["Time"].map(lambda x: x.split(" ")[0])
in_df["Time"] = in_df["Time"].map(lambda x: " ".join(x.split(" ")[1:])).map(normalize_time)
in_df["_ts"] = in_df["Time"].map(lambda x: x.split(":")).map(lambda x: int(x[0])*60+int(x[1]))
tmp_df = in_df.groupby(["Name","Date"])["_ts"].describe()
tmp_df = tmp_df[["min", "max"]].astype(int)


tmp_df["Evening"] = tmp_df.apply(lambda x: 1 if x["max"] in range(EVENING_EXIT_MIN_HR * 60, EVENING_EXIT_MAX_HR * 60) and x["min"] in range(EVENING_ENTRY_MIN_HR * 60, EVENING_ENTRY_MAX_HR * 60) else 0, axis = 1 )
tmp_df["MORNING"] = tmp_df.apply(lambda x: 1 if x["max"] in range(MORNING_EXIT_MIN_HR * 60, MORNING_EXIT_MAX_HR * 60) and x["min"] in range(MORNING_ENTRY_MIN_HR * 60, MORNING_ENTRY_MAX_HR * 60) else 0, axis = 1 )
tmp_df["NIGHT"] = tmp_df.apply(lambda x: 1 if x["max"] in range(NIGHT_EXIT_MIN_HR * 60, NIGHT_EXIT_MAX_HR * 60) and x["min"] in range(NIGHT_ENTRY_MIN_HR * 60, NIGHT_ENTRY_MAX_HR * 60) else 0, axis = 1 )
tmp_df["max"] = tmp_df["max"]/60
tmp_df["min"] = tmp_df["min"]/60

tmp_df.to_csv(output_file)
print(tmp_df)