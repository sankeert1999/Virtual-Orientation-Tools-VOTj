#@PrefService prefs 

from ij import IJ
from ij.macro import MacroConstants
from ij.plugin import ImageCalculator,Duplicator, ImageInfo,Commands
from ij.gui import WaitForUserDialog, GenericDialog
from fiji.util.gui import GenericDialogPlus
import os 

Win = GenericDialogPlus("Virtual Orientation Toolbar (Batch)")
Win.addDirectoryOrFileField("Image directory selector", prefs.get("InputDirPath", ""))
Win.addDirectoryOrFileField("Output directory", prefs.get("OutputDirPath", ""))
Win.addDirectoryOrFileField("Select the Macro/Script file for execution", prefs.get("MacroFilePath", ""))
Win.addChoice("Save_Format", ["tif", "tiff","jpg","jpeg","png","bmp"], prefs.get("Save_Format", "tiff"))
Win.addChoice("Tasks", ["Centering", "Rotation","Centering+Rotation"], prefs.get("Tasks","Centering+Rotation"))
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
Win.addChoice("Center_Of_Rotation", ["Object_center", "Image_center"], prefs.get("Center_Of_Rotation","Image_center"))
Win.addChoice("Enlarge", ["Yes", "No"], prefs.get("Enlarge","No")) 
Win.addChoice("Object_Polarity", ["None", "Left-Right/Top-Bottom", "Right-Left/Bottom-Top"], prefs.get("Object_Polarity","None"))
Win.addCheckbox("Save_Mask_File", prefs.getInt("SaveMask", False)) 
Win.addChoice("Mask_Save_Format", ["tif", "tiff","jpg","jpeg","png","bmp"], prefs.get("Save_Format", "tiff"))

# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:
Cite paper""") 

# Provide a link to the plugin's documentation on GitHub.
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  

# Display the GUI to the user.
Win.showDialog()

if Win.wasOKed():  
    InputDirPath = Win.getNextString()
    OutputDirPath = Win.getNextString()
    MacroFilePath = Win.getNextString()
    Save_Format = Win.getNextChoice()
    task = Win.getNextChoice()
    orientation = Win.getNextChoice()
    center_of_rotation = Win.getNextChoice()
    enlarge = Win.getNextChoice()
    object_polarity = Win.getNextChoice()
    save_mask  = Win.getNextBoolean() 
    Mask_Save_Format = Win.getNextChoice()
    prefs.put("InputDirPath", InputDirPath)
    prefs.put("OutputDirPath", OutputDirPath)
    prefs.put("MacroFilePath", MacroFilePath)
    prefs.put("Save_Format", Save_Format)
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Enlarge", enlarge)
    prefs.put("Object_Polarity", object_polarity)
    prefs.put("Save_Mask", save_mask)
    prefs.put("Mask_Save_Format", Mask_Save_Format)

    if save_mask == True:
        # Specify the path for the new directory
        Mask_Directory_Path = os.path.join(OutputDirPath, "Mask_VOTj")
        # Create the directory
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
            ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity)
            imp_out = output_image_maker(img, ip_list)
            imp_out.show()
            out_filename = imp_out.getTitle()
            out_file_path = os.path.join(OutputDirPath, out_filename)
            IJ.saveAs(imp_out, Save_Format,out_file_path)
            if save_mask == True:
                mask_file_path = os.path.join(Mask_Directory_Path, out_filename)
                IJ.saveAs(mask, Mask_Save_Format,mask_file_path)
            Commands.closeAll()
