import pyzbar.pyzbar as pyzbar 
import numpy as np              # pip install numpy
import cv2                      # pip install opencv-python

# 바코드 탐지하는 엔진 (바코드 및 QR코드 탐지)
def decode(im):
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)

    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data, '\n')

    return decodedObjects


# Display barcode and QR code location
def display(im, decodedObjects):
    # Loop over all decoded objects
    for decodedObject in decodedObjects:
        points = decodedObject.polygon

        # If the points do not form a quad, find convex hull
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points;

        # Number of points in the convex hull
        n = len(hull)

        # Draw the convext hull
        for j in range(0, n):
            cv2.line(im, hull[j], hull[(j + 1) % n], (255, 0, 0), 3)

    # Display results
    cv2.imshow("Results", im);
    cv2.waitKey(0);

# 파일명 zbar.jpg의 이미지에서 바코드를 탐지하면 해당 코드를 리턴
# Main
if __name__ == '__main__':
    # Read image
    im = cv2.imread('zbar.jpg')

    decodedObjects = decode(im)
    display(im, decodedObjects)
