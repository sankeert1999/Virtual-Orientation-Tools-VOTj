#@PrefService prefs 

from ij import IJ
from ij.macro import MacroConstants
from ij.plugin import ImageCalculator,Duplicator, ImageInfo
from ij.gui import WaitForUserDialog, GenericDialog
from fiji.util.gui import GenericDialogPlus

# Open your image (replace 'your_image_path' with the actual image path)

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
        img_type (str): Type of Image 2D/3D/4D/5D
    """
    # Extract the title of the image
    img_Title = img.getTitle()

    # Get the bit depth of the image
    img_Bit_Depth = img.getBitDepth()

    # Retrieve the height and width of the image
    height = img.getHeight()
    width = img.getWidth()

    # Determine the number of dimensions, channels, slices, and frames
    dimension = img.getNDimensions()
    channels = img.getNChannels()
    slices = img.getNSlices()
    frames = img.getNFrames()

    # Determine the type of image based on its dimensions
    if channels == 1 and slices == 1 and frames == 1:
        img_type = "2D"
    elif (channels > 1 and slices == 1 and frames == 1) or (channels == 1 and slices > 1 and frames == 1) or (channels == 1 and slices == 1 and frames > 1):
        img_type = "3D"
    elif (channels > 1 and slices > 1 and frames == 1) or (channels > 1 and slices == 1 and frames > 1) or (channels == 1 and slices > 1 and frames > 1):
        img_type = "4D"
    elif channels > 1 and slices > 1 and frames > 1:
        img_type = "5D"

    return img_Title, img_Bit_Depth, height, width, dimension, channels, slices, frames, img_type


def threshold_single_slice_annotation(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end):
    """
    Perform threshold-based image segmentation of the user annotation on a single slice of the image stack.

    Args:
        img: Image stack to be thresholded.
        channel_start: Starting channel index.
        channel_end: Ending channel index.
        slice_start: Starting slice index.
        slice_end: Ending slice index.
        frame_start: Starting frame index.
        frame_end: Ending frame index.

    Returns:
        mask: Segmented image consisting the user annotations.
    """
    # Duplicate the specified slice from the image stack
    mask = Duplicator().run(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end)

    # Display the duplicated slice
    mask.show()

    # Apply a Look-Up Table (LUT) to enhance the visualization
    IJ.run(mask, "Apply LUT", "")

    IJ.setTool("Paintbrush Tool")
    IJ.setForegroundColor(255,255,255)

        # Create a dialog instructing the user to annotate the image
    wait_dialog = WaitForUserDialog("Title Message", "Mark the object of interest on the image.(To increase brush width double left click on the paintbrush icon from the Toolbar)")
    button_info=wait_dialog.getButton()
    button_info.label="Continue"
    wait_dialog.show()
    # Calculate and set a raw threshold based on the image histogram
    histogram = mask.getStatistics()
    IJ.setRawThreshold(mask, histogram.histMax - 1, histogram.histMax)

    # Convert the thresholded image to a binary mask
    IJ.run(mask, "Convert to Mask", "")

    return mask


def threshold_multi_slice_annotation(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end):
    """
    Perform threshold-based image segmentation of the user annotation on a stack of image slices.

    Args:
        img: Image stack to be thresholded.
        channel_start: Starting channel index.
        channel_end: Ending channel index.
        slice_start: Starting slice index.
        slice_end: Ending slice index.
        frame_start: Starting frame index.
        frame_end: Ending frame index.

    Returns:
        mask: Segmented image stack consisiting the user annotations.
    """
    # Duplicate the specified stack of slices from the image stack
    mask = Duplicator().run(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end)

    # Display the duplicated image stack
    mask.show()

    # Apply a Look-Up Table (LUT) to enhance the visualization for a stack
    IJ.run(mask, "Apply LUT", "stack")

    IJ.setTool("Paintbrush Tool")
    IJ.setForegroundColor(255,255,255)

        # Create a dialog instructing the user to annotate the image
    wait_dialog = WaitForUserDialog("Title Message", "Mark the object of interest across the stack (To increase brush width double left click on the paintbrush icon from the Toolbar)")
    button_info=wait_dialog.getButton()
    button_info.label="Continue"
    wait_dialog.show()

    # Calculate and set a raw threshold based on the image histogram
    histogram = mask.getStatistics()
    IJ.setRawThreshold(mask, histogram.histMax - 1, histogram.histMax)

    # Convert the thresholded image stack to binary masks
    IJ.run(mask, "Convert to Mask", "method=Default background=Dark black")

    return mask



## Create a graphical user interface (GUI) for  Virtual Orientation Tool Annotation Toolbar 
Win = GenericDialogPlus("User Guided Virtual Orientation Tool Toolbar") 

# Add an option for users to select an image. 
Win.addImageChoice("Input Image", prefs.get("Image","Choice")) 

# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:
Cite paper""") 

# Provide a link to the plugin's documentation on GitHub.
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  

# Display the GUI to the user.
Win.showDialog()

# Check if the user clicked "OK" in the GUI.
if Win.wasOKed():  
    img = Win.getNextImage() 

# Extract metadata from the selected image.
img_Title, img_Bit_Depth, height, width, dimension, channels, slices, frames, img_type = input_image_metadata_extractor(img)

## Determine the type of the selected image.

# If the image type is 2D, duplicate the image and use it for annotation.
if img_type == "2D":
    mask = threshold_single_slice_annotation(img, 1, 1, 1, 1, 1, 1) 
    mask.show()

# If the image has multiple channels, let the user choose the appropriate channel number
elif img_type == "3D" and channels > 1:                       
        Win = GenericDialogPlus("Select the appropriate channel for annotation") 
        Win.addNumericField("Channel_number", prefs.getInt("Channel_number", 1), 1)                                 
        Win.showDialog()
        if Win.wasOKed():  
            Channel_number = int(Win.getNextNumber())
            prefs.put("Channel_number", Channel_number)
            mask = threshold_single_slice_annotation(img, Channel_number, Channel_number, 1, 1, 1, 1) 
            mask.show()
else:
    # Create a dialog for the user to choose the annotation mode (single or multi-slice).
    Win = GenericDialogPlus("Select annotation mode") 
    Win.addChoice("Annotation_mode", ["Single-Slice-Annotation", "Multi-Slice-Annotation"], prefs.get("Annotation_Mode", "Multi-Slice-Annotation")) 
    Win.showDialog()
    
    # Check if the user clicked "OK" in the annotation mode dialog.
    if Win.wasOKed():  
        Annotation_mode = Win.getNextChoice() 
        prefs.put("Annotation_Mode", Annotation_mode)
    
    # If the selected annotation mode is "Single-Slice-Annotation", that means the binary mask created would be just a single image iresspective of the image type (3D,4D,5D etc.)
    if Annotation_mode == "Single-Slice-Annotation":
        if img_type == "3D":
            # If the image has multiple slices, let the user choose the appropriate slice number
            if slices > 1:
                Win = GenericDialogPlus("Select the appropriate slice for annotation") 
                Win.addNumericField("Slice_number", prefs.getInt("Slice_number", 1), 1)                                 
                Win.showDialog()
                if Win.wasOKed():  
                    Slice_number = int(Win.getNextNumber())
                    prefs.put("Slice_number", Slice_number)
                    mask = threshold_single_slice_annotation(img, 1, 1, Slice_number, Slice_number, 1, 1) 
                    mask.show()
            # If the image has multiple frames, let the user choose the appropriate frame number
            elif frames > 1:
                Win = GenericDialogPlus("Select the appropriate frame for annotation") 
                Win.addNumericField("Frame_number", prefs.getInt("Frame_number", 1), 1)                                 
                Win.showDialog()
                if Win.wasOKed():  
                    Frame_number = int(Win.getNextNumber())
                    prefs.put("Frame_number", Frame_number)
                    # Duplicate the image for the selected frame and apply single-slice annotation.
                    mask = Duplicator().run(img, 1, 1, 1, 1, Frame_number, Frame_number)
                    mask = threshold_single_slice_annotation(img, 1, 1, 1, 1, Frame_number, Frame_number) 
                    mask.show()
        elif img_type == "4D":
            # If the image has multiple slices and frames, let the user choose the appropriate slice number and frame number
            if channels == 1:
                Win = GenericDialogPlus("Select the appropriate image for annotation") 
                Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)
                Win.addNumericField("Frame_number", prefs.getInt("Frame_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Slice_number = int(Win.getNextNumber())  
                    Frame_number = int(Win.getNextNumber())
                    prefs.put("Slice_number", Slice_number)
                    prefs.put("Frame_number", Frame_number)
                    mask = threshold_single_slice_annotation(img, 1, 1, Slice_number, Slice_number, Frame_number, Frame_number) 
                    mask.show()
            # If the image has multiple channels and frames, let the user choose the appropriate channel number and frame number        
            elif slices == 1:
                Win = GenericDialogPlus("Select the appropriate image for annotation") 
                Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)
                Win.addNumericField("Frame_number", prefs.getInt("Frame_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Channel_number = int(Win.getNextNumber())  
                    Frame_number = int(Win.getNextNumber())
                    prefs.put("Channel_number", Channel_number)
                    prefs.put("Frame_number", Frame_number)
                    mask = threshold_single_slice_annotation(img, Channel_number, Channel_number, 1, 1, Frame_number, Frame_number) 
                    mask.show()
            # If the image has multiple slices and channels, let the user choose the appropriate slice number and channel number        
            elif frames == 1:
                Win = GenericDialogPlus("Select the appropriate image for annotation") 
                Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)
                Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Channel_number = int(Win.getNextNumber())  
                    Slice_number = int(Win.getNextNumber())
                    prefs.put("Channel_number", Channel_number)
                    prefs.put("Slice_number", Slice_number)
                    mask = threshold_single_slice_annotation(img, Channel_number, Channel_number, Slice_number, Slice_number, 1, 1) 
                    mask.show()
        elif img_type == "5D":
            # Let the user choose the appropriate slice number, channel number and frame number
            Win = GenericDialogPlus("Select the appropriate image for annotation") 
            Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)
            Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)
            Win.addNumericField("Frame_number", prefs.getInt("Frame_number",1),1) 
            Win.showDialog()
            if Win.wasOKed():
                Channel_number = int(Win.getNextNumber())
                Slice_number = int(Win.getNextNumber())  
                Frame_number = int(Win.getNextNumber()) 
                prefs.put("Channel_number", Channel_number)
                prefs.put("Slice_number", Slice_number)
                prefs.put("Frame_number", Frame_number)
                mask = threshold_single_slice_annotation(img, Channel_number, Channel_number, Slice_number, Slice_number, Frame_number, Frame_number) 
                mask.show()
    #If the selected annotation mode is "Multi-Slice-Annotation", that means the binary mask created would be a 3D stack based on theuser annotation           
    elif Annotation_mode == "Multi-Slice-Annotation":        
        if img_type == "3D":
            if slices > 1:
                mask = threshold_multi_slice_annotation(img, 1, 1, 1, slices, 1, 1)
            elif frames > 1:    
                mask = threshold_multi_slice_annotation(img, 1, 1, 1, 1, 1, frames) 
            mask.show()
        elif img_type == "4D":
            # If the image has multiple slices and frames, let the user choose the appropriate slice number and frame number
            if channels == 1:
                Win = GenericDialogPlus("Select the appropriate image stack for annotation") 
                Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Slice_number = int(Win.getNextNumber())  
                    prefs.put("Slice_number", Slice_number)
                    mask = threshold_multi_slice_annotation(img, 1, 1, Slice_number, Slice_number, 1, frames)
                    mask.show()
            # If the image has multiple channels and frames, let the user choose the appropriate channel number and frame number        
            elif slices == 1:
                Win = GenericDialogPlus("Select the appropriate image stack for annotation") 
                Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Channel_number = int(Win.getNextNumber())  
                    prefs.put("Channel_number", Channel_number)
                    mask = threshold_multi_slice_annotation(img, Channel_number, Channel_number, 1, 1, 1, frames)
                    mask.show()
            # If the image has multiple slices and channels, let the user choose the appropriate slice number and channel number        
            elif frames == 1:
                Win = GenericDialogPlus("Select the appropriate image stack for annotation") 
                Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Channel_number = int(Win.getNextNumber())  
                    prefs.put("Channel_number", Channel_number)
                    mask = threshold_multi_slice_annotation(img, Channel_number, Channel_number, 1, slices, 1, 1)
                    mask.show()
        elif img_type == "5D":
            # Let the user choose the appropriate slice number, channel number and frame number
            Win = GenericDialogPlus("Select the appropriate image stack for annotation") 
            Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)
            Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)
            Win.showDialog()
            if Win.wasOKed():
                Channel_number = int(Win.getNextNumber())
                Slice_number = int(Win.getNextNumber())  
                prefs.put("Channel_number", Channel_number)
                prefs.put("Slice_number", Slice_number)
                mask = threshold_multi_slice_annotation(img, Channel_number, Channel_number, Slice_number, Slice_number, 1, frames)
                mask.show()

### Create a graphical user interface (GUI) for Virtual Orientation Toolbar
Win = GenericDialogPlus("Virtual Orientation Toolbar") 
Win.addChoice("Tasks", ["Centering", "Rotation","Centering+Rotation"], prefs.get("Tasks","Centering+Rotation"))
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
Win.addChoice("Center_Of_Rotation", ["Object_center", "Image_center"], prefs.get("Center_Of_Rotation","Image_center"))
Win.addChoice("Enlarge", ["Yes", "No"], prefs.get("Enlarge","No")) 
Win.showDialog()
if Win.wasOKed():  
    task = Win.getNextChoice()
    orientation = Win.getNextChoice()
    center_of_rotation = Win.getNextChoice()
    enlarge = Win.getNextChoice()     
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Enlarge", enlarge)


##Calling the utils file 
from VOT_Utils import process_input_img,output_image_maker
ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge)
imp_out = output_image_maker(img, ip_list)
imp_out.show()
imp_out.changes = True
