#@PrefService prefs 

from ij import IJ
from ij.macro import MacroConstants
from ij.process import StackStatistics
from ij.plugin import ImageCalculator,Duplicator, ImageInfo
from ij.gui import WaitForUserDialog, GenericDialog, NonBlockingGenericDialog
from fiji.util.gui import GenericDialogPlus
from java.awt import Font
##Calling the utils file 
from VOT_Utils import process_input_img,output_image_maker,CustomWaitDialog
import textwrap


def wait_dialog_box(mask):
    long_string = textwrap.dedent(""" 
    - Double-click the paintbrush icon to increase brush width.
    - Press spacebar/enter or click 'Continue' to proceed.""")

    # Split the long string into sentences
    sentences = long_string.split('\n')

    # Set the desired width for each line
    line_width = 50

    # Center-align each sentence individually
    centered_sentences = [sentence.center(line_width) for sentence in sentences]
    centered_text='\n'.join(centered_sentences)
    wait_dialog = CustomWaitDialog("Mark the object of interest on the image/stack",centered_text)
    mask.getCanvas().addKeyListener(wait_dialog) # add the dialog as a listener to key events on the image, this way any key event will call keyPressed(self, e) of the dialog 
    wait_dialog.show()


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
    # Calculate and set a raw threshold based on the image histogram
    histogram = mask.getStatistics()
    max_value = histogram.max + 50
    mask.setDisplayRange(histogram.min, max_value )
    IJ.setTool("Paintbrush Tool")
    IJ.setForegroundColor(255,255,255)

    # Create a dialog instructing the user to annotate the image
    wait_dialog_box(mask)

    if mask.getBitDepth() == 24:
        IJ.run(mask, "8-bit", "")
        IJ.setRawThreshold(mask, 254,255)
        # Convert the thresholded image to a binary mask
        IJ.run(mask, "Convert to Mask", "")
        return mask

    
    IJ.setRawThreshold(mask, max_value - 1, max_value)

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

    # Display the duplicated slice
    mask.show()
    # Calculate and set a raw threshold based on the image histogram
    histogram = StackStatistics(mask)
    max_value = histogram.max + 50
    mask.setDisplayRange(histogram.min, max_value )
    IJ.setTool("Paintbrush Tool")
    IJ.setForegroundColor(255,255,255)

    # Create a dialog instructing the user to annotate the image
    wait_dialog_box(mask)

    if mask.getBitDepth() == 24:
        IJ.run(mask, "8-bit", "")
        IJ.setRawThreshold(mask, 254,255)
        # Convert the thresholded image stack to binary masks
        IJ.run(mask, "Convert to Mask", "method=Default background=Dark black")
        return mask
    
    IJ.setRawThreshold(mask, max_value - 1, max_value)

    # Convert the thresholded image stack to binary masks
    IJ.run(mask, "Convert to Mask", "method=Default background=Dark black")

    return mask



## Create a graphical user interface (GUI) for  Virtual Orientation Tool Annotation Toolbar 
Win = GenericDialogPlus("Virtual Orientation Tool for FIJI (VOTj) - Annotation Assisted Alignment") 

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
            Win = NonBlockingGenericDialog("Select the appropriate channel for annotation") 
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
                    Win = NonBlockingGenericDialog("Select the appropriate slice for annotation") 
                    Win.addNumericField("Slice_number", prefs.getInt("Slice_number", 1), 1)                                 
                    Win.showDialog()
                    if Win.wasOKed():  
                        Slice_number = int(Win.getNextNumber())
                        prefs.put("Slice_number", Slice_number)
                        mask = threshold_single_slice_annotation(img, 1, 1, Slice_number, Slice_number, 1, 1) 
                        mask.show()
                # If the image has multiple frames, let the user choose the appropriate frame number
                elif frames > 1:
                    Win = NonBlockingGenericDialog("Select the appropriate frame for annotation") 
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
                    Win = NonBlockingGenericDialog("Select the appropriate image for annotation") 
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
                    Win = NonBlockingGenericDialog("Select the appropriate image for annotation") 
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
                    Win = NonBlockingGenericDialog("Select the appropriate image for annotation") 
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
                Win = NonBlockingGenericDialog("Select the appropriate image for annotation") 
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
                    Win = NonBlockingGenericDialog("Select the appropriate image stack for annotation") 
                    Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)                                   
                    Win.showDialog()
                    if Win.wasOKed():
                        Slice_number = int(Win.getNextNumber())  
                        prefs.put("Slice_number", Slice_number)
                        mask = threshold_multi_slice_annotation(img, 1, 1, Slice_number, Slice_number, 1, frames)
                        mask.show()
                # If the image has multiple channels and frames, let the user choose the appropriate channel number and frame number        
                elif slices == 1:
                    Win = NonBlockingGenericDialog("Select the appropriate image stack for annotation") 
                    Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)                                   
                    Win.showDialog()
                    if Win.wasOKed():
                        Channel_number = int(Win.getNextNumber())  
                        prefs.put("Channel_number", Channel_number)
                        mask = threshold_multi_slice_annotation(img, Channel_number, Channel_number, 1, 1, 1, frames)
                        mask.show()
                # If the image has multiple slices and channels, let the user choose the appropriate slice number and channel number        
                elif frames == 1:
                    Win = NonBlockingGenericDialog("Select the appropriate image stack for annotation") 
                    Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)                                   
                    Win.showDialog()
                    if Win.wasOKed():
                        Channel_number = int(Win.getNextNumber())  
                        prefs.put("Channel_number", Channel_number)
                        mask = threshold_multi_slice_annotation(img, Channel_number, Channel_number, 1, slices, 1, 1)
                        mask.show()
            elif img_type == "5D":
                # Let the user choose the appropriate slice number, channel number and frame number
                Win = NonBlockingGenericDialog("Select the appropriate image stack for annotation") 
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
    Win = GenericDialogPlus("Virtual Orientation Tool for FIJI (VOTj) - Annotation Assisted Alignment") 
    # Add a message with the specified font
    custom_font_h1 = Font("SansSerif", Font.BOLD, 14)  # Adjust font properties as needed
    # Add a message with the specified font
    Win.addMessage("Object alignment settings",custom_font_h1) 
    Win.addChoice("Tasks", ["Move object to image-center","Align object to desired orientation" ,"Center object and then align to orientation"], prefs.get("Tasks","Center object and then align to orientation"))
    # Create a Font instance
    Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
    Win.addChoice("Center_of_rotation", ["Object center", "Image center"], prefs.get("Center of rotation","Image center"))
    Win.addChoice("Alignment_with_object_pointing_to", ["Any","Left (for horizontal) / Top (for vertical)", "Right (for horizontal) / Bottom (for vertical)"], prefs.get("Alignment with object pointing to","Any"))
    Win.addChoice("Fill_background_with", ["Black","White", "Mean"], prefs.get("Fill background with","Black"))
    # Add a message with the specified font
    Win.addMessage("Additional options",custom_font_h1) 
    Win.addCheckbox("Enlarge_canvas_(prevent image cropping)", prefs.getInt("Enlarge", False)) 
    Win.addCheckbox("Log_window", prefs.getInt("Log_Window", False)) 
    # Display the GUI to the user.
    Win.showDialog()
    if Win.wasOKed():  
        task = Win.getNextChoice()
        orientation = Win.getNextChoice()
        center_of_rotation = Win.getNextChoice()
        object_polarity = Win.getNextChoice()
        background = Win.getNextChoice()
        enlarge = Win.getNextBoolean() 
        log_window = Win.getNextBoolean()
        prefs.put("Tasks", task)
        prefs.put("Orientation", orientation)
        prefs.put("Center_Of_Rotation", center_of_rotation)
        prefs.put("Object_Polarity", object_polarity)
        prefs.put("Fill_background_with", background)
        prefs.put("Enlarge", enlarge)
        prefs.put("log_window", log_window) 


        if log_window == True:
            IJ.log("Logging the selected configuration options")
            IJ.log("Tasks : " + str(task))
            IJ.log("Orientation : " + str(orientation))
            IJ.log("Center of rotation : " + str(center_of_rotation))
            IJ.log("Alignment with object pointing to : " + str(object_polarity))
            IJ.log("Enlarge canvas (prevent image cropping) : " + str(enlarge))
            IJ.log("Fill background with : " + str(background))
            IJ.log("  ")
            IJ.log("Logging the detected object orientation")
            IJ.log("Filename : " + str(img.getTitle()))
        ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity,background,log_window)
        imp_out = output_image_maker(img, ip_list)
        imp_out.show()
        imp_out.changes = True
