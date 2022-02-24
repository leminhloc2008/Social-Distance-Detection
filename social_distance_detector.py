import cv2
import numpy as np
import argparse
import imutils
import keyboard
from datetime import datetime
from scipy.spatial import distance as dist

parser = argparse.ArgumentParser()
parser.add_argument('--webcam', help="True/False", default=False)
parser.add_argument('--play_video', help="True/False", default=True)
parser.add_argument('--video_path', help="Video Path", default="Videos\Video3.mp4")
args = parser.parse_args()

def load_yolo():
    yolov3weightspath = "yolov3\yolov3.weights"
    yolov3configpath = "yolov3\yolov3.cfg"
    coconamespath = "yolov3\coco.names"

    net = cv2.dnn.readNet(yolov3weightspath, yolov3configpath)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    classes = []
    with open(coconamespath, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layers_names = net.getLayerNames()
    output_layers = [layers_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, classes, output_layers

def detect_objects(frame, net, outputLayers):
    blob = cv2.dnn.blobFromImage(frame, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(outputLayers)
    return blob, outputs

points = np.zeros((4,2),np.int)
count = 0

def getMousePoint(event,x,y,flags,prams):
    global count
    if event == cv2.EVENT_LBUTTONDOWN:
        points[count] = x,y
        count += 1

def computePerspectiveTransform(width,height,img):
    pts1 = np.float32([points[0], points[1], points[2], points[3]])
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    transformedImg = cv2.warpPerspective(img, matrix, (width, height))

    #return matrix,transformedImg
    return matrix

def computePointsPerspectiveTransformation(matrix,centerPointsList):
    list_points_to_detect = np.float32(centerPointsList).reshape(-1, 1, 2)
    transformedPoints = cv2.perspectiveTransform(list_points_to_detect, matrix)
    arrayTransformedPoints = []
    for i in range(0,transformedPoints.shape[0]):
        arrayTransformedPoints.append([transformedPoints[i][0][0],transformedPoints[i][0][1]])
    return arrayTransformedPoints

def social_distance_detection(cap):
    model, classes, output_layers = load_yolo()
    writer = None
    firstFrame = True
    startDetect = False

    while True:
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=700)
        height, width, channels = frame.shape

        while firstFrame:
            selectPoints = frame

            for x in range(0, 4):
                cv2.circle(selectPoints, (int(points[x][0]), int(points[x][1])), 3, (224, 224, 224), cv2.FILLED)

            cv2.putText(selectPoints, "Bam phim S de bat dau phan tich",
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.60, (224, 224, 224), 1)

            cv2.imshow("Chon diem", selectPoints)
            cv2.setMouseCallback("Chon diem", getMousePoint)
            key = cv2.waitKey(1)

            # draw lines between points
            if count == 2:
                cv2.line(selectPoints, points[0], points[1], (224, 224, 224), 2)

            if count == 3:
                cv2.line(selectPoints, points[0], points[2], (224, 224, 224), 2)

            if count == 4:
                cv2.line(selectPoints, points[2], points[3], (224, 224, 224), 2)
                cv2.line(selectPoints, points[3], points[1], (224, 224, 224), 2)

            if keyboard.is_pressed('s'):
                firstFrame = False
                startDetect = True

                # close selection pointframe
                cv2.destroyWindow("Chon diem")
                break

        if startDetect == True:
            # bird eye view
            #matrix, birdEyeImg = computePerspectiveTransform(width, height, frame)
            matrix = computePerspectiveTransform(width, height, frame)

            birdEyeImg = np.zeros((height, width, 3), dtype=np.uint8)
            birdEyeImg.fill(255)

            blob, outputs = detect_objects(frame, model, output_layers)
            boxes = []
            centerPoints = []
            results = []
            confs = []
            class_ids = []

            for output in outputs:
                for detect in output:
                    scores = detect[5:]
                    class_id = np.argmax(scores)
                    conf = scores[class_id]
                    if conf > 0.5 and class_id == 0:
                        center_x = int(detect[0] * width)
                        center_y = int(detect[1] * height)
                        w = int(detect[2] * width)
                        h = int(detect[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        centerPoints.append((center_x, center_y))
                        confs.append(float(conf))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)

            birdEyePoints = computePointsPerspectiveTransformation(matrix, centerPoints)

            # if there are more than 2 people in area
            if len(indexes) > 0:
                # duyet qua tung nguoi
                flatted = indexes.flatten()
                for i in flatted:
                    # get coordinate
                    (x, y) = (boxes[i][0], boxes[i][1])
                    (w, h) = (boxes[i][2], boxes[i][3])

                    # update result
                    r = (confs[i], (x, y, x + w, y + h), birdEyePoints[i], centerPoints[i])
                    results.append(r)

            violate = set()

            if len(results) >= 2:
                # get midpoints
                midPoints = np.array([r[2] for r in results])
                visualMidPonts = np.array([r[3] for r in results])

                # caculate distance between 2 mid point use euclidean
                distBw = dist.cdist(midPoints, midPoints, metric="euclidean")

                # duyet qua khoan cach tung nguoi
                for i in range(0, distBw.shape[0]):
                    for j in range(i + 1, distBw.shape[1]):
                        # if smaller than 2,
                        if distBw[i, j] < 110:
                            # draw line
                            cv2.line(frame, visualMidPonts[i], visualMidPonts[j], (0, 0, 255), 2)

                            # add to violate list
                            violate.add(i)
                            violate.add(j)

            font = cv2.FONT_HERSHEY_PLAIN
            for (i, (prob, bbox, birdCenterPoint, centerPoint)) in enumerate(results):
                # lay du lieu (toa do, diem o giua)
                (startX, startY, endX, endY) = bbox
                (cX, cY) = centerPoint
                (cvX, cvY) = birdCenterPoint

                print(cvX,cvY)

                # if violate then change bouding box color to red
                if i in violate:
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    cv2.circle(frame, (cX, cY), 3, (0, 0, 255), cv2.FILLED)
                    #cv2.circle(birdEyeImg, (int(cvX), int(cvY)), 3, (0, 0, 255), cv2.FILLED)
                    #cv2.circle(birdEyeImg, (int(cX), int(cY)), 3, (0, 0, 255), cv2.FILLED)

                # else (not violate) change to green
                else:
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    cv2.circle(frame, (cX, cY), 3, (0, 255, 0), cv2.FILLED)
                    #cv2.circle(birdEyeImg, (int(cvX), int(cvY)), 3, (0, 255, 0), cv2.FILLED)
                    #cv2.circle(birdEyeImg, (int(cX), int(cY)), 3, (0, 255, 0), cv2.FILLED)

                # hien thi
                cv2.putText(frame, "Tong so nguoi: " + str(len(indexes)),
                            (10, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 0, 0), 2)
                cv2.putText(frame, "So nguoi khong tuan thu: " + str(len(violate)),
                            (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 0, 255), 2)
                cv2.putText(frame, "So nguoi tuan thu: " + str(len(indexes) - len(violate)),
                            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 255, 0), 2)

        # show frame
        cv2.imshow("Phan tich gian cach xa hoi", frame)

        key = cv2.waitKey(1)

        # close frame
        if cv2.getWindowProperty("Phan tich gian cach xa hoi", 1) < 0:
            break

        # export video
        if writer is None:
            date_time = datetime.now().strftime("%m-%d-%Y %H-%M-%S")
            OUTPUT_PATH = 'output\output {}.avi'.format(date_time)
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            writer = cv2.VideoWriter(OUTPUT_PATH, fourcc, 30, (frame.shape[1], frame.shape[0]), True)
        writer.write(frame)

    cap.release()
    writer.release()

def webcam_detect():
    cap = cv2.VideoCapture(0)
    social_distance_detection(cap)

def start_video(video_path):
    cap = cv2.VideoCapture(video_path)
    social_distance_detection(cap)

def streamCam(streamUrl):
    cap = cv2.VideoCapture(streamUrl)
    social_distance_detection(cap)

def passCam(username, password):
    cap = cv2.VideoCapture("rtsp://" + username + ':' + password + "@192.168.1.64/1")
    social_distance_detection(cap)

if __name__ == '__main__':
    webcam = args.webcam
    video_play = args.play_video
    if webcam:
        webcam_detect()
    if video_play:
        video_path = args.video_path
        start_video("Videos\PETS2009.avi")

    cv2.destroyAllWindows()