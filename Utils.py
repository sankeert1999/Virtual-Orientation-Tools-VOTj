#@ File (label="Select the input file 2D") input_File
#@ File (label="Select the mask file to the input file") Mask_File
#@ String (choices={"Centering", "Rotation","Rotation+Centering"}, label = "Tasks", style="listBox") task
#@ String (choices={"Horizontal", "Vertical"}, label = "Orientation",style="listBox") orientation
#@ String (choices={"Object_center", "Image_center"}, label = "Center of rotation",style="radioButtonHorizontal") center_of_rotation 
#@ String (choices={"Yes", "No"}, label = "Enlarge Image",style="radioButtonHorizontal") enlarge
from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar,split,PCACompute,Point2f,Size,cvmSet,copyMakeBorder,BORDER_CONSTANT
from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours,getRotationMatrix2D,warpAffine
from ijopencv.ij      import ImagePlusMatConverter as imp2mat
from ijopencv.opencv  import MatImagePlusConverter as mat2ip
from ij import ImagePlus,IJ,ImageStack
from ij.plugin import HyperStackConverter
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
   
def small_angle_calculation(angle):
    """
    Calculate the equivalent small angle within the range (-90, 90).
    For eg : 120 -> -60
    Avoiding large rotation angle to align the object of interest.
    By convention the positive angles mean a anti-clockwise rotation and 
    negative mean a clockwise roation.

    Args:
        angle (float): The input angle in degrees.

    Returns:
        float: The equivalent small angle within the range (-90, 90).
    """
    if 90 > abs(angle) >= 0:
        return angle
    elif 180 > abs(angle) >= 90:
        angle_final = 180 - abs(angle)
        if angle > 0:
            angle_final = -angle_final                        
    elif 270 > abs(angle) >= 180:
        angle_final = abs(angle) - 180
        if angle < 0:
            angle_final = -angle_final
    elif 360 >= abs(angle) >= 270:
        angle_final = 360 - abs(angle)
        if angle > 0:
            angle_final = -angle_final            
    return angle_final


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
    angle_orientation = math.atan2(eigenvectors_cvmat.get(0, 1), eigenvectors_cvmat.get(0, 0))  #calculating the orientation
    angle_orientation = int(math.degrees(angle_orientation))    #converting to degrees from radians
    angle_rotation = small_angle_calculation(angle_orientation) #calculating the smallest angle of rotation to oreint the object from the obtained orienation angle of the object 
    return angle_rotation

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
        bottom = enlarged_dims - (imMat.rows() + top) 
    
    if (enlarged_dims - imMat.cols()) % 2 == 0:
        left = right = (enlarged_dims - imMat.cols()) // 2
    else:
        left = (enlarged_dims - imMat.cols()) // 2
        right = enlarged_dims - (imMat.cols() + left)   
    
    
    # Copy the input image into the center of the enlarged square image
    copyMakeBorder(imMat, imMat_en, top, bottom, left, right, BORDER_CONSTANT, Scalar(0))
    
    return imMat_en

def compute_transformation(maskProc, enlarge, orientation):
    """
    Compute image transformation parameters.

    Args:
        enlarge (str): Whether to enlarge the image ("Yes" or "No").
        orientation (str): Orientation of the object ("Horizontal" or "Vertical").
        imgMat (Mat): Input image plane as a Mat.
        maskMat (Mat): Binary mask image plane as a Mat.

    Returns:
        tuple: A tuple containing:
            Com_x (float): X-coordinate of the center of mass.
            Com_y (float): Y-coordinate of the center of mass.
            angle (float): Orientation angle of the largest contour.
            imgMat (Mat): Transformed image.
    """
    # Convert image and mask processors to matrices
    maskMat = imp2mat.toMat(maskProc)
    
    # Check if image enlargement is requested
    if enlarge == "Yes":
        maskMat = enlarge_image(maskMat)
    
    # Detect the largest contour in the binary mask
    largest_contour = detectContours(maskMat)
    
    # Extract the center coordinates of the largest contour
    Com_x, Com_y = contourCenterExtractor(largest_contour)
    
    # Calculate the orientation angle of the largest contour
    angle = getOrientation(largest_contour)
    
    # Adjust the angle if the orientation is specified as "Vertical"
    if orientation == "Vertical":
        angle = angle + 90
    
    # Return the center coordinates, angle, and the transformed image
    return Com_x, Com_y, angle


def apply_transformation(imgProc,task, center_of_rotation, enlarge, Com_x, Com_y, angle):
    """
    Apply a transformation to the input image plane based on the specified task.

    Args:
        task (str): The transformation task to perform. Options: "Centering", "Rotation", "Rotation+Centering".
        center_of_rotation (str): The center of rotation. Options: "Image_center","Object_center".
        Com_x (float): X-coordinate of the center of mass.
        Com_y (float): Y-coordinate of the center of mass.
        angle (float): The rotation angle (in degrees).
        imgMat (Mat): Input image as a Mat.

    Returns:
        imgMat_out: Transformed image as a Mat.
    """
    imgMat = imp2mat.toMat(imgProc)
    
    if enlarge == "Yes":
        imgMat = enlarge_image(imgMat)
    
    W, H = imgMat.cols(), imgMat.rows()

    if task == "Centering":
        # Translate the input image using the calculated translation coordinates
        imgMat_out = translate_image(imgMat, Com_x, Com_y, W, H)
    elif task == "Rotation":
        if center_of_rotation == "Image_center":
            Com_x = int((W/2))
            Com_y = int((H/2))
        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat, angle, Com_x, Com_y, W, H)
    elif task == "Rotation+Centering":
        # Translate the input image using the calculated translation coordinates
        imgMat_out = translate_image(imgMat, Com_x, Com_y, W, H)
        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat_out, angle, int(W/2), int(H/2), W, H)
    # Convert the transformed image back to ImageProcessor
    img_out = mat2ip.toImageProcessor(imgMat_out)

    return img_out

def input_image_metadata_extractor(img):
    """
    Extract metadata from an input image.

    Args:
        img: Input image.

    Returns:
        img_Title (str): Title of the image.
        img_Bit_Depth (int): Bit depth of the image.
        height (int): Height of the image.
        width (int): Width of the image.
        dimension (int): Number of dimensions of the image.
        channels (int): Number of channels in the image.
        slices (int): Number of slices in the image.
        frames (int): Number of frames in the image.
    """
    img_Title = img.getTitle()
    img_Bit_Depth = img.getBitDepth()
    height = img.getHeight()
    width = img.getWidth()
    dimension = img.getNDimensions()
    channels = img.getNChannels()
    slices = img.getNSlices()
    frames = img.getNFrames()
    
    return img_Title, img_Bit_Depth, height, width, dimension, channels, slices, frames




def process_input_img(img, mask, task, orientation, center_of_rotation, enlarge):
    """
    Process input images based on specified transformations.

    Args:
        task (str): Task identifier.
        orientation (str): Orientation of transformation.
        center_of_rotation (float): Center of rotation angle.
        enlarge (str): Whether to enlarge the images.
        img (ImageStack): Input image stack.
        mask (ImageStack): Binary mask stack.

    Returns:
        list: List of processed ImageProcessors.
    """
    # Initialize a list to store image processors
    ip_list = []

    if mask.getNDimensions() == 3:
        stack_Size = mask.getStackSize()
        for stack_Index in range(1, (stack_Size + 1)):
            mask.setPosition(stack_Index)
            maskProc = mask.getProcessor()
            Com_x, Com_y, angle = compute_transformation(maskProc, enlarge, orientation)

            if img.getNFrames() > 1:
                for z_slice in range(1, (img.getNSlices() + 1)):
                    for channel_index in range(1, (img.getNChannels() + 1)):
                        img.setPosition(channel_index, z_slice, stack_Index)
                        imgProc = img.getProcessor()
                        # Apply transformation to the image
                        img_out = apply_transformation(imgProc,task, center_of_rotation, enlarge, Com_x, Com_y, angle)
                        # Append the transformed image to the list
                        ip_list.append(img_out)
            elif img.getNFrames() == 1 and img.getNSlices() > 1:
                for channel_index in range(1, (img.getNChannels() + 1)):
                    img.setPosition(channel_index, stack_Index, 1)
                    imgProc = img.getProcessor()
                    # Apply transformation to the image
                    img_out = apply_transformation(imgProc,task, center_of_rotation, enlarge, Com_x, Com_y, angle)
                    # Append the transformed image to the list
                    ip_list.append(img_out)

    elif mask.getNDimensions() == 2:
        maskProc = mask.getProcessor()
        Com_x, Com_y, angle = compute_transformation(maskProc, enlarge, orientation)

        for frame_index in range(1, (img.getNFrames() + 1)):
            for z_slice in range(1, (img.getNSlices() + 1)):
                for channel_index in range(1, (img.getNChannels() + 1)):
                    img.setPosition(channel_index, z_slice, frame_index)
                    imgProc = img.getProcessor()
                    # Apply transformation to the image
                    img_out = apply_transformation(imgProc,task, center_of_rotation, enlarge, Com_x, Com_y, angle)
                    # Append the transformed image to the list
                    ip_list.append(img_out)
    return ip_list

  


def output_image_maker(ip_list, channels, slices, frames, img_Title):
    """
    Create and return an ImagePlus object based on the given dimension, image title, and list of image processors.

    Args:
        img_Title (str): The title for the output image.
        ip_list (list): List of ImageProcessor objects for the output image.

    Returns:
        ImagePlus: The created ImagePlus object.
    """
    if len(ip_list) == 1:
        # Create a new ImagePlus for a 2D image and display it
        imp_out = ImagePlus(img_Title, ip_list[0])

    else:
        # Create an output image stack
        stack_out = ImageStack()
        # Add transformed slices to the output stack
        for ip in ip_list:
            stack_out.addSlice(ip)
        # Create an ImagePlus from the output stack
        imp_out = ImagePlus(img_Title, stack_out)
        if channels > 1:
            imp_out = HyperStackConverter.toHyperStack(imp_out, channels, slices, frames)

    return imp_out





if __name__ in ['__main__', '__builtin__']:
    img = IJ.openImage(str(input_File))
    mask = IJ.openImage(str(Mask_File))
    img.show()
    img_Title, img_Bit_Depth,height,width,dimension,channels,slices,frames = input_image_metadata_extractor(img)
    ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge)
    imp_out = output_image_maker(ip_list, channels, slices, frames, img_Title)
    imp_out.show()
    
    

 