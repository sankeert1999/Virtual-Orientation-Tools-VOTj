// Display a welcome message with instructions
showMessage("Annotation Tool", "<html>"
+"<h2>Welcome to the Annotation Tool</h2>"
+"This tool allows you to annotate your images and create binary masks for objects of interest."
+"<br><br>"
+"<h4>Instructions:</h4>"
+"<ul>"
+"<li>Input your image or image sequence (2D, 2D image sequence, 3D) and specify the output directory where you want to save the binary masks."
+"<li>Indicate the type of data you are annotating in the upcoming dialogue box."
+"<li>Use the white brush to draw over the objects of interest. If you make a mistake, you can undo with Ctrl+Z (limited to immediate undo)."
+"<li>For corrections, use the black brush to paint over mistakes and turn them black."
+"<li>Try to center your annotations over the objects of interest and cover them adequately."
+"<li>You can adjust the brush size by double-right-clicking on the  <span style='font-size:20px;'>&#128396</span> icon and entering the desired size."
+"</ul>"
+"<br>"
+"Once you are satisfied with your annotations, the tool will create a binary mask based on your annotations and save it to the destination you specified."
+"<br><br>"
+"Happy annotating!"
+"<br><br>"
+"The following project was part of a secondment under INFLANET consortium (under the Marie Sklodowska-Curie grant agreement No 955576)."
+"<br><br>@author: Sankeert Satheesan ACQUIFER Imaging GmbH Heidelberg, Germany<br>Contact:s.satheesan@acquifer.de/sankeert1999@gmail.com"
);

// User input for image type and output directory
#@ String (label="Specify the type of input image",choices={"2D", "3D","2D Image Sequence"}, style="radioButtonHorizontal") myChoice
#@ File (label="Select the output directory to save the binary mask", style="directory") outputDir

function annotateImage(stack){
	source = getTitle(); // Getting the source title of the imported image
	if (stack == 1){
		run("Apply LUT", "stack");
	}
	if (bitDepth() == 24){
		run("8-bit");		
	}
	run("Apply LUT");
	run("Colors...", "foreground=white background=black selection=yellow");
	setTool("Paintbrush Tool");
	waitForUser("Annotate the set of images, depicting the object of interest. Complete the stack and press okay");
	run("Colors...", "foreground=black background=black selection=yellow");
	waitForUser("Revisit your annotations, rectify your mistakes");
	run("Colors...", "foreground=white background=black selection=yellow");
}

// Function to process the image
function processImage() {    	
	getHistogram(values, counts,256);
	maxValue = values[0];
	// Loop through the array to find the maximum value	
	for (i = 1; i < values.length; i++) {
    	if (values[i] > maxValue) {
        	maxValue = values[i];
    	}
	}
	if (bitDepth() == 8){
		setThreshold(maxValue, 255, "raw");		
	}
	if (bitDepth() == 16){
		setThreshold(maxValue, 65535, "raw");		
	}
	if (bitDepth() == 32){
		setThreshold(maxValue, 1000000000000000000000000000000.0000, "raw");		
	}
	
	run("Convert to Mask", "background=Dark only"); 
}

// Process based on user choice
if (myChoice == "3D"){
	stack = 1;
	annotateImage(stack);
	nSlice = nSlices();
	// Loop through each slice
	for (slice = 1; slice <= nSlice; slice++) {
    	// Select the current slice
    	setSlice(slice);
		processImage();
	}
	saveAs("Tiff",outputDir+File.separator+source);
}

if (myChoice == "2D"){
	stack = 0;
	annotateImage(stack);
	saveAs("Tiff",outputDir+File.separator+source);	

}

if (myChoice == "2D Image Sequence"){
	stack = 1;
	annotateImage(stack);
	nSlice = nSlices();
	// Loop through each slice
	for (slice = 1; slice <= nSlice; slice++) {
    	// Select the current slice
    	setSlice(slice);
		processImage();
	}
	run("Image Sequence... ", "select="+outputDir+" format=TIFF use");
}

close("*");
print("You have done your part");
