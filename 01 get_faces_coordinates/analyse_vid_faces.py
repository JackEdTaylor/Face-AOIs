import cv2
import sys
import csv

if len(sys.argv) != 3:
    print("Usage:\n"
          "python analyse_vid_faces.py video_path expected_faces\n\n"
          "e.g. python analyse_vid_faces.py recording.mp4 1")
    exit()


#video input setup
videoPath = sys.argv[1]
video_capture = cv2.VideoCapture(videoPath)

# How many faces do you expect to detect? (detects the N most probable faces)
face_detection_limit = int(sys.argv[2])

# Do you want to display additional windows, one for each face
displayFaceWindows=True

#csv output setup
saveOutput=True
if saveOutput:
    outputPath = "{}_AOIs.csv".format(videoPath[:-4])
    csvHeadings = ['Frame', 'Ms', 'Percentage Complete', 'Faces Count']
    for x in range(0, face_detection_limit):
        csvHeadings.append('F{} xPos'.format(x+1))
        csvHeadings.append('F{} yPos'.format(x+1))
        csvHeadings.append('F{} width'.format(x+1))
        csvHeadings.append('F{} height'.format(x+1))
        csvHeadings.append('F{} weight'.format(x+1))
    with open(outputPath, 'w') as csvfile:
        outF = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        outF.writerow(csvHeadings)
else:
    outputPath = "N/A"

# Video output setup
outputVideo=True
if outputVideo:
    outputVideoPath='{}_AOIs.avi'.format(videoPath[:-4])
    # define codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # get relevant info for video output
    cap = video_capture
    vidFps = float(cap.get(cv2.CAP_PROP_FPS))
    vidWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vidHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # video output settings
    out = cv2.VideoWriter(outputVideoPath,fourcc, vidFps, (vidWidth,vidHeight))
else:
    outputVideoPath = "N/A"

#cascade setup
faceCascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(faceCascPath)

#display various data about the video from cv2
print("\nVideo:\t{}".format(videoPath))
cap = video_capture
vidFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print("Frames:\t{}".format(vidFrames))
vidFps = float(cap.get(cv2.CAP_PROP_FPS))
print("Fps:\t{}".format(vidFps))
vidWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
vidHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Size:\t{0} x {1}".format(vidWidth, vidHeight))
print("")
print("Face Cascade:\t{}".format(faceCascPath))
print("Faces Expected:\t{}".format(face_detection_limit))
print("")
print("CSV Output:\t{}".format(outputPath))
print("Video Output:\t{}".format(outputVideoPath))
print("")
input("Press enter to begin...")
print("")
beginProcess=True

faceTotal=0
faceMax=0
currentFrame=0
font = cv2.FONT_HERSHEY_SIMPLEX
#while True:
while video_capture.isOpened() and beginProcess and currentFrame!=vidFrames:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame_raw = frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #detectMultiScale3 organises data slightly differently from detectMultiScale, but allows for confidence values (weights)
    facesdMS3 = faceCascade.detectMultiScale3(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        # cv2.cv.CV_HAAR_SCALE_IMAGE
        flags=cv2.CASCADE_SCALE_IMAGE,
        outputRejectLevels = True
    )
    faceWeights=facesdMS3[2]
    faceNeighbours=facesdMS3[1]


    # Draw a rectangle around any faces and record in dictionary(/ies)
    faceCount=0
    faceDict = {}
    faceDictX = {}
    faceDictY = {}
    faceDictW = {}
    faceDictH = {}
    faceDictWeight = {}
    for (f_x, f_y, f_w, f_h) in facesdMS3[0]:
        # Check if reached expected number of faces detected
        if faceCount==face_detection_limit:
            break
        else:
            faceCount+=1
            faceTotal+=1
            faceID="F{}".format(faceCount)
            faceDict[faceID]="x:{0}, y:{1}, w:{2}, h:{3}, weight:{4}".format(f_x, f_y, f_w, f_h, faceWeights[faceCount-1][0])
            faceDictX[faceID]=f_x
            faceDictY[faceID]=f_y
            faceDictW[faceID]=f_w
            faceDictH[faceID]=f_h
            faceDictWeight[faceID]=faceWeights[faceCount-1][0]
            # Display faces with weights in other windows
            if displayFaceWindows:
                faceCropped = frame[f_y:f_y+f_h, f_x:f_x+f_w]
                faceCropped = cv2.resize(faceCropped, (200, 200))
                cv2.putText(faceCropped, "Frame: {0}".format(currentFrame), (2, 182), font, 0.35, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.putText(faceCropped, "Weight: {0}".format(round(faceWeights[faceCount - 1][0], 2)), (2, 195), font, 0.35, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.imshow('F{}'.format(faceCount), faceCropped)
            # Draw rectangle around face on frame
            cv2.rectangle(frame, (f_x, f_y), (f_x + f_w, f_y + f_h), (0, 255, 0), 2)
            # Add text below rectangle for face ID and weight
            cv2.putText(frame, "{0} ({1})".format(faceID, round(faceWeights[faceCount - 1][0], 2)), (f_x, f_y + f_h + 20), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, "Frame: {0}/{1}".format(currentFrame, vidFrames), (10, vidHeight-10), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)


    # Display text indicating whether or not each expected face is active
    faceCheckIter=1
    for x in range(0, face_detection_limit):
        if 'F{}'.format(x+1) in faceDict:
            givenWeight=faceDictWeight['F{}'.format(x+1)]
            face_active='ACTIVE ({})'.format(round(givenWeight, 2))
            colour=(0, 255, 0)
        else:
            face_active='INACTIVE'
            colour=(0, 0, 255)
        cv2.putText(frame, "F{0}: {1}".format(x+1, face_active), (10, 20*faceCheckIter), font, 0.6, colour, 1, cv2.LINE_AA)
        faceCheckIter+=1

    # Display the resulting main frame (resized to be more convenient)
    frame_small = cv2.resize(frame, (0,0), fx=0.6, fy=0.6)
    cv2.imshow('Video', frame_small)

    # Display blank windows at startup for expected faces if additional windows selected
    if displayFaceWindows:
        if faceTotal == 0:
            for x in range(0, face_detection_limit):
                faceCropped = frame[0:1, 0:1]
                faceCropped = cv2.resize(faceCropped, (200, 200))
                cv2.imshow('F{}'.format(x+1), faceCropped)


    # Get current info:
    currentFrame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    currentMs = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    percentDone = "{}".format(round((currentFrame/vidFrames)*100, 2))
    faceMean=float("{}".format(round(faceTotal/currentFrame, 2)))

    if faceCount>faceMax:
        faceMax=faceCount

    # Display status
    print("Frame: {0}/{1}  Ms: {2} ({3}% done)  Faces: {4}\nFACES: mean={5} max={6} \r".format(currentFrame, vidFrames, currentMs, percentDone, faceCount, faceMean, faceMax), end='')

    # Save frame's data to output file
    if saveOutput==True:
        with open(outputPath, 'a') as csvfile:
            outF = csv.writer(csvfile, delimiter=',')
            csvData=[currentFrame, currentMs, percentDone, faceCount]
            for x in range(0, face_detection_limit):
                try:
                    csvData.append(faceDictX['F{}'.format(x+1)])
                    csvData.append(faceDictY['F{}'.format(x+1)])
                    csvData.append(faceDictW['F{}'.format(x+1)])
                    csvData.append(faceDictH['F{}'.format(x+1)])
                    csvData.append(faceDictWeight['F{}'.format(x+1)])
                except:
                    pass
            outF.writerow(csvData)

    # Video output
    if outputVideo:
        out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and output
video_capture.release()
try:
    out.release()
except:
    pass
cv2.destroyAllWindows()

print("\n\n -Done.")
print("Written ROI data to '{}'".format(outputPath))
if outputVideo:
    print("Written video to '{}'".format(outputVideoPath))
