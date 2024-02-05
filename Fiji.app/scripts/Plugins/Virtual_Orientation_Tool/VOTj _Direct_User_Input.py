#@PrefService prefs 

from ij import IJ
from fiji.util.gui import GenericDialogPlus
from java.awt import Font
Win = GenericDialogPlus("Virtual Orientation Tool for FIJI (VOTj) - Direct User Input")
# Add a message with the specified font
custom_font_h1 = Font("SansSerif", Font.BOLD, 14)  # Adjust font properties as needed
Win.addMessage("Input Configuration",custom_font_h1) 

Win.addImageChoice("Select_the_image", prefs.get("Image","Choice")) 
Win.addImageChoice("Select_the_mask", prefs.get("Mask", "Choice")) 


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
Win.addCheckbox("Enlarge_canvas (prevent image cropping)", prefs.getInt("Enlarge", False)) 
Win.addCheckbox("Log_File_Output", prefs.getInt("Log_Window", False)) 

# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:Cite paper""") 

# Provide a link to the plugin's documentation on GitHub.
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  

# Display the GUI to the user.
Win.showDialog()

if Win.wasOKed(): 
    img = Win.getNextImage()  
    mask = Win.getNextImage() 
    task = Win.getNextChoice()
    orientation = Win.getNextChoice()
    center_of_rotation = Win.getNextChoice()
    object_polarity = Win.getNextChoice()
    background = Win.getNextChoice()
    enlarge = Win.getNextBoolean() 
    log_window = Win.getNextBoolean() 
    prefs.put("Image", img.getTitle()) 
    prefs.put("Mask", mask.getTitle()) 
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Object_Polarity", object_polarity)
    prefs.put("Fill_background_with", background)
    prefs.put("Enlarge", enlarge)
    prefs.put("log_window", log_window)


    from VOT_Utils import process_input_img,output_image_maker
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



