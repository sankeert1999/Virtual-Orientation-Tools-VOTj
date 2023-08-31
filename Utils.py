#@ImagePlus imp
from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar,split,PCACompute
from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours
from ImageConverter import ImProcToMat,MatToImProc
from ij import ImagePlus
import math

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
    largest_contour_out -- The largest contour detected in the binary masks as a Mat.
    """
    # Create a MatVector to store detected contours
    listContour = MatVector()
    findContours(binary_masks, listContour, RETR_LIST, CHAIN_APPROX_NONE)
    
    # Calculate the area of each detected contour and store in the 'area' list
    area = []
    for i in range(listContour.size()):
        area.append(contourArea(listContour.get(i)))

    # Find the largest contour based on area
    max_value, max_value_index = getMax(area)
    largest_contour = listContour.get(max_value_index)
    
    # Convert the largest contour to a new Mat
    largest_contour_out = Mat()
    largest_contour.convertTo(largest_contour_out, 5)  # Convert to desired data type
    
    return largest_contour_out


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
   
def getOrientation(largest_contour):
    """
    Calculate the orientation angle of the largest contour.

    Arguments:
    largest_contour -- The largest contour detected.

    Returns:
    angle -- The orientation angle in degrees.
    """
    # Convert the largest_contour to a MatVector
    largest_contour_MV = MatVector()
    split(largest_contour, largest_contour_MV)
    
    # Determine the number of points in the contour
    sz = largest_contour.total()
    
    # Create a Mat to store contour points for PCA
    largest_contour_pca = Mat(sz, 2, 5)
    
    # Copy contour points to the Mat
    largest_contour_MV.get(0).copyTo(largest_contour_pca.col(0))
    largest_contour_MV.get(1).copyTo(largest_contour_pca.col(1))
    
    # Perform PCA to find mean, eigenvectors, and eigenvalues
    mean_pca = Mat()
    eigenvectors = Mat()
    PCACompute(largest_contour_pca, mean_pca, eigenvectors)
    
    # Convert eigenvectors to a CvMat for indexing
    eigenvectors_cvmat = CvMat(eigenvectors)
    
    # Calculate the angle of rotation based on eigenvectors
    angle = math.atan2(eigenvectors_cvmat.get(0, 1), eigenvectors_cvmat.get(0, 0))
    angle = int(math.degrees(angle))
    
    return angle

	
    
if __name__ in ['__main__', '__builtin__']:
    # Convert ImageProcessor to Mat using custom ImageConverter
    imMat = ImProcToMat(imp.getProcessor())
    # Use the converted image as binary mask
    binary_masks = imMat
    # Detect the largest contour in the binary mask
    largest_contour = detectContours(binary_masks)
    angle = getOrientation(largest_contour)
    print(angle)

    
	

	
	
	
	
	