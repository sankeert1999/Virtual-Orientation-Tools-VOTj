#@PrefService prefs 
from ij import IJ, WindowManager
from ij.plugin.frame import RoiManager
from ij.plugin.filter import GaussianBlur, RankFilters
from ij.process import ImageProcessor
from ij.plugin import ImageCalculator,Duplicator, ImageInfo
from ij.measure import ResultsTable
from ij.plugin.filter import ParticleAnalyzer
from ij.gui import OvalRoi, Roi, WaitForUserDialog, GenericDialog
from ij.macro import MacroConstants  
from fiji.util.gui import GenericDialogPlus



### Create a graphical user interface (GUI) for Virtual Orientation Toolbar



    
Win = GenericDialogPlus("Virtual Orientation Toolbar") 
# Add an option for users to select an image. 
Win.addImageChoice("Input Image", prefs.get("Image","Choice")) 
# Display a message asking users to cite the paper if they use the plugin.
Win.addMessage("""If you use this plugin please cite:
Cite paper""") 
# Provide a link to the plugin's documentation on GitHub.
Win.addHelp("https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/README.md")  
Win.addChoice("Tasks", ["Centering", "Rotation","Centering+Rotation"], prefs.get("Tasks","Centering+Rotation"))
Win.addChoice("Orientation", ["Horizontal", "Vertical"], prefs.get("Orientation","Horizontal"))
Win.addChoice("Center_Of_Rotation", ["Object_center", "Image_center"], prefs.get("Center_Of_Rotation","Image_center"))
Win.addChoice("Enlarge", ["Yes", "No"], prefs.get("Enlarge","No")) 
Win.showDialog()
if Win.wasOKed():  
    img = Win.getNextImage() 
    task = Win.getNextChoice()
    orientation = Win.getNextChoice()
    center_of_rotation = Win.getNextChoice()
    enlarge = Win.getNextChoice()     
    prefs.put("Tasks", task)
    prefs.put("Orientation", orientation)
    prefs.put("Center_Of_Rotation", center_of_rotation)
    prefs.put("Enlarge", enlarge)



# Get the active image title and dimensions
roiMgr = RoiManager.getRoiManager()
roiMgr.reset()
imageWidth = img.getWidth()
imageHeight = img.getHeight()

# Set the background to black and foreground to white
IJ.run("Colors...", "foreground=white background=black selection=yellow")

# Create a duplicate image named "TEMP" and apply Gaussian blur and invert
temp = img.duplicate()
temp.setTitle("TEMP")
tempProcessor = temp.getProcessor()
tempProcessor.blurGaussian(50)
tempProcessor.invert()
# Perform image calculation to add the "IMG" and "TEMP" images and create a 32-bit result
calc = ImageCalculator()
result = calc.run("Add create 32-bit", img, temp)
#result.show()
rank_filters = RankFilters()

# Define the radius for the Mean filter
radius = 20  # Adjust the radius as needed

# Apply the Mean filter to the active image's processor
rank_filters.rank(result.getProcessor(), radius, RankFilters.MEAN)
#result.show()
# Set auto-threshold to convert the image to a binary mask
IJ.setAutoThreshold(result, "Default no-reset")
IJ.run(result, "Convert to Mask", "method=Default background=Dark calculate")

# Analyze particles in the binary mask with a size range from 10000 to infinity
rt = ResultsTable()
options = ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES | ParticleAnalyzer.ADD_TO_MANAGER | ParticleAnalyzer.SHOW_MASKS
pa = ParticleAnalyzer(options, ParticleAnalyzer.AREA, rt, float(10000), float('inf'), 0.0, 1.0)
pa.setHideOutputImage(True)
pa.analyze(result)
#resulting_mask = pa.getOutputImage()

# Get the number of detected ROIs (particles) in the ROI Manager

nROIs = roiMgr.getCount()
print(nROIs)

# Initialize an array to store distances between ROI centers and image center
distanceArray = [0] * nROIs

# Check if there are no ROIs detected
if nROIs == 0:
    # If there are no ROIs, create a new black image named "Mask" with dimensions 2048x2048
    IJ.newImage("Mask", "8-bit black", imageWidth, imageHeight, 1)
else:
    # Calculate distances between ROI centers and image center
    for i in range(nROIs):
        roiMgr.select(i)
        roi = roiMgr.getRoi(i)
        roiCenterX = roi.getRotationCenter().xpoints[0]
        roiCenterY = roi.getRotationCenter().ypoints[0]
        X = (imageWidth / 2) - roiCenterX
        Y = (imageHeight / 2) - roiCenterY
        distanceToCenter = ((X * X) + (Y * Y)) ** 0.5
        distanceArray[i] = distanceToCenter
        

    # Find the minimum distance and its index from the distanceArray
    minDistance = distanceArray[0]
    minDistanceIndex = 0
    for i in range(1, nROIs):
        if distanceArray[i] < minDistance:
            minDistance = distanceArray[i]
            minDistanceIndex = i

    # Select the ROI with the least distance to the image center
    roiMgr.select(minDistanceIndex)
    
    # Create a convex hull around the selected ROI
    IJ.run("Convex Hull")

    # Create a new black image named "Mask" with dimensions 2048x2048
    IJ.newImage("mask", "8-bit black", imageWidth, imageHeight, 1)
    
    # Restore the selection of the ROI and add it to the ROI Manager for the "Mask" image
    roiMgr.reset()
    IJ.run("Restore Selection")
    roiMgr.addRoi(roi)

    # Select the last ROI in the ROI Manager (the convex hull ROI)
    #lastRoiIndex = roiMgr.getCount() - 1
    #roiMgr.select(lastRoiIndex)
    
    # Fill the selected ROI to create a mask
    IJ.run("Fill")

    # Delete the last ROI (convex hull) from the ROI Manager
    roiMgr.runCommand("Delete")
    
mask=IJ.getImage()   
##Calling the utils file 
from VOT_Utils import process_input_img,output_image_maker
ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge)
imp_out = output_image_maker(img, ip_list)
imp_out.show()
imp_out.changes = True