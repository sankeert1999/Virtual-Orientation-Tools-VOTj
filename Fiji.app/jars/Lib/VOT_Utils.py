#@ File (label="Select the input file") input_File
#@ File (label="Select the mask file to the input file") Mask_File
#@ String (choices={"Centering", "Rotation","Centering+Rotation"}, label = "Tasks", style="listBox") task
#@ String (choices={"Horizontal", "Vertical"}, label = "Orientation",style="listBox") orientation
#@ String (choices={"Object_center", "Image_center"}, label = "Center of rotation",style="radioButtonHorizontal") center_of_rotation 
#@ String (choices={"Yes", "No"}, label = "Enlarge Image",style="radioButtonHorizontal") enlarge
from opcode import hasjabs
from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar,split,PCACompute,Point2f,Size,cvmSet,copyMakeBorder,BORDER_CONSTANT
from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours,getRotationMatrix2D,warpAffine
from ijopencv.ij      import ImagePlusMatConverter as imp2mat
from ijopencv.opencv  import MatImagePlusConverter as mat2ip
from ij import ImagePlus,IJ,ImageStack,CompositeImage
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

def detectContours(binary_mask):
    """
    Detect contours in the given binary mask and return the largest contour.

    Arguments:
    binary_mask, Mat -- Binary mask image containing object regions.

    Returns:
    largest_contour_out -- The largest contour detected in the binary masks as a Mat.
    """
    
    # Create a MatVector to store detected contours
    listContour = MatVector()
    findContours(binary_mask, listContour, RETR_LIST, CHAIN_APPROX_NONE)
    
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
   
def getCorrectingAngle(angle,orientation):
    """
    The input angle is the orientation of teh object of interest which can span from (-360,360)
    with this function equivalent small angle within the range (-90, 90) is calculated.
    
    For example: 120 -> -60 (horizontal) 30 (vertical)
    Avoiding large rotation angle to align the object of interest.
    By convention, positive angles mean an anti-clockwise rotation, and 
    negative mean a clockwise rotation.

    Args:
        angle (float): The input angle in degrees.
        orientation (str): The orientation of the angle ("Vertical" or "Horizontal").

    Returns:
        float: The equivalent small angle within the range (-90, 90).
    """
    if orientation == "Vertical":
        if 90 > abs(angle) >= 0:
            angle_final = 90 - abs(angle)
            if angle > 0:
                angle_final = -angle_final  
        elif 180 > abs(angle) >= 90:
            angle_final = abs(angle) - 90
            if angle < 0:
                angle_final = -angle_final                        
        elif 270 > abs(angle) >= 180:
            angle_final = 270 - abs(angle)
            if angle > 0:
                angle_final = -angle_final
        elif 360 >= abs(angle) >= 270:
            angle_final = abs(angle) - 270
            if angle < 0:
                angle_final = -angle_final            
        return angle_final
    
    else:
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
    return angle_orientation

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

def enlarge_image(imMat,task):
    """
    Enlarge the input image to a square shape.

    Arguments:
    imMat -- Input image as a Mat.

    Returns:
    imMat_en -- Enlarged square image as a Mat.
    """
    # if the task is rotation the image is enalrged such the image height and width is replcaed by the diagonal of the input image
    if task == "Rotation":
        # Calculate the dimensions for the enlarged  image
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
    # For other task image is enalrged such that the height and width of the input image is doubled
    else:
        if imMat.rows() == imMat.cols():
            top = bottom = left = right =int(imMat.rows()/2)
            # Calculate the dimensions for the enlarged  image
            enlarged_dims = 2*imMat.rows()
            imMat_en = Mat(enlarged_dims, enlarged_dims, imMat.type())
        else:
            top=bottom = int(imMat.rows()/2)
            left=right = int(imMat.cols()/2)                  
            # Calculate the dimensions for the enlarged  image
            enlarged_dims_x = 2*imMat.cols()
            enlarged_dims_y = 2*imMat.rows()
            imMat_en = Mat(enlarged_dims_y, enlarged_dims_x, imMat.type())    
    # Copy the input image into the center of the enlarged square image
    copyMakeBorder(imMat, imMat_en, top, bottom, left, right, BORDER_CONSTANT, Scalar(0))
    
    return imMat_en

def compute_transformation(maskProc, enlarge, orientation,task):
    """
    Compute image transformation parameters.

    Args:
        enlarge (str): Whether to enlarge the image ("Yes" or "No").
        orientation (str): Orientation of the object ("Horizontal" or "Vertical").

    Returns:
        tuple: A tuple containing:
            Com_x (float): X-coordinate of the center of mass.
            Com_y (float): Y-coordinate of the center of mass.
            angle (float): Orientation angle of the largest contour.
    """
    
    if maskProc.getBitDepth() != 8:
        maskProc = maskProc.convertToByteProcessor() # findContours from opencv works with 8-bit only, conversion will scale from min/max to 0-255
    
    # Convert mask processor to matrices
    maskMat = imp2mat.toMat(maskProc)
    
    # Check if image enlargement is requested
    if enlarge == "Yes":
        maskMat = enlarge_image(maskMat,task)
    
    # Detect the largest contour in the binary mask
    largest_contour = detectContours(maskMat)
    
    # Extract the center coordinates of the largest contour
    Com_x, Com_y = contourCenterExtractor(largest_contour)
    
    # Calculate the orientation angle of the largest contour
    angle = getOrientation(largest_contour)

    angle = getCorrectingAngle(angle, orientation) #calculating the smallest angle of rotation to oreint the object from the obtained orienation angle of the object 
    
    # Adjust the angle if the orientation is specified as "Vertical"
    #if orientation == "Vertical":
    #    angle = angle + 90
    
    # Return the center coordinates, angle, and the transformed image
    return Com_x, Com_y, angle

def transform_current_plane(img, task, center_of_rotation, enlarge, Com_x, Com_y, angle):
    """
    Apply the transformation specified by task to the currently active image-plane of the ImagePlus.
    The current plane is set via imp.setPosition(c,z,t) or imp.setPositionWithoutUpdate(c,z,t) for better performance.
    The transformed image plane is returned as a new image processor

    Args:
        img: The input image.
        task (str): The transformation task ("Rotation", "Centering+Rotation", or "No Rotation").
        center_of_rotation: The center of rotation coordinates.
        enlarge (str): Whether to enlarge the image ("Yes" or "No").
        Com_x (float): X-coordinate of the center of mass.
        Com_y (float): Y-coordinate of the center of mass.
        angle (float): The rotation angle.

    Returns:
        img_out: The transformed image.
    """
    imgProc = img.getProcessor()

    if task == "Rotation" and angle == 0 :
        return imgProc.duplicate() # nothing to do, returns a copy of the input image plane then
    
    if task == "Centering+Rotation" and angle == 0 :
        task = "Centering"
    
    # Convert the ImageProcessor to a Mat
    imgMat = imp2mat.toMat(imgProc)
    
    if enlarge == "Yes":
        # Enlarge the input image
        imgMat = enlarge_image(imgMat,task)
    
    W, H = imgMat.cols(), imgMat.rows()

    if task == "Centering": # Translate the input image using the calculated translation coordinates
        imgMat_out = translate_image(imgMat, Com_x, Com_y, W, H)
    
    elif task == "Rotation":
        
        if center_of_rotation == "Image_center":
            Com_x = int((W/2))
            Com_y = int((H/2))
        
        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat, angle, Com_x, Com_y, W, H)
    
    elif task == "Centering+Rotation":
        
        # Translate the input image using the calculated translation coordinates
        imgMat_out = translate_image(imgMat, Com_x, Com_y, W, H)
        
        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat_out, angle, int(W/2), int(H/2), W, H)
    
    # Convert the transformed image back to an ImageProcessor
    return mat2ip.toImageProcessor(imgMat_out)


def process_input_img(img, mask, task, orientation, center_of_rotation, enlarge):
    """
    Process input images based on specified transformations.

    This function takes input images and masks, applies transformations according to the specified task, orientation,
    and other parameters, and returns a list of processed images.

    Args:
        img (ImageStack): Input image stack.
        mask (ImageStack): Binary mask stack.
        task (str): Task identifier.
        orientation (str): Orientation of transformation.
        center_of_rotation (float): Center of rotation angle.
        enlarge (str): Whether to enlarge the images.

    Returns:
        list: List of processed ImageProcessors.
    """
    # Initialize a list to store image processors
    ip_list = []
    current_status = 0

    if (img.getHeight() != mask.getHeight()) or (img.getWidth() != mask.getWidth()):
        IJ.error("Mask dimension and Image dimension doesn't match")
        raise Exception("Mask dimension and Image dimension doesn't match")


    if img.getNChannels() > 1 and img.getNFrames()==1 and img.getNSlices()==1 and mask.getNDimensions() == 3:
        IJ.error("Expected 2D mask but got 3D mask")
        raise Exception("Expected 2D mask but got 3D mask")
    
    # Check if the mask has 3 dimensions
    if mask.getNDimensions() == 3:
        stack_Size = mask.getStackSize()

        # Loop through the stack
        for stack_Index in range(1, (stack_Size + 1)):
            mask.setPosition(stack_Index)
            maskProc = mask.getProcessor()
            Com_x, Com_y, angle = compute_transformation(maskProc, enlarge, orientation,task)

            # Check if the input image has multiple frames
            if img.getNFrames() > 1:
                for z_slice in range(1, (img.getNSlices() + 1)):
                    for channel_index in range(1, (img.getNChannels() + 1)):
                        current_status = current_status + 1
                        IJ.showProgress(current_status,(img.getNFrames()*img.getNChannels()*img.getNSlices()))
                        # Set the position of the input image
                        img.setPositionWithoutUpdate(channel_index, z_slice, stack_Index)
                        img_out = transform_current_plane(img, task, center_of_rotation, enlarge, Com_x, Com_y, angle)
                        # Append the transformed image to the list
                        ip_list.append(img_out)

            # If the input image has only one frame and multiple slices
            elif img.getNFrames() == 1 and img.getNSlices() > 1:
                for channel_index in range(1, (img.getNChannels() + 1)):
                    current_status = current_status + 1
                    IJ.showProgress(current_status,(img.getNFrames()*img.getNChannels()*img.getNSlices()))
                    img.setPositionWithoutUpdate(channel_index, stack_Index, img.getNFrames())
                    img_out = transform_current_plane(img, task, center_of_rotation, enlarge, Com_x, Com_y, angle)
                    # Append the transformed image to the list
                    ip_list.append(img_out)

    # If the mask is a single image plane
    elif mask.getNDimensions() == 2:
        maskProc = mask.getProcessor()
        Com_x, Com_y, angle = compute_transformation(maskProc, enlarge, orientation,task)

        # Loop through the input image frames, slices, and channels
        for frame_index in range(1, (img.getNFrames() + 1)):
            for z_slice in range(1, (img.getNSlices() + 1)):
                for channel_index in range(1, (img.getNChannels() + 1)):
                    current_status = current_status + 1
                    IJ.showProgress(current_status,(img.getNFrames()*img.getNChannels()*img.getNSlices()))
                    img.setPositionWithoutUpdate(channel_index, z_slice, frame_index)
                    img_out = transform_current_plane(img, task, center_of_rotation, enlarge, Com_x, Com_y, angle)
                    # Append the transformed image to the list
                    ip_list.append(img_out)
                    

    return ip_list


def output_image_maker(img, ip_list):
    """
    Create an ImagePlus from the list of transformed ImageProcessor (ip_list).
    The ImagePlus has the same dimensions than the input ImagePlus (especially for hyperstacks same number of channels, timepoint... between input and output image)
    """
    
    if len(ip_list) == 1:
        
        # Create a new ImagePlus for a 2D image and display it
        img_title = img.getTitle()
        # Find the position of the dot (.) which separates the name from the extension
        # Extract the name portion of the string        
        imp_out = ImagePlus(img_title[:img_title.rfind(".")]+"_aligned", ip_list[0])
        
        if imp_out.getBitDepth() == 24 : # RGB, only propagate display range (although not really working)
            imp_out.setDisplayRange(img.getDisplayRangeMin(), img.getDisplayRangeMax())
        else:
            imp_out.setLut(img.getLuts()[0])
        
        imp_out.copyScale(img)  #copying the scale metadata from the input image and transferring it to th output image.
        
        return imp_out
    
    else:
        # Create an output image stack
        stack_out = ImageStack()
        
        # Add transformed slices to the output stack
        for ip in ip_list:
            stack_out.addSlice(ip)
        
        # Create an ImagePlus from the output stack
        img_title = img.getTitle()
        # Find the position of the dot (.) which separates the name from the extension
        # Extract the name portion of the string        
        imp_out = ImagePlus(img_title[:img_title.rfind(".")]+"_aligned", stack_out)
        
        if imp_out.getBitDepth() != 24 : # conversion to hyperstack raises null pointer exception with RGB images
             imp_out = HyperStackConverter.toHyperStack(imp_out, img.getNChannels(), img.getNSlices(), img.getNFrames())
        
        # Propagate lut, display range and display mode from input image to output image
        if imp_out.isComposite(): # multi-channels i.e composite images
             imp_out.copyLuts(img)          # this function is only available to CompositeImagePlus not all ImagePlus
             imp_out.setMode(img.getMode()) # composite (i.e merging channel colors) or color (i.e separate color channels)
        
        elif imp_out.getBitDepth() != 24 : # non-composite (i.e single channel) and non-RGB
             imp_out.setLut(img.getLuts()[0]) # propagate LUT and display range - this throws an error for RGB
        
        else : # RGB - only set display range (although not really working)
            imp_out.setDisplayRange(img.getDisplayRangeMin(), img.getDisplayRangeMax()) # not really working for RGB but does not throw an error

        imp_out.copyScale(img)  #copying the scale metadata from the input image and transferring it to th output image.

        return imp_out


if __name__ in ['__main__', '__builtin__']:
    img = IJ.openImage(str(input_File))
    mask = IJ.openImage(str(Mask_File))
    img.show()
    ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge)
    imp_out = output_image_maker(img, ip_list)
    imp_out.show()
    