#@PrefService prefs 

from ij import IJ
from ij.macro import MacroConstants
from ij.plugin import ImageCalculator,Duplicator, ImageInfo,Commands
from ij.gui import WaitForUserDialog, GenericDialog
from fiji.util.gui import GenericDialogPlus
from java.awt import Font
import os 

Win = GenericDialogPlus("Virtual Orientation Tools for FIJI (VOTj)_Batch - Custom Macro")
# Add a message with the specified font
custom_font_h1 = Font("SansSerif", Font.BOLD, 14)  # Adjust font properties as needed
Win.addMessage("Input Configuration",custom_font_h1) 
Win.addDirectoryOrFileField("Image_directory", prefs.get("InputDirPath", ""))
Win.addMessage("Custom_Segmentation_Macro_Configuration",custom_font_h1) 
Win.addDirectoryOrFileField("Select_the_Macro/Script_file_for_execution", prefs.get("MacroFilePath", ""))

# Add a message with the specified font
Win.addMessage("Object alignment settings",custom_font_h1) 
# Create a Font instance
Win.addChoice("Tasks", ["Move object to image-center","Align object to desired orientation" ,"Center object and then align to orientation"], prefs.get("Tasks","Center object and then align to orientation"))
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
Win.addChoice("Center_of_rotation", ["Object center", "Image center"], prefs.get("Center of rotation","Image center"))
Win.addChoice("Alignment_with_object_pointing_to", ["Any","Left (for horizontal) / Top (for vertical)", "Right (for horizontal) / Bottom (for vertical)"], prefs.get("Alignment with object pointing to","Any"))
Win.addChoice("Fill_background_with", ["Black","White", "Mean"], prefs.get("Fill background with","Black"))
# Add a message with the specified font
Win.addMessage("Additional options",custom_font_h1) 
Win.addCheckbox("Enlarge_canvas (prevent image cropping)", prefs.getInt("Enlarge", False)) 
Win.addCheckbox("Log_output", prefs.getInt("Log_Window", False)) 

Win.addMessage("Output Configuration",custom_font_h1) 
Win.addDirectoryOrFileField("Save_processed_images/masks_to", prefs.get("OutputDirPath", ""))
Win.addChoice("Save_images_in_format", ["tif", "tiff","jpg","jpeg","png","bmp"], prefs.get("Save_Format_out", "tiff"))

Win.addCheckbox("Save_generated_mask", prefs.getInt("SaveMask", False)) 
Win.addToSameRow()
Win.addChoice("Save_masks_in_format", ["tif", "tiff","jpg","jpeg","png","bmp"], prefs.get("Save_Format_mask", "tiff"))

# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:
Cite paper""") 

# Provide a link to the plugin's documentation on GitHub.
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  

# Display the GUI to the user.
Win.showDialog()

if Win.wasOKed():  
    InputDirPath = Win.getNextString()
    MacroFilePath = Win.getNextString()
    task = Win.getNextChoice()
    orientation = Win.getNextChoice()
    center_of_rotation = Win.getNextChoice()
    object_polarity = Win.getNextChoice()
    background = Win.getNextChoice()
    enlarge = Win.getNextBoolean()
    log_window = Win.getNextBoolean()
    OutputDirPath = Win.getNextString()
    Save_Format = Win.getNextChoice()
    save_mask  = Win.getNextBoolean() 
    Mask_Save_Format = Win.getNextChoice()    

    prefs.put("InputDirPath", InputDirPath)
    prefs.put("MacroFilePath", MacroFilePath)
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Object_Polarity", object_polarity)
    prefs.put("Fill_background_with", background)
    prefs.put("Enlarge", enlarge)
    prefs.put("log_window", log_window)
    prefs.put("OutputDirPath", OutputDirPath)
    prefs.put("Save_Format", Save_Format)
    prefs.put("Save_Mask", save_mask)
    prefs.put("Mask_Save_Format", Mask_Save_Format)
    
    if log_window == True:
        IJ.log("Logging the selected configuration options")
        IJ.log("Tasks : " + str(task))
        IJ.log("Orientation : " + str(orientation))
        IJ.log("Center of rotation : " + str(center_of_rotation))
        IJ.log("Alignment with object pointing to : " + str(object_polarity))
        IJ.log("Enlarge canvas (prevent image cropping) : " + str(enlarge))
        IJ.log("Fill background with : " + str(background))
        IJ.log("  ")
        

    if save_mask == True:
        # Specify the path for the new directory
        Mask_Directory_Path = os.path.join(OutputDirPath, "Mask_VOTj")
        # Create the directory
        if not os.path.exists(Mask_Directory_Path):
            os.makedirs(Mask_Directory_Path)

    # Get a list of files in the folder
    files = os.listdir(InputDirPath)
    # Supported image file extensions
    image_extensions = ['.tif', '.tiff', '.jpg', '.jpeg', '.png','.bmp']

    for file_name in files:
        # Create the full path to the file
        file_path = os.path.join(InputDirPath, file_name)

        # Check if the file is an image based on the extension
        if any(file_name.lower().endswith(ext) for ext in image_extensions):
            img = IJ.openImage(file_path)
            img.show()
            IJ.runMacroFile(MacroFilePath)
            mask = IJ.getImage()
            mask.changes = False
            
            ##Calling the utils file 
            from VOT_Utils import process_input_img,output_image_maker

            if (img.getHeight() != mask.getHeight()) or (img.getWidth() != mask.getWidth()):
                IJ.error("Mask dimension and Image dimension don't match")
                if log_window == True:
                    IJ.log("Logging the detected object orientation")
                    IJ.log("Mask dimension and image dimension don't match, object orientation aborted.")
                    IJ.log("Filename : " + str(img.getTitle()))
                    IJ.log(" Filename : " + str(mask.getTitle()))
                    IJ.log(" ")
                continue

            if log_window == True:
                IJ.log(" Filename : " + str(img.getTitle()))

            
            ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity,background,log_window)
            imp_out = output_image_maker(img, ip_list)
            imp_out.show()
            out_filename = imp_out.getTitle()
            out_file_path = os.path.join(OutputDirPath, out_filename)
            IJ.saveAs(imp_out, Save_Format,out_file_path)
            if save_mask == True:
                out_filename_mask = img.getTitle()[:img.getTitle().rfind(".")]+"_Mask"
                mask_file_path = os.path.join(Mask_Directory_Path, out_filename_mask)
                IJ.saveAs(mask, Mask_Save_Format,mask_file_path)
            Commands.closeAll()



                
