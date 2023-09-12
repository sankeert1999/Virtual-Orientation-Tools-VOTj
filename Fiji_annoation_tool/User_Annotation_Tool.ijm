showMessage("Annotation Tool", "<html>"
+"<h2>Welcome to the Annotation Tool</h2>"
+"This tool allows you to annotate your images and create binary masks for objects of interest."
+"<br><br>"
+"<h4>Instructions:</h4>"
+"<ul>"
+"<li>Input your image or image sequence (2D, 2D image sequence, 3D) and specify the output directory where you want to save the binary masks."
+"<li>Select the appropriate annoation mode based on your input."
    +"<ul>"
    +"<li><strong>2D</strong> If you have a single image.</li>"
    +"<li><strong>2D Image Sequence</strong> If you input a folder of 2D images.</li>"
    +"<li><strong>	3D multi slice annotation </strong> If you input a stack (either Z or T as third dimension), and you need to annotate each slice of the stack.</li>"
    +"<li><strong>	3D single slice annotation </strong> If you input a stack (either Z or T as third dimension), and you need to annotate just one of slice in a stack</li>"
    +"</ul>"
+"</li>"
+"<li>Use the <strong>white brush</strong> to draw over the objects of interest. If you make a mistake, you can undo with Ctrl+Z (limited to immediate undo).</li>"
+"<li>For corrections, use the <strong>black brush</strong> to paint over mistakes and turn them black.</li>"
+"<li>Try to center your annotations over the objects of interest and cover them adequately.</li>"
+"<li>You can adjust the brush size by double-right-clicking on the <span style='font-size:20px;'>&#128396</span> icon and entering the desired size.</li>"
+"</ul>"
+"<br>"
+"Once you are satisfied with your annotations, the tool will create a binary mask based on your annotations and save it to the destination you specified."
+"<br><br>"
+"Happy annotating!"
+"<br><br>"
+"The following project was part of a secondment under INFLANET consortium (under the Marie Sklodowska-Curie grant agreement No 955576)."
+"<br><br>@author: Sankeert Satheesan ACQUIFER Imaging GmbH Heidelberg, Germany<br>Contact:sankeert.satheesan@bruker.de/sankeert1999@gmail.com"
);


// User input for image type and output directory
Dialog.create("Annoation Mode");
Dialog.addMessage("Select the appropriate annoation mode");
Dialog.addChoice("Type:", newArray("2D","2D Image Sequence","3D multi slice annotation","3D single slice annotation"));
Dialog.show();	
myChoice  = Dialog.getChoice();
outputDir  = getDirectory("Select the output directory to save the binary mask");
//print(outputDir)


function annoateImage(){
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
	setThreshold(maxValue, 255, "raw");
	run("Convert to Mask", "background=Dark only");
	if (myChoice == "2D"){	
		setOption("BlackBackground", true);
		run("Convert to Mask");
	}
	if (myChoice == "3D single slice annotation"){	
		setOption("BlackBackground", true);
		run("Convert to Mask");
	}
}

// Process based on user choice
if (myChoice == "3D multi slice annotation"){
	source = getTitle(); // Getting the source title of the imported image
	run("8-bit");
	nSlice = nSlices();
	annoateImage();
	// Loop through each slice
	for (slice = 1; slice <= nSlice; slice++) {
    	// Select the current slice
    	setSlice(slice);
		processImage();
	}
	saveAs("Tiff",outputDir+File.separator+source);
}

if (myChoice == "3D single slice annotation"){
	source = getTitle(); // Getting the source title of the imported image
	run("8-bit");
	nSlice = nSlices();
	setSlice((nSlice/2)+1);	
	annoateImage();
	run("Duplicate...", "use");
	close("\\Others");
	processImage();
	// Loop through each slice
	for (slice = 2; slice <= nSlice; slice++) {
    	// Select the current slice
		run("Duplicate...", "title=Duplicate_" + slice);
	}
	run("Images to Stack", "use");
	saveAs("Tiff",outputDir+File.separator+source);
	close("*");
}


if (myChoice == "2D"){
	source = getTitle(); // Getting the source title of the imported image
	run("8-bit");
	annoateImage();
	processImage();
	saveAs("Tiff",outputDir+File.separator+source);	
	close("*");
	print("You have done your part");
}

if (myChoice == "2D Image Sequence"){
	source = getTitle(); // Getting the source title of the imported image
	run("8-bit");
	nSlice = nSlices();
	annoateImage();
	// Loop through each slice
	for (slice = 1; slice <= nSlice; slice++) {
    	// Select the current slice
    	setSlice(slice);
		processImage();
	}
	run("Image Sequence... ", "select="+outputDir+" format=TIFF use");
	close("*");
	print("You have done your part");
}
close("*");
