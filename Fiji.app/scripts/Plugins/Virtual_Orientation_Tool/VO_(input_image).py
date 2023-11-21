#@PrefService prefs 
from fiji.util.gui import GenericDialogPlus
Win = GenericDialogPlus("Virtual Orientation Toolbar")
Win.addImageChoice("Select the image file", prefs.get("Image","Choice")) 
Win.addImageChoice("Select the mask file", prefs.get("Mask", "Choice")) 
Win.addChoice("Tasks", ["Centering", "Rotation","Centering+Rotation"], prefs.get("Tasks","Centering+Rotation"))
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
Win.addChoice("Center_Of_Rotation", ["Object_center", "Image_center"], prefs.get("Center_Of_Rotation","Image_center"))
Win.addChoice("Enlarge", ["Yes", "No"], prefs.get("Enlarge","No")) 
Win.addChoice("Object_Polarity", ["None", "Left-Right/Top-Bottom", "Right-Left/Bottom-Top"], prefs.get("Object_Polarity","None"))
# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:
Cite paper""") 

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
    enlarge = Win.getNextChoice()
    object_polarity = Win.getNextChoice()
    prefs.put("Image", img.getTitle()) 
    prefs.put("Mask", mask.getTitle()) 
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Enlarge", enlarge)
    prefs.put("Object_Polarity", object_polarity)



    from VOT_Utils import process_input_img,output_image_maker
	
    ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity)
    imp_out = output_image_maker(img, ip_list)
    imp_out.show()



