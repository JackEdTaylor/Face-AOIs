'''
Joins output from Tobii Data Export with AOI data from 'analyse_vid_faces.py'
Will write to the Tobii Data Export csv file

Tobii output should have:

RecordingTimestamp
LocalTimeStamp
EyeTrackerTimestamp
FixationIndex
SaccadeIndex
GazeEventType
GazeEventDuration
FixationPointX (MCSpx)
FixationPointY (MCSpx)
SaccadicAmplitude
AbsoluteSaccadicDirection
RelativeSaccadicDirection
GazePointIndex
GazePointLeftX (ADCSpx)
GazePointLeftY (ADCSpx)
GazePointRightX (ADCSpx)
GazePointRightY (ADCSpx)
GazePointX (ADCSpx)
GazePointY (ADCSpx)
GazePointX (MCSpx)
GazePointY (MCSpx)
GazePointLeftX (ADCSmm)
GazePointLeftY (ADCSmm)
GazePointRightX (ADCSmm)
GazePointRightY (ADCSmm)
StrictAverageGazePointX (ADCSmm)
StrictAverageGazePointY (ADCSmm)

'''

import csv
import bisect
import sys

if len(sys.argv) != 4:
    print("Usage:\n"
          "  python combine.py eyetracking_data aoi_data output_csv"
          "\n\ne.g. python combine.py film_output.csv participant03_data.csv participant03_combined.csv")
    exit()

tobii_csv_file = str(sys.argv[1])  # ensure in csv format (.xlsx default from Tobii(?))

face_detection_file = str(sys.argv[2])  # this should come from running 'analyse_vid_faces.py'

output_csv_file = str(sys.argv[3])

# import csv files
def importCsv(targetFile):
    with open(targetFile, 'rt') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
        rowIter = 0
        global row
        row = {}
        for x in csvReader:
            if rowIter == 0:
                global headers
                headers = x
            else:
                if x:
                    if x[0] != '':  # added this and previous conditional to deal with any blank rows
                        row[rowIter] = x
            if x:
                if x[0] != '':
                    global lastLine
                    lastLine = rowIter-1
                    rowIter += 1

print('Importing...')

print("Eyetracking data:\t'{}'".format(tobii_csv_file))
importCsv(tobii_csv_file)
tobii_headers = headers
tobii_row = row
lastRowTimestamp = int(tobii_row[lastLine][0])
msPerLineEstimate = lastRowTimestamp/lastLine

print("Face AOI data:\t\t'{}'".format(face_detection_file))
importCsv(face_detection_file)
face_detect_headers = headers
face_detect_row = row
face_count = int(face_detect_headers[-1:][0][1:2])

print(' -Done\n')


# add necessary headers and set up column info for later
x_col = {}
y_col = {}
w_col = {}
h_col = {}
for faceNr in range(1, face_count+1):
    h1 = 'F{0} xPos'.format(faceNr)
    h2 = 'F{0} yPos'.format(faceNr)
    h3 = 'F{0} width'.format(faceNr)
    h4 = 'F{0} height'.format(faceNr)
    tobii_headers.extend([h1, h2, h3, h4])
    x_col[faceNr] = face_detect_headers.index('F{} xPos'.format(faceNr))
    y_col[faceNr] = face_detect_headers.index('F{} yPos'.format(faceNr))
    w_col[faceNr] = face_detect_headers.index('F{} width'.format(faceNr))
    h_col[faceNr] = face_detect_headers.index('F{} height'.format(faceNr))

# combine the lists from here
# match ms
face_ms_list = []
for y in face_detect_row:
    face_ms_list.append(face_detect_row[y][1])

percentage = 0
for x in tobii_row:
    print("Compiling Face AOI data with Eyetracking data ({}%)... \r".format(percentage), end='')
    tobii_ms = tobii_row[x][0]
    tryout_iter = 0
    for tryout in face_ms_list:
        tryout_iter += 1
        try:
            if int(tryout)>int(tobii_ms):
                match_ms = int(tryout)
                match_row = int(tryout_iter)
                break
        except:
            pass
    for z in range(0, face_count):
        try:
            xPos = face_detect_row[match_row][x_col[z + 1]]
            yPos = face_detect_row[match_row][y_col[z + 1]]
            width = face_detect_row[match_row][w_col[z + 1]]
            height = face_detect_row[match_row][h_col[z + 1]]
            tobii_row[x].extend([xPos, yPos, width, height])
        except:
            pass
    percentage = '{}'.format(round((x/len(tobii_row))*100))

print('\n -Done\n')

# write to csv
print("Saving to '{}'...".format(output_csv_file))
try:
    # headers
    with open(output_csv_file, 'w', newline='') as csvfile:
        dataexporter=csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        dataexporter.writerow(tobii_headers)
    # rows
    with open(output_csv_file, 'a', newline='') as csvfile:
        for n in tobii_row:
            dataexporter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            dataexporter.writerow(tobii_row[n])
except PermissionError:
    print(" -ERROR\nPermissionError: Cannot write to '{}'.\nCheck it's not open in another program and that this user has permission to edit.".format(output_csv_file))
    exit()
print(' -Done\n')