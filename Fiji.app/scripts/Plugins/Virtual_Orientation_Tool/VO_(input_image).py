#@PrefService prefs 

from ij import IJ
from fiji.util.gui import GenericDialogPlus
from java.awt import Font
Win = GenericDialogPlus("Virtual Orientation Toolbar")
# Add a message with the specified font
custom_font_h1 = Font("SansSerif", Font.BOLD, 14)  # Adjust font properties as needed
Win.addMessage("Input Configuration",custom_font_h1) 

Win.addImageChoice("Select the image", prefs.get("Image","Choice")) 
Win.addImageChoice("Select the mask", prefs.get("Mask", "Choice")) 
Win.addChoice("Tasks", ["Move object to image-center","Align object to desired orientation" ,"Center object and then align to orientation"], prefs.get("Tasks","Center object and then align to orientation"))
# Create a Font instance

# Add a message with the specified font
Win.addMessage("Object alignment settings",custom_font_h1) 
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
Win.addChoice("Center of rotation", ["Object center", "Image center"], prefs.get("Center of rotation","Image center"))
Win.addChoice("Alignement with object pointing to", ["Any","Left (for horizontal) / Top (for vertical)", "Right (for horizontal) / Bottom (for vertical)"], prefs.get("Alignement with object pointing to","Any"))
# Add a message with the specified font
Win.addMessage("Additional options",custom_font_h1) 
Win.addCheckbox("Enlarge_canvas (prevent image cropping)", prefs.getInt("Enlarge", False)) 
Win.addCheckbox("Log File Output", prefs.getInt("Log_Window", False)) 

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
    enlarge = Win.getNextBoolean() 
    log_window = Win.getNextBoolean() 
    prefs.put("Image", img.getTitle()) 
    prefs.put("Mask", mask.getTitle()) 
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Object_Polarity", object_polarity)
    prefs.put("Enlarge", enlarge)
    prefs.put("Enlarge", log_window)


    from VOT_Utils import process_input_img,output_image_maker
    if log_window == True:
        IJ.log(" Filename : " + str(img.getTitle()))
    ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity,log_window)
    imp_out = output_image_maker(img, ip_list)
    imp_out.show()



