#@ File (label="Select the input file 2D") input_File
#@ File (label="Select the mask file to the input file") Mask_File
#@ String (choices={"Centering", "Rotation","Rotation+Centering"}, label = "Tasks", style="listBox") task
#@ String (choices={"Horizontal", "Vertical"}, label = "Orientation",style="listBox") orientation
#@ String (choices={"Object_center", "Image_center"}, label = "Center of rotation",style="radioButtonHorizontal") Center_of_rotation 
#@ String (choices={"Yes", "No"}, label = "Enlarge Image",style="radioButtonHorizontal") enlarge
from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar,split,PCACompute,Point2f,Size,cvmSet,copyMakeBorder,BORDER_CONSTANT
from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours,getRotationMatrix2D,warpAffine
from ImageConverter import ImProcToMat,MatToImProc
from ij import ImagePlus,IJ
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
    if abs(angle) >= 180:
        angle_final = angle - 180
        if  angle < 0:
            return  angle_final*(-1)
        else:
            return angle_final     
    
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

def enlarge_image(imMat):
    """
    Enlarge the input image to a square shape.

    Arguments:
    imMat -- Input image as a Mat.

    Returns:
    imMat_en -- Enlarged square image as a Mat.
    """
    # Calculate the dimensions for the enlarged square image
    enlarged_dims = int((imMat.rows() * imMat.rows() + imMat.cols() * imMat.cols()) ** 0.5)
    
    # Create a new square Mat for the enlarged image
    imMat_en = Mat(enlarged_dims, enlarged_dims, imMat.type())
    
    # Calculate the border widths for top, bottom, left, and right
    if (enlarged_dims - imMat.rows()) % 2 == 0:
        top = bottom = (enlarged_dims - imMat.rows()) // 2
    else:
        top = (enlarged_dims - imMat.rows()) // 2
        bottom = (enlarged_dims - imMat.rows()) - top 
    
    if (enlarged_dims - imMat.cols()) % 2 == 0:
        left = right = (enlarged_dims - imMat.cols()) // 2
    else:
        left = (enlarged_dims - imMat.cols()) // 2
        right = (enlarged_dims - imMat.cols()) - top   
    
    
    # Copy the input image into the center of the enlarged square image
    copyMakeBorder(imMat, imMat_en, top, bottom, left, right, BORDER_CONSTANT, Scalar(0))
    
    return imMat_en,enlarged_dims

def process_image(imgMat,maskMat,W,H):
    if enlarge == "Yes":
        imgMat,H = enlarge_image(imgMat)
        maskMat,W = enlarge_image(maskMat)
    # Detect the largest contour in the binary mask
    largest_contour = detectContours(maskMat)
    # Extract the center coordinates of the largest contour
    Com_x, Com_y = contourCenterExtractor(largest_contour)    
    # Calculate the orientation angle of the largest contour
    angle = getOrientation(largest_contour)
    if orientation == "Vertical":
        angle = angle+90
    if task == "Centering":
        # Translate the input image using the calculated translation coordinates    
        imgMat_out = translate_image(imgMat,Com_x, Com_y, W, H)
    elif task == "Rotation":
        if Center_of_rotation == "Image_center":
            Com_x = int((W/2))
            Com_y = int((H/2))
        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat, angle, Com_x, Com_y, W, H)        
    elif task == "Rotation+Centering":   
        # Translate the input image using the calculated translation coordinates    
        imgMat_out = translate_image(imgMat,Com_x, Com_y, W, H) 
        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat_out, angle, int(W/2), int(H/2), W, H)
    
    return imgMat_out

if __name__ in ['__main__', '__builtin__']:
    img = IJ.openImage(str(input_File))
    mask = IJ.openImage(str(Mask_File))
    img.show()        
    # Get the height and width of the ImagePlus
    H = img.getHeight()
    W = img.getWidth()    
    # Convert ImageProcessor to Mat using custom ImageConverter
    imgProc = img.getProcessor()
    maskProc = mask.getProcessor()
    imgMat = ImProcToMat(imgProc, imgProc.getBitDepth())
    maskMat = ImProcToMat(maskProc, maskProc.getBitDepth())


    imgMat_out = process_image(imgMat,maskMat,W,H)
    img_out = MatToImProc(imgMat_out)
    # Create a new ImagePlus and display the rotated image
    imp2 = ImagePlus("imp2", img_out)
    imp2.show()

 