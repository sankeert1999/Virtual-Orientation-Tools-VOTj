#@ImagePlus imp
from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar,split,PCACompute,Point2f,Size,cvmSet
from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours,getRotationMatrix2D,warpAffine
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
    #x,y of the points were stored as different channels, which is not very intuitive, using split made it sperate
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

def rotate_image(imMat, angle, Com_x, Com_y, W, H):
    """
    Rotate an input image by a specified angle around a given center.

    Arguments:
    imMat -- The input image as a Mat.
    angle -- The rotation angle in degrees.
    Com_x -- X-coordinate of the center of rotation.
    Com_y -- Y-coordinate of the center of rotation.
    W -- Width of the output image.
    H -- Height of the output image.

    Returns:
    imMat_out -- The rotated image as a Mat.
    """
    # Define the scale factor for the rotation
    scale = 1.0
    
    # Create a Mat to store the rotation matrix
    M_rotate = Mat()
    
    # Define the center of rotation as a Point2f
    center = Point2f(float(Com_x), float(Com_y))
    
    # Calculate the rotation matrix using getRotationMatrix2D
    M_rotate = getRotationMatrix2D(center, angle, scale)
    #print(CvMat(M_rotate))
    # Create a Mat to store the rotated output image
    imMat_out = Mat()
    
    # Define the size of the output image as a Size
    szi = Size(int(W), int(H))
    
    # Apply the affine transformation to rotate the image
    warpAffine(imMat, imMat_out, M_rotate, szi)

    return imMat_out

def translate_image(imMat, Com_x, Com_y, W, H):
    """
    Translate the input image to reposition its center of mass (COM).

    Arguments:
    imMat -- Input image as a Mat.
    Com_x -- X-coordinate of the center of mass.
    Com_y -- Y-coordinate of the center of mass.
    W -- Width of the output image.
    H -- Height of the output image.

    Returns:
    imMat_out -- Translated image as a Mat.
    """
    # Calculate the correction values for centering the image
    cntr_corec_x, cntr_corec_y = (int((W/2)) - Com_x), (int((H/2)) - Com_y)
    
    # Create a translation matrix
    M_translate_mat = Mat(2, 3, 5)
    M_translate_cvmat = CvMat(M_translate_mat)
    
    # Set the translation matrix values
    cvmSet(M_translate_cvmat, 0, 0, 1)
    cvmSet(M_translate_cvmat, 0, 1, 0)
    cvmSet(M_translate_cvmat, 0, 2, cntr_corec_x)
    cvmSet(M_translate_cvmat, 1, 0, 0)
    cvmSet(M_translate_cvmat, 1, 1, 1)
    cvmSet(M_translate_cvmat, 1, 2, cntr_corec_y)
    
    # Create a translation matrix
    M_translate = Mat(M_translate_cvmat)
    
    # Apply translation to the input image
    imMat_out = Mat()
    szi = Size(int(W), int(H))
    warpAffine(imMat, imMat_out, M_translate, szi)
    
    return imMat_out

    

if __name__ in ['__main__', '__builtin__']:
    # Get the height and width of the ImagePlus
    H = imp.getHeight()
    W = imp.getWidth()
    
    # Convert ImageProcessor to Mat using custom ImageConverter
    ImProc = imp.getProcessor()
    imMat = ImProcToMat(ImProc, ImProc.getBitDepth())
    
    # Use the converted image as a binary mask
    binary_masks = imMat
    
    # Detect the largest contour in the binary mask
    largest_contour = detectContours(binary_masks)
    
    # Extract the center coordinates of the largest contour
    Com_x, Com_y = contourCenterExtractor(largest_contour)
    
    # Calculate the orientation angle of the largest contour
    angle = getOrientation(largest_contour)
    # Translate the input image using the calculated translation coordinates    
    imMat_out = translate_image(imMat,Com_x, Com_y, W, H)
    # Rotate the input image using the calculated angle and center coordinates
    imMat_out = rotate_image(imMat_out,angle,int(W/2), int(H/2), W, H)
    # Convert the rotated Mat back to ImageProcessor
    img_out = MatToImProc(imMat_out)
    # Create a new ImagePlus and display the rotated image
    imp2 = ImagePlus("imp2", img_out)
    imp2.show()