#@PrefService prefs 

from ij import IJ
from ij.plugin import ImageCalculator,Duplicator
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
    img_Title = img.getTitle()
    img_Bit_Depth = img.getBitDepth()
    height = img.getHeight()
    width = img.getWidth()
    dimension = img.getNDimensions()
    channels = img.getNChannels()
    slices = img.getNSlices()
    frames = img.getNFrames()

    if channels == 1 and slices == 1 and frames == 1:
        img_type="2D"
    elif (channels > 1 and slices == 1 and frames == 1) or (channels == 1 and slices > 1 and frames == 1) or (channels == 1 and slices == 1 and frames > 1):
        img_type="3D"
    elif (channels > 1 and slices > 1 and frames == 1) or (channels > 1 and slices == 1 and frames > 1) or (channels == 1 and slices > 1 and frames > 1):
        img_type="4D" 
    elif (channels > 1 and slices > 1 and frames > 1) :
        img_type="5D"    
    
    return img_Title, img_Bit_Depth, height, width, dimension, channels, slices, frames,img_type

def threshold_single_slice_annotation(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end):
    mask = Duplicator().run(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end)
    mask.show()
    IJ.run(mask, "Apply LUT", "")
    # Create a WaitForUserDialog with a title message
    wait_dialog = WaitForUserDialog("Title Message", "Pick the paint brush tool and mark the object of interest")
    wait_dialog.show()
    # Get the histogram data
    histogram = mask.getStatistics()
    IJ.setRawThreshold(mask, histogram.histMax - 1, histogram.histMax)
    IJ.run(mask, "Convert to Mask", "")
    return mask

def threshold_multi_slice_annotation(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end):
    mask = Duplicator().run(img, channel_start, channel_end, slice_start, slice_end, frame_start, frame_end)     
    mask.show()
    IJ.run(mask, "Apply LUT", "stack")
    # Create a WaitForUserDialog with a title message
    wait_dialog = WaitForUserDialog("Title Message", "Pick the paint brush tool and mark the object of interest across the stack")
    wait_dialog.show()
    # Get the histogram data
    histogram = mask.getStatistics()
    IJ.setRawThreshold(mask, histogram.histMax - 1, histogram.histMax)
    IJ.run(mask, "Convert to Mask", "method=Default background=Dark black")
    return mask


## Create GUI 
Win = GenericDialogPlus("Virtual Orientation Tool Annotation Toolbar") 
Win.addImageChoice("Image", prefs.get("Image","Choice")) 
Win.addMessage("""If you use this plugin please cite :
Cite paper""") 
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  
Win.showDialog()

if Win.wasOKed():  
	img = Win.getNextImage() 
img_Title, img_Bit_Depth, height, width, dimension, channels, slices, frames,img_type = input_image_metadata_extractor(img)

## Getting the image type
## If image type is 2D just duplicate the image and give that for the annotation
if img_type == "2D":
    mask = threshold_single_slice_annotation(img, 1, 1, 1, 1, 1, 1) 
    mask.show()
else:
    # Create a WaitForUserDialog with a title message
    Win = GenericDialogPlus("Select annotation mode") 
    Win.addChoice("Annotation_mode", ["Single-Slice-Annotation","Multi-Slice-Annotation"], prefs.get("Annotation_Mode","Multi-Slice-Annotation")) 
    Win.showDialog()
    if Win.wasOKed():  
        Annotation_mode = Win.getNextChoice() 
        prefs.put("Annotation_Mode", Annotation_mode)
    if Annotation_mode == "Single-Slice-Annotation":
        if img_type == "3D":
            if channels > 1:                        
                Win = GenericDialogPlus("Select the appropriate channel for annotation") 
                Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)                                 
                Win.showDialog()
                if Win.wasOKed():  
                    Channel_number = int(Win.getNextNumber())
                    prefs.put("Channel_number", Channel_number)
                    mask = threshold_single_slice_annotation(img, Channel_number, Channel_number, 1, 1, 1, 1) 
                    mask.show()
            elif slices > 1:
                Win = GenericDialogPlus("Select the appropriate slice for annotation") 
                Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)                                 
                Win.showDialog()
                if Win.wasOKed():  
                    Slice_number = int(Win.getNextNumber())
                    prefs.put("Slice_number", Slice_number)
                    mask = threshold_single_slice_annotation(img, 1, 1, Slice_number, Slice_number, 1, 1) 
                    mask.show()
            elif frames > 1:
                Win = GenericDialogPlus("Select the appropriate frame for annotation") 
                Win.addNumericField("Frame_number", prefs.getInt("Frame_number",1),1)                                 
                Win.showDialog()
                if Win.wasOKed():  
                    Frame_number = int(Win.getNextNumber())
                    prefs.put("Frame_number", Frame_number)
                    mask = Duplicator().run(img, 1, 1, 1, 1, Frame_number, Frame_number)
                    mask = threshold_single_slice_annotation(img, 1, 1, 1, 1, Frame_number, Frame_number) 
                    mask.show()
        elif img_type == "4D":
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
    elif Annotation_mode == "Multi-Slice-Annotation":        
        if img_type == "3D":
            if channels > 1:
                IJ.error("For multichannel 3D stack a 2D binary mask is expected")
                raise Exception("Expected a single annotation but got multiple annotation")
            else:
                if slices > 1:
                    mask = threshold_multi_slice_annotation(img, 1, 1, 1, slices, 1, 1)
                elif frames > 1:    
                    mask = threshold_multi_slice_annotation(img, 1, 1, 1, 1, 1, frames) 
                mask.show()
        elif img_type == "4D":
            if channels == 1:
                Win = GenericDialogPlus("Select the appropriate image stack for annotation") 
                Win.addNumericField("Slice_number", prefs.getInt("Slice_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Slice_number = int(Win.getNextNumber())  
                    prefs.put("Slice_number", Slice_number)
                    mask = threshold_multi_slice_annotation(img, 1, 1, Slice_number, Slice_number, 1, frames)
                    mask.show()
            elif slices == 1:
                Win = GenericDialogPlus("Select the appropriate image stack for annotation") 
                Win.addNumericField("Channel_number", prefs.getInt("Channel_number",1),1)                                   
                Win.showDialog()
                if Win.wasOKed():
                    Channel_number = int(Win.getNextNumber())  
                    prefs.put("Channel_number", Channel_number)
                    mask = threshold_multi_slice_annotation(img, Channel_number, Channel_number, 1, 1, 1, frames)
                    mask.show()
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

from VOT_Utils import process_input_img,output_image_maker

ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge)
imp_out = output_image_maker(img, ip_list)
imp_out.show()