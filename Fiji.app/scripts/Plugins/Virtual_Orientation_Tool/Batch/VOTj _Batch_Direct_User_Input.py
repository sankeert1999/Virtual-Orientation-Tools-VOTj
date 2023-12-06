#@PrefService prefs 

from ij import IJ
from ij.macro import MacroConstants
from ij.plugin import ImageCalculator, Duplicator, ImageInfo, Commands
from ij.gui import WaitForUserDialog, GenericDialog
from fiji.util.gui import GenericDialogPlus
from java.awt import Font
import os 

# Create a generic dialog window with a specific title
Win = GenericDialogPlus("Virtual Orientation Tool for FIJI (VOTj)_Batch - Direct User Input")

# Add a message to the dialog window with a specified font for the input configuration section
custom_font_h1 = Font("SansSerif", Font.BOLD, 14)
Win.addMessage("Input Configuration", custom_font_h1) 

# Add directory or file fields to input image and mask directories
Win.addDirectoryOrFileField("Image directory selector", prefs.get("InputDirPath", ""))
Win.addDirectoryOrFileField("Mask directory selector", prefs.get("MaskDirPath", ""))

# Add a message to the dialog window with a specified font for the object alignment settings section
Win.addMessage("Object alignment settings", custom_font_h1) 

# Add choices for different alignment settings
Win.addChoice("Tasks", ["Move object to image-center", "Align object to desired orientation", "Center object and then align to orientation"], prefs.get("Tasks", "Center object and then align to orientation"))
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation", "Horizontal"))
Win.addChoice("Center of rotation", ["Object center", "Image center"], prefs.get("Center of rotation", "Image center"))
Win.addChoice("Alignment with object pointing to", ["Any", "Left (for horizontal) / Top (for vertical)", "Right (for horizontal) / Bottom (for vertical)"], prefs.get("Alignment with object pointing to", "Any"))
Win.addChoice("Fill background with", ["Black","White", "Mean"], prefs.get("Fill background with","Black"))
# Add a message to the dialog window with a specified font for additional options section
Win.addMessage("Additional options", custom_font_h1) 

# Add checkboxes for additional options
Win.addCheckbox("Enlarge_canvas (prevent image cropping)", prefs.getInt("Enlarge", False)) 
Win.addCheckbox("Log File Output", prefs.getInt("Log_Window", False)) 

# Add a message to the dialog window with a specified font for output configuration section
Win.addMessage("Output Configuration", custom_font_h1) 

# Add directory or file fields for output directory
Win.addDirectoryOrFileField("Save processed images/masks to", prefs.get("OutputDirPath", ""))
Win.addChoice("Save images in format", ["tif", "tiff", "jpg", "jpeg", "png", "bmp"], prefs.get("Save_Format_out", "tiff"))

# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:
Cite paper""") 

# Provide a link to the plugin's documentation on GitHub.
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  

# Display the GUI to the user.
Win.showDialog()

# Check if the user clicked the OK button in the dialog
if Win.wasOKed():  

    # Retrieve values from the dialog for various configuration parameters
    InputDirPath = Win.getNextString()
    MaskDirPath = Win.getNextString()
    task = Win.getNextChoice()
    orientation = Win.getNextChoice()
    center_of_rotation = Win.getNextChoice()
    object_polarity = Win.getNextChoice()
    background = Win.getNextChoice()
    enlarge = Win.getNextBoolean()
    log_window = Win.getNextBoolean()
    OutputDirPath = Win.getNextString()
    Save_Format = Win.getNextChoice()

    # Store the retrieved values in the preferences
    prefs.put("InputDirPath", InputDirPath)
    prefs.put("MaskDirPath", MaskDirPath)
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Object_Polarity", object_polarity)
    prefs.put("Fill_background_with", background)
    prefs.put("Enlarge", enlarge)
    prefs.put("log_window", log_window)
    prefs.put("OutputDirPath", OutputDirPath)
    prefs.put("Save_Format", Save_Format)

    # Get a list of files in the folder
    # Supported image file extensions
    image_extensions = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp']
    input_files_lst = os.listdir(InputDirPath)
    mask_files_lst = os.listdir(MaskDirPath)
    input_imgs_lst = []
    mask_imgs_lst = []

    if log_window == True:
        IJ.log("Logging the selected configuration options")
        IJ.log("Tasks : " + str(task))
        IJ.log("Orientation : " + str(orientation))
        IJ.log("Center of rotation : " + str(center_of_rotation))
        IJ.log("Alignment with object pointing to : " + str(object_polarity))
        IJ.log("Enlarge canvas (prevent image cropping) : " + str(enlarge))
        IJ.log("Fill background with : " + str(background))
        IJ.log("  ")

    # Check if the file is an image based on the extension
    for temp_input_file_name in input_files_lst:
        if any(temp_input_file_name.lower().endswith(ext) for ext in image_extensions):
            input_imgs_lst.append(temp_input_file_name)
    input_imgs_lst.sort()
    for temp_mask_file_name in mask_files_lst:
        if any(temp_mask_file_name.lower().endswith(ext) for ext in image_extensions):
            mask_imgs_lst.append(temp_mask_file_name)
    mask_imgs_lst.sort()
    # Check if the number of image files in the mask and image folders is equal
    if len(mask_imgs_lst) == len(input_imgs_lst):		
        for file_serial in range(len(mask_imgs_lst)):
            input_file_name = input_imgs_lst[file_serial]
            mask_file_name = mask_imgs_lst[file_serial]
            # Create the full path to the file
            input_file_path = os.path.join(InputDirPath, input_file_name)
            mask_file_path = os.path.join(MaskDirPath, mask_file_name)
            img = IJ.openImage(input_file_path)
            mask = IJ.openImage(mask_file_path)
            if mask_file_name.lower().startswith(input_file_name.lower()[:input_file_name.lower().rfind(".")]):                
                img.show()                
                mask.show()                
                # Calling the utils file
                    # Check if dimensions of the input image and mask match
                if (img.getHeight() != mask.getHeight()) or (img.getWidth() != mask.getWidth()):
                    IJ.error("Mask dimension and Image dimension don't match")
                    if log_window == True:
                        IJ.log("Logging the detected object orienatation")
                        IJ.log("Mask dimension and image dimension don't match, object orientation aborted.")
                        IJ.log("Filename : " + str(img.getTitle()))
                        IJ.log(" Filename : " + str(mask.getTitle()))
                        IJ.log(" ")
                    continue

                else:
                    from VOT_Utils import process_input_img, output_image_maker
                    if log_window == True:
                        IJ.log("Logging the detected object orienatation")
                        IJ.log("Filename : " + str(img.getTitle()))
                        IJ.log(" Filename : " + str(mask.getTitle()))
                        
                    ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity,background,log_window)
                    imp_out = output_image_maker(img, ip_list)
                    imp_out.show()
                    out_filename = imp_out.getTitle()
                    out_file_path = os.path.join(OutputDirPath, out_filename)
                    IJ.saveAs(imp_out, Save_Format, out_file_path)
                    Commands.closeAll()
            else:
                error = "The mask filename doesn't match the image filename. Please verify."
                IJ.error("Filename Mismatch", error)
                if log_window == True:
                    IJ.log("Logging the detected object orienatation")
                    IJ.log("The mask filename doesn't match the image filename, object orientation aborted.")
                    IJ.log("Filename : " + str(img.getTitle()))
                    IJ.log(" Filename : " + str(mask.getTitle()))
                    IJ.log(" ")
                continue
    else:
        error = "The number of image files in the mask and image folders are unequal. Please check the respective folders."
        IJ.error("Folder Mismatch Error", error)
        raise Exception(error) # needed to stop further execution
