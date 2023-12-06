#@ ImagePlus (label="Select the image file") img 
#@ ImagePlus (label="Select the mask file") mask 
#@ String (choices={"Move object to image-center","Align object to desired orientation" ,"Center object and then align to orientation"}, label = "Tasks", style="listBox") task
#@ String (choices={"Horizontal", "Vertical"}, label = "Orientation",style="listBox") orientation
#@ String (choices={"Any","Left (for horizontal) / Top (for vertical)", "Right (for horizontal) / Bottom (for vertical)"}, label = "Object Polarity",style="listBox") object_polarity
#@ String (choices={"Object center", "Image center"}, label = "Center of rotation",style="radioButtonHorizontal") center_of_rotation 
#@ Boolean (label="Enlarge Image") enlarge
#@ String (choices={"Black","White", "Mean"}, label = "Fill background with ",style="listBox") background
#@ Boolean (label="Log File Output") log_window


from ij import ImagePlus,IJ,ImageStack,CompositeImage
from ij.plugin import HyperStackConverter
from ij.process import FloatProcessor
from ij.gui import ProfilePlot, Plot, WaitForUserDialog
from java.awt.event import KeyAdapter
import math

try:
    from org.bytedeco.javacpp.opencv_core import Mat, MatVector, CvMat,Scalar,split,PCACompute,Point2f,Size,cvmSet,copyMakeBorder,BORDER_CONSTANT,flip,Rect
    from org.bytedeco.javacpp.opencv_imgproc import findContours, RETR_LIST, CHAIN_APPROX_NONE, contourArea,moments,drawContours,getRotationMatrix2D,warpAffine,boundingRect,INTER_LINEAR 
    from ijopencv.ij      import ImagePlusMatConverter as imp2mat
    from ijopencv.opencv  import MatImagePlusConverter as mat2ip
    
except: 
    error = "Missing IJ-OpenCV update site.\nPlease activate it under Help > Update... > Manage Update sites"
    IJ.error("Missing IJ-OpenCV update site", error)
    raise Exception(error) # needed to stop further execution


CENTERING = "Move object to image-center"
ROTATION = "Align object to desired orientation" 
CENTERING_ROTATION = "Center object and then align to orientation"
HORIZONTAL = "Horizontal"
VERTICAL = "Vertical"
OBJECT_CENTER = "Object center"
IMAGE_CENTER = "Image center"
ANY = "Any"
LEFT_TOP = "Left (for horizontal) / Top (for vertical)"
RIGHT_BOTTOM = "Right (for horizontal) / Bottom (for vertical)"
BLACK = "Black"
WHITE = "White"
MEAN = "Mean" 



class CustomWaitDialog(WaitForUserDialog):
	"""
	Extends the WaitForUserDialog, b giving the possiblity to respond to keyboard input
	The ok label is also replaced with "Continue"
	"""
	
	def __init__(self, title, message=""):
		super(CustomWaitDialog, self).__init__(title, message)
		okButton = self.getButton()
		okButton.label = "Continue"
	
	def keyPressed(self, e):
		if e.getKeyChar() == ' ' or e.getKeyChar() == '\n':
			super(CustomWaitDialog, self).keyPressed(e) # call the mother class event handling, usually good practice
			#print("Pressed")
			# Use e to know what key was pressed
			self.close() # in your case you want to close the dialog I think, that's what you currently do with the classic WaitForUserDialog

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
    if listContour.size() == 0:
        largest_contour_out = 0
        return largest_contour_out
    
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
    if orientation == VERTICAL:
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


def get_object_polarity(mask_proc_out, orientation):
    """
    Calculate the polarity of an object in a binary mask post orientation.

    Arguments:
    maskProc -- Binary mask imageprocessor(oriented).
    orientation -- Orientation of the object ("Vertical" or "Horizontal").

    Returns:
    left_top_mean -- Sum of mean intensity of the left/top part of the object.
    right_bottom_mean -- Sum of mean intensity of the right/bottom part of the object.
    flip_value -- Flag indicating the axis of flipping  (0 for vertical, 1 for horizontal).
    """
    # Create a temporary ImagePlus from the binary mask
    temp_mask_ip = ImagePlus("temp_mask_ip", mask_proc_out)
    temp_maskMat = imp2mat.toMat(mask_proc_out)
    temp_contour = detectContours(temp_maskMat)
    contour_bounding_rectangle = boundingRect(temp_contour)
    contour_rectangle = Rect(contour_bounding_rectangle)
	

    # Set default values
    flip_value = 1
    profile_plot_orientation = 0

    # Select the entire image
    IJ.run(temp_mask_ip, "Select All", "")

    # Adjust parameters based on orientation
    if orientation == VERTICAL:
        profile_plot_orientation = 1
        flip_value = 0

    # Create a ProfilePlot for the specified orientation
    temp_mask_ip.setRoi(contour_rectangle.x(),contour_rectangle.y(),contour_rectangle.width(),contour_rectangle.height())
    temp_profile_plot = ProfilePlot(temp_mask_ip, profile_plot_orientation)
    
    # Get the intensity profile data
    temp_profile_plot_data = temp_profile_plot.getProfile()

    left_top_ls, right_bottom_ls = temp_profile_plot_data[:len(temp_profile_plot_data)//2], temp_profile_plot_data[len(temp_profile_plot_data)//2:]


    # Calculate the sum of mean intensity for left/top and right/bottom halves
    left_top_mean_sum = sum(left_top_ls)
    right_bottom_mean_sum = sum(right_bottom_ls)

    return left_top_mean_sum, right_bottom_mean_sum, flip_value


def set_object_polarity(imgMat_out, object_polarity, left_top_mean_sum, right_bottom_mean_sum, flip_value):
    """
    Set the polarity of an object in the output image based on intensity means.

    Arguments:
    imgMat_out -- Output image as a Mat.
    object_polarity -- Desired object polarity ("Left-Right/Top-Bottom" or "Right-Left/Bottom-Top").
    left_top_mean -- Mean intensity of the left/top part of the object.
    right_bottom_mean -- Mean intensity of the right/bottom part of the object.
    flip_value -- Flag indicating the axis of flipping  (0 for vertical, 1 for horizontal).

    Returns:
    imgMat_out -- Updated output image Mat with applied polarity.
    """
    # Check and apply polarity based on object_polarity
    if object_polarity == LEFT_TOP:
        if right_bottom_mean_sum > left_top_mean_sum:
            # Flip the image if the condition is met
            flip(imgMat_out, imgMat_out, flip_value)
    elif object_polarity == RIGHT_BOTTOM:
        if left_top_mean_sum > right_bottom_mean_sum:
            # Flip the image if the condition is met
            flip(imgMat_out, imgMat_out, flip_value)

    return imgMat_out


def rotate_image(imMat, angle, Com_x, Com_y, W, H,background_value):
    """
    Rotate an input image by a specified angle around a given center.

    Arguments:
    imMat -- The input image as a Mat.
    angle -- The rotation angle in degrees.
    Com_x -- X-coordinate of the center of rotation.
    Com_y -- Y-coordinate of the center of rotation.
    W -- Width of the output image.
    H -- Height of the output image.
    background_value -- Pixel value of the background created post rotation.

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

    if isinstance(background_value, tuple): # rgb case
        background_value = Scalar(*background_value)
    else :
        background_value = Scalar(float(background_value))
    
    # Apply the affine transformation to rotate the image
    warpAffine(imMat, imMat_out, M_rotate, szi,INTER_LINEAR,BORDER_CONSTANT,background_value)

    return imMat_out

def translate_image(imMat, Com_x, Com_y, W, H,background_value):
    """
    Translate the input image to reposition its center of mass (COM).

    Arguments:
    imMat -- Input image as a Mat.
    Com_x -- X-coordinate of the center of mass.
    Com_y -- Y-coordinate of the center of mass.
    W -- Width of the output image.
    H -- Height of the output image.
    background_value -- Pixel value of the background created post translation.

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
    
    if isinstance(background_value, tuple): # rgb case
        background_value = Scalar(*background_value)
    else :
        background_value = Scalar(float(background_value))

    warpAffine(imMat, imMat_out, M_translate, szi,INTER_LINEAR,BORDER_CONSTANT,background_value)
    
    return imMat_out

def enlarge_image(imMat,task,background_value):
    """
    Enlarge the input image.

    Arguments:
    imMat -- Input image as a Mat.
    task (str): The transformation task ("Rotation", "Centering+Rotation", or "No Rotation").
    background_value -- Pixel value of the background created post enalarging the canvas.

    Returns:
    imMat_en -- Enlarged square image as a Mat.
    """
    # if the task is rotation the image is enalrged such the image height and width is replcaed by the diagonal of the input image
    if task == ROTATION:
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

    if isinstance(background_value, tuple): # rgb case
        background_value = Scalar(*background_value)
    else :
        background_value = Scalar(float(background_value))
    
    # Copy the input image into the center of the enlarged square image
    copyMakeBorder(imMat, imMat_en, top, bottom, left, right, BORDER_CONSTANT, background_value)
    
    return imMat_en

def compute_transformation(maskProc, enlarge, orientation,task):
    """
    Compute image transformation parameters.

    Args:
        enlarge (boolean): Whether to enlarge the image (Boolean).
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
    if enlarge == True:
        maskMat = enlarge_image(maskMat,task,0)
    
    # Detect the largest contour in the binary mask
    largest_contour = detectContours(maskMat)
    if largest_contour == 0:
        Com_x, Com_y, angle = "No_Object_Detected","No_Object_Detected","No_Object_Detected"
        return Com_x, Com_y, angle

    
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

def transform_current_plane(img, task, center_of_rotation, enlarge, object_polarity, background, Com_x, Com_y, angle, left_top_mean_sum, right_bottom_mean_sum, flip_value):
    """
    Apply the transformation specified by task to the currently active image-plane of the ImagePlus.
    The current plane is set via imp.setPosition(c, z, t) or imp.setPositionWithoutUpdate(c, z, t) for better performance.
    The transformed image plane is returned as a new image processor.

    Args:
        img: The input image.
        task (str): The transformation task ("Rotation", "Centering+Rotation", or "No Rotation").
        center_of_rotation: The center of rotation.
        enlarge (boolean): Whether to enlarge the image (Boolean).
        Com_x (float): X-coordinate of the center of mass.
        Com_y (float): Y-coordinate of the center of mass.
        angle (float): The rotation angle.
        left_top_mean (float): Sum of mean intensity of the left/top part of the object.
        right_bottom_mean (float): Sum of mean intensity of the right/bottom part of the object.
        flip_value -- Flag indicating the axis of flipping  (0 for vertical, 1 for horizontal).
        background (str) -- Background color
        

    Returns:
        img_out: The transformed image.
    """
    imgProc = img.getProcessor()

    if background == BLACK:
        background_value = 0
    elif background == WHITE:
        if (img.getBitDepth() == 8):
            background_value = 255        
        elif (img.getBitDepth() == 24):
            background_value = (255.0,255.0,255.0,1.0)
        elif img.getBitDepth() == 16:
            background_value = 65535
        elif img.getBitDepth() == 32:
            background_value = 2**32 - 1 
    elif background == MEAN:
        imgProc_stat = imgProc.getStats()
        background_value = imgProc_stat.mean
    else : 
        background_value = 0


    # If there is no rotation angle, return a duplicate of the input image
    if task == ROTATION and angle == 0:
        return imgProc.duplicate()

    # If the task is Centering+Rotation and there is no rotation angle, switch to Centering task
    if task == CENTERING_ROTATION and angle == 0:
        task = CENTERING

    # Convert the ImageProcessor to a Mat
    imgMat = imp2mat.toMat(imgProc)

    # Enlarge the input image if specified
    if enlarge == True:
        imgMat = enlarge_image(imgMat, task,background_value)

    W, H = imgMat.cols(), imgMat.rows()

    if task == CENTERING:
        # Translate the input image using the calculated translation coordinates
        imgMat_out = translate_image(imgMat, Com_x, Com_y, W, H,background_value)

    elif task == ROTATION:
        # Set center of rotation coordinates to image center if specified
        if center_of_rotation == IMAGE_CENTER:
            Com_x = int((W / 2))
            Com_y = int((H / 2))

        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat, angle, Com_x, Com_y, W, H,background_value)

    elif task == CENTERING_ROTATION:
        # Translate the input image using the calculated translation coordinates
        imgMat_out = translate_image(imgMat, Com_x, Com_y, W, H,background_value)

        # Rotate the input image using the calculated angle and center coordinates
        imgMat_out = rotate_image(imgMat_out, angle, int(W / 2), int(H / 2), W, H,background_value)

    # Set object polarity if specified
    if (object_polarity == LEFT_TOP) or (object_polarity == RIGHT_BOTTOM):
        imgMat_out = set_object_polarity(imgMat_out, object_polarity, left_top_mean_sum, right_bottom_mean_sum, flip_value)

    # Convert the transformed image back to an ImageProcessor
    return mat2ip.toImageProcessor(imgMat_out)



def process_input_img(img, mask, task, orientation, center_of_rotation, enlarge, object_polarity,background,log_window):
    """
    Process input images based on specified transformations.

    This function takes input images and masks, applies transformations according to the specified task, orientation,
    and other parameters, and returns a list of processed images.

    Args:
        img (ImageStack): Input image stack.
        mask (ImageStack): Binary mask stack.
        task (str): Task identifier.
        orientation (str): Orientation of transformation.
        center_of_rotation (str): Center of rotation angle.
        enlarge (boolean): Whether to enlarge the images.
        object_polarity (str): Object polarity ("Left-Right/Top-Bottom" or "Right-Left/Bottom-Top").

    Returns:
        list: List of processed ImageProcessors.
    """
    # Initialize a list to store image processors
    ip_list = []
    current_status = 0

    # Check if dimensions of the input image and mask match
    if (img.getHeight() != mask.getHeight()) or (img.getWidth() != mask.getWidth()):
        IJ.error("Mask dimension and Image dimension don't match")
        raise Exception("Mask dimension and Image dimension don't match")

    # Check if the mask has 3 dimensions
    if mask.getNDimensions() == 3:
        stack_Size = mask.getStackSize()

        # Loop through the stack
        for stack_Index in range(1, (stack_Size + 1)):
            mask.setPosition(stack_Index)
            maskProc = mask.getProcessor()
            Com_x, Com_y, angle = compute_transformation(maskProc, enlarge, orientation, task)
            if (Com_x == "No_Object_Detected") and (Com_y == "No_Object_Detected") and (angle == "No_Object_Detected"):
                if log_window == True:
                    IJ.log("Image stack framenumber : " + str(stack_Index))
                    IJ.log("Detected object center (X coordinate) : " + str(Com_x))
                    IJ.log("Detected object center (Y coordinate) : " + str(Com_y))
                    IJ.log("Detected object orientation angle : " + str(angle))
                    IJ.log(" ")
                return ip_list
                
            
            # Calculate object polarity if required
            if (object_polarity == LEFT_TOP) or (object_polarity == RIGHT_BOTTOM):
                left_top_mean_sum, right_bottom_mean_sum, flip_value = 0, 0, 0
                mask_proc_out = transform_current_plane(mask, task, center_of_rotation, enlarge, object_polarity,0,Com_x, Com_y, angle, left_top_mean_sum, right_bottom_mean_sum, flip_value)
                left_top_mean_sum, right_bottom_mean_sum, flip_value = get_object_polarity(mask_proc_out, orientation)
            else:
                left_top_mean_sum, right_bottom_mean_sum, flip_value = 0, 0, 0

            # Check if the input image has multiple frames
            if img.getNFrames() > 1:
                for z_slice in range(1, (img.getNSlices() + 1)):
                    for channel_index in range(1, (img.getNChannels() + 1)):
                        current_status = current_status + 1
                        IJ.showProgress(current_status, (img.getNFrames() * img.getNChannels() * img.getNSlices()))
                        # Set the position of the input image
                        img.setPositionWithoutUpdate(channel_index, z_slice, stack_Index)
                        img_out = transform_current_plane(img, task, center_of_rotation, enlarge, object_polarity,background, Com_x, Com_y, angle, left_top_mean_sum, right_bottom_mean_sum, flip_value)
                        # Append the transformed image to the list
                        ip_list.append(img_out)
                if log_window == True:
                    IJ.log("Image stack framenumber : " + str(stack_Index))
                    IJ.log("Detected object center (X coordinate) : " + str(Com_x))
                    IJ.log("Detected object center (Y coordinate) : " + str(Com_y))
                    IJ.log("Detected object orientation angle : " + str(angle))
                    IJ.log(" ")

            # If the input image has only one frame and multiple slices
            elif img.getNFrames() == 1 and img.getNSlices() > 1:
                for channel_index in range(1, (img.getNChannels() + 1)):
                    current_status = current_status + 1
                    IJ.showProgress(current_status, (img.getNFrames() * img.getNChannels() * img.getNSlices()))
                    img.setPositionWithoutUpdate(channel_index, stack_Index, img.getNFrames())
                    img_out = transform_current_plane(img, task, center_of_rotation, enlarge, object_polarity, background,Com_x, Com_y, angle, left_top_mean_sum, right_bottom_mean_sum, flip_value)
                    # Append the transformed image to the list
                    ip_list.append(img_out)
                if log_window == True:
                    IJ.log("Image stack slicenumber(Z) : " + str(stack_Index))
                    IJ.log("Detected object center (X coordinate) : " + str(Com_x))
                    IJ.log("Detected object center (Y coordinate) : " + str(Com_y))
                    IJ.log("Detected object orientation angle : " + str(angle))
                    IJ.log(" ")
    # If the mask is a single image plane
    elif mask.getNDimensions() == 2:
        maskProc = mask.getProcessor()
        Com_x, Com_y, angle = compute_transformation(maskProc, enlarge, orientation, task)
        

        if (Com_x == "No_Object_Detected") and (Com_y == "No_Object_Detected") and (angle == "No_Object_Detected"):
            if log_window == True:
                IJ.log("Detected object center (X coordinate) : " + str(Com_x))
                IJ.log("Detected object center (Y coordinate) : " + str(Com_y))
                IJ.log("Detected object orientation angle : " + str(angle))
                IJ.log(" ")
            return ip_list

        # Calculate object polarity if required
        if (object_polarity == LEFT_TOP) or (object_polarity == RIGHT_BOTTOM):
            left_top_mean_sum, right_bottom_mean_sum, flip_value = 0, 0, 0
            mask_proc_out = transform_current_plane(mask, task, center_of_rotation, enlarge, object_polarity, 0, Com_x, Com_y, angle, left_top_mean_sum, right_bottom_mean_sum, flip_value)
            left_top_mean_sum, right_bottom_mean_sum, flip_value = get_object_polarity(mask_proc_out, orientation)
        else:
            left_top_mean_sum, right_bottom_mean_sum, flip_value = 0, 0, 0

        # Loop through the input image frames, slices, and channels
        for frame_index in range(1, (img.getNFrames() + 1)):
            for z_slice in range(1, (img.getNSlices() + 1)):
                for channel_index in range(1, (img.getNChannels() + 1)):
                    current_status = current_status + 1
                    IJ.showProgress(current_status, (img.getNFrames() * img.getNChannels() * img.getNSlices()))
                    img.setPositionWithoutUpdate(channel_index, z_slice, frame_index)
                    img_out = transform_current_plane(img, task, center_of_rotation, enlarge, object_polarity, background, Com_x, Com_y, angle, left_top_mean_sum, right_bottom_mean_sum, flip_value)
                    # Append the transformed image to the list
                    ip_list.append(img_out)

        if log_window == True:
            IJ.log("Detected object center (X coordinate) : " + str(Com_x))
            IJ.log("Detected object center (Y coordinate) : " + str(Com_y))
            IJ.log("Detected object orientation angle : " + str(angle))
            IJ.log(" ")

    return ip_list




def output_image_maker(img, ip_list):
    """
    Create an ImagePlus from the list of transformed ImageProcessor (ip_list).
    The ImagePlus has the same dimensions than the input ImagePlus (especially for hyperstacks same number of channels, timepoint... between input and output image)
    """
    
    if len(ip_list) == 0:
        return img
    
    elif len(ip_list) == 1:
        
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
    if log_window == True:
        IJ.log("Filename : " + str(img.getTitle()))
    ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity,background,log_window)
    imp_out = output_image_maker(img, ip_list)
    imp_out.show()

    
    