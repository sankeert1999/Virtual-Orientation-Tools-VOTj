#@ File (label="Select the input directory", style="directory") inputDir	// User selects the input folder containing the BF Stacks
#@ File (label="Select the output directory with GFP stacks", style="directory") outputDir	// User selects the input folder containing the GFP Stacks
fileList = getFileList(inputDir);
for(i=0; i<fileList.length; i++) {
	if (endsWith(fileList[i], ".tif")) {	//Selecting Only the image files in the directroy  I am selecting only ".tif" specify the image type
		open(inputDir + File.separator + fileList[i]); 
		source=getTitle(); // Getting the src title of the imported image
		rename("BF"); // Renaming the BF stack to "BF"
		run("VO (Zebrafish Segmentation)", "input=BF tasks=Centering+Rotation orientation=Horizontal center_of_rotation=Image_center enlarge=No");
		outFileName = source + "Centering_Rotation"; 
		saveAs("Tiff",outputDir+File.separator+outFileName); //Saving cropped GFP stack for looking at single cell movements or for input into downstream processing such as CellPose
		close("*");
	}
}
		