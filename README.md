#Get Face-AOIs

Analyses a video to get coordinates and timestamps of a given number of faces. Then allows you to combine this information with raw Tobii eye-tracker output (can be adapted to work for eye-trackers).

First, run the video file through 'analyse_vid_faces.py', such as with:

python analyse_vid_faces.py recording.mp4 1

where:

'recording.mp4' is the video you want to analyse for faces

'1' is the number of faces you expect to find

This will also create a video output, drawing boxes around the AOIs on the original video, to demonstrate the coordinates and timecourse.

#Combine with eye-tracking output

Second, combine the output from the AOI analysis with the raw eyetracker data with 'combine.py'.

This works for Tobii output but has not yet been tested on other data.

python combine.py participant01_rec.csv recording_AOIs.csv output.csv

where:

'participant01_rec.csv' is the eye-tracking output

'recording_AOIs.csv' is the AOI data (output from analyse_vid_faces.py)

'output.csv' is the desired name of the output file, which will have the combined eye-tracking and AOI data
