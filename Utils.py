#@ImagePlus imp
from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar
from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours
from ImageConverter import ImProcToMat,MatToImProc
from ij import ImagePlus

def getMax(myList):
    """
    Find the maximum value and its index in the given list.

    Arguments:
    myList -- List containing numerical values.

    Returns:
    max_value -- The maximum value in the list.
    max_value_index -- The index of the maximum value in the list.
    """
    max_value = 0
    max_value_index = 0
    for i in range(len(myList)):
        if myList[i] > max_value:
            max_value = myList[i]
            max_value_index = i
    return max_value, max_value_index

def detectContours(binary_masks):
    """
    Detect contours in the given binary masks and return the largest contour.

    Arguments:
    binary_masks -- Binary mask image containing object regions.

    Returns:
    largest_contour -- The largest contour detected in the binary masks.
    """
    listContour = MatVector()
    findContours(binary_masks, listContour, RETR_LIST, CHAIN_APPROX_NONE)
    area = []
    for i in range(listContour.size()):
        area.append(contourArea(listContour.get(i)))

    max_value, max_value_index = getMax(area)
    largest_contour = listContour.get(max_value_index)
    return largest_contour


def contourCenterExtractor(largest_contour):
    """
    Extracts the center coordinates of a contour using its moments.

    Arguments:
    largest_contour -- The contour for which to calculate the center.

    Returns:
    Com_x -- The x-coordinate of the center.
    Com_y -- The y-coordinate of the center.
    """
    # Calculate the moments of the largest contour
    contour_Moments = moments(largest_contour)
    # Calculate the x and y coordinates of the center using moments
    Com_x = int(contour_Moments.m10() / contour_Moments.m00())
    Com_y = int(contour_Moments.m01() / contour_Moments.m00())
    return Com_x, Com_y
   
# Function to get orientation
#def getOrientation(pts):
	
    
if __name__ in ['__main__', '__builtin__']:
	# Convert ImageProcessor to Mat using custom ImageConverter
	imMat = ImProcToMat(imp.getProcessor())
	# Use the converted image as binary mask
	binary_masks = imMat
	# Detect the largest contour in the binary mask
	largest_contour = detectContours(binary_masks)
	jk=largest_contour.reshape(1,2)
	print(jk.rows())
	#print(Cvlargest_contour)
	Com_x, Com_y = contourCenterExtractor(largest_contour)
	print(Com_x, Com_y)
	

	
	
	
	
	