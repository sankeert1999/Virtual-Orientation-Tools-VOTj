[![DOI](https://zenodo.org/badge/DOI/10.1186/s12859-020-3363-7.svg)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11193110/)

# Installation

- ## Via the Fiji updater
  Tick the __Virtual-Orientation-Tools-VOTj__ AND __IJ-OpenCV__ update site of the Fiji udpater.  
  A new entry will show up in the Plugin Menu (all the way down) after restarting Fiji.  
  See how to [activate an update site](https://imagej.net/How_to_follow_a_3rd_party_update_site).

- ## Manual installation
  You can also do a manual installation by copying the files in the right place. 
  - **Install Dependencies**: Open the Fiji updater and tick the IJ-OpenCV update site to install the necessary dependencies.
    
  - **Download Files**: Go to the main page above this README, click the green Code button, and select Download ZIP. Unzip the downloaded file.

  - **Merge Directories**: On Windows, drag the Fiji.app folder from the unzipped directory and drop it into the Fiji.app directory of your existing Fiji installation. This will merge both Fiji.app           
    directories,automatically copying the files into the corresponding subdirectories.

  - **Restart Fiji**: After merging the directories, restart Fiji.

  If the drag-and-drop method does not work, manually copy the files from the unzipped directory to the corresponding directories in your Fiji installation. If some directories (e.g., Lib in Fiji.app/jars)     do not exist, create them.

  

# Virtual Orientation Tool for FIJI (VOTj)
This tool is designed to center and align objects of interest both horizontally and vertically from their base orientation. It requires an input image and a corresponding mask that defines the object of interest within the image.
This tool is adapted at aligning a single object in each image, and this alignment can seamlessly propagate across multiple channels in the case of multichannel images. 
It offers compatibility across a wide range of image types, including 2D, 3D, 4D, and 5D data.

A video tutorial is available on YouTube [https://youtu.be/WHeDhn1Mnpc](https://youtu.be/WHeDhn1Mnpc)

![Intro Image](https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT.png)
- ## How does it work ?
  The tool primarily serves to determine the orientation of a given object, aligning it with the horizontal or vertical axis, and optionally centering the object. The process begins by detecting the object of interest from the provided binary mask, followed by identifying its center. To establish the object's orientation, the tool employs [Principal Component Analysis (PCA)](https://docs.opencv.org/4.5.3/d1/dee/tutorial_introduction_to_pca.html) on the contour of the detected object. 
  <p align="justify">
  This process yields two principal components, representing the eigenvectors that capture the data variance.The tool calculates the angle between these eigenvectors using the tanh function, providing the initial orientation angle. 
  
  To ensure alignment within the [-90, 90] range and accommodate small rotations, an additional step transforms the obtained angles into the final angle for alignment. For users choosing to orient the object vertically, an extra transformation step determines the respective alignment angle. 
  Refer to the table below for a detailed calculation of the alignment angle. Once the center and angle are established, the tool facilitates user-defined transformations, such as rotation or rotation with centering, etc. Notably, the tool accounts for object polarity, deduced from the mask. After alignment, a final step applies a flip operation to adjust object polarity based on user preferences.
  </p>
  <p align="center">
  <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_algo.png" width="50%" height="50%">
  </p>

  <p align="center">
  <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_small_angle_Table.png" width="50%" height="50%">
  </p>

# VOTj Modes
<p align="justify">
The Virtual Orientation Tool for Fiji (VOTj) offers two distinct modes:
</p>

- ## Single Mode
  <p align="justify">
  In this mode, users can orient a single image at a time. This mode provides two suboptions.
  </p>

  - ### VOTj Direct User Input
    <p align="justify">
    In this specific operational mode of the VOTj tool, the user is prompted to select an input image (the image to be aligned) and an associated mask (2D or 3D stack) that corresponds to the input image. 
    </p>

    The tool then proceeds to generate the output image after collecting essential alignment information from the user.[GUI configuration overview](#VOTj-GUI-Overview)
    
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_input_image.png" width="50%" height="50%">
    </p>
  
  - ### VOTj Annotation Assisted Alignment
    <p align="justify">
    In this specific operational mode of the VOTj tool, the user is prompted to annotate the object of interest and based on these annotations 
    the input image is aligned.
    </p>

    - #### <ins> Selecting the input image </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_1.png" width="50%" height="50%">
    </p>
      
    - #### <ins> Selecting the annotation mode </ins>
      <p align="justify">
      User would be prompted with a window to select the annotation mode (only for images with dimensionality > 3).
      There are two annoation mode Single-Slice-Annotation and Multi-Slice-Annotation.
      </p>

      - ##### **Single-Slice-Annotation**
        <p align="justify">
        This option lets you annotate a single slice (e.g of a Z-stack or multi-channel image) and the tool will align the full stack based on this single annotation.
        </p>

      - ##### **Multi-Slice Annotation**
        **Multi-Slice-Annotation**, on the other hand, allows you to annotate multiple slices, typically suited for timelapse where each timepoint is aligned separately (with any number of Z-slices and channels).A single slice in each timepoint
        is annotated (you choose which timepoint and Z-slice to use). The "substacks" (Z and/or multi-channel) at each timepoint are then 
        aligned separately based on this timepoint-specific annotation.  
      

      <p align="justify">
      These two annotation modes provide you with the flexibility to align images efficiently based on your specific image 
      characteristics and alignment requirements. In essence, through annotation, you create a mask file that guides the 
      alignment process. 
      </p>

      To better understand how to design your mask according to your input,[consult the following table](#Select-the-mask),which outlines the different mask files expected by the tool for various input image scenarios.

      <p align="center">
      <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_2.png" width="50%" height="50%">
      </p>
      
    - #### <ins> Selecting appropriate Slice/Stack for annotation </ins>
      After selecting the appropriate annotation mode, the user will be prompted to choose the image or stack for annotation. Depending on 
      whether you've chosen **Single-Slice-Annotation** or **Multi-Slice-Annotation**, the tool will guide you accordingly. For instance, if 
      you have a Z-stack and opt for **Single-Slice-Annotation** mode, you will be prompted to select the specific Z 
      slice you wish to annotate.
      

      <p align="center">
      <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_3.png" width="50%" height="50%">
      </p>

    - #### <ins> Annotating the object of interest </ins> 
      <p align="justify">
      Once you've selected the image for annotation, the tool will present the image or stack for annotation, and the paintbrush tool will be 
      automatically activated with a white color. To adjust the brush width, simply double-click on the paintbrush tool icon. It's important 
      to note that drawing on the image before confirming the width will make the annotation permanent and irreversible.
      Here are some tips for effective annotation:
      </p>

        - When marking the object of interest, ensure it covers the orientation you want to align.
        - Try to position the annotation somewhat centered on the object of interest.
        - For multi-slice annotation, aim for a consistent drawing that doesn't drastically change across the stack, particularly at the 
          centers."
        - To account for the polarity in the annoation refer here [Alignment with object pointing to](#Alignment-with-object-pointing-to).
      
      
      <p align="center">
      <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_4.png" width="80%" height="80%">
      </p>

    - #### <ins> Configuring the VOTj panel </ins>
      Now, the user is prompted to select the alignment operation they need for their image.[GUI configuration overview](#VOTj-GUI-Overview)
      <p align="center">
      <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_5.png" width="60%" height="60%">
      </p>

- ## Batch Mode
  Batch Mode allows users to batch process an entire folder of images. This mode provides three suboptions.
  - ### VOTj Batch Direct User Input
    This operational mode is a batch format of the [VOTj Direct User Input mode](#VOTj-Direct-User-Input)
    <p align="justify">
    The GUI initiates by requesting input configuration, where users specify the input image and its corresponding mask folder details. It is essential that the filenames of masks match those of the input images to avoid errors. 
    </p>

    The subsequent steps include configuring [object alignment settings](#Object-alignment-settings),[additional options](#Additional-options) and finally [output configuration](#Output-configuration). In the output configuration, users specify the destination folder for saving output images and choose the desired image format.
    
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_B_DUI.png" width="40%" height="40%">
    </p>

  - ### VOTj Batch Custom Macro
    <p align="justify">
    This operational mode allows users to process a folder of images, using a custom macro to generate masks for each input image and further orienting them.
    The GUI begins by prompting input configuration, where users specify image folder details and the macro folder. The macro should generate masks, with the final mask as the active image window.
    </p>

    Followed by configuring [object alignment settings](#Object-alignment-settings),[additional options](#Additional-options) and finally [output configuration](#Output-configuration).Users can save output images to a specified folder and opt to save corresponding masks in a "Mask_VOTj" subfolder. Users also have the flexibility to choose image and mask formats.

    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_B_CM.png" width="40%" height="40%">
    </p>

  - ### VOTj Batch Annotation Assisted Alignment
    This operational mode is a batch format of the [VOTj Annotation Assisted Alignment](#VOTj-Annotation-Assisted-Alignment).

    The GUI initiates by requesting input configuration, where users specify the input image. The subsequent steps include configuring [object alignment settings](#Object-alignment-settings),[additional options](#Additional-options) and finally [output configuration](#Output-configuration).Users can save output images to a specified folder and opt to save corresponding masks in a "Mask_VOTj" subfolder. Users also have the flexibility to choose image and mask formats. Following GUI configuration, proceed with the annotation procedure for each image, mirroring the process in [VOTj Annotation Assisted Alignment](#VOTj-Annotation-Assisted-Alignment).
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_B_AAA.png" width="40%" height="40%">
    </p> 


# VOTj GUI Overview

- ## Input Configuration
  - ### **Select the image** 
    Input image to be aligned (compatibile across a wide range of image types, including 2D, 3D, 4D, and 5D data.)
  - ### **Select the mask** 
    Corresponding mask file for the input image representing the object of interest within the image. The table below outlines the various scenarios in which this tool is compatible and the corresponding mask file expectations for the respective input files.

|INPUT IMAGE TYPE|BINARY MASK|
|:-------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------- |
| Single Plane (2D --> C = 1, Z = 1, T = 1) | <ins>**PLANE**</ins> (a single plane/2D with the mask)                                                                                      |
| Z-stack (3D --> C = 1, Z > 1, T = 1) | <ins>**PLANE**</ins> -> align all Z-slices identically / <ins>**STACK (Z-stack)** </ins> -> Align each Z-slice separately\* (1-to-1 between image and mask) |
| Timelapse (3D --> C = 1, Z = 1, T > 1) | <ins>**PLANE**</ins> -> align all timepoints identically / <ins>**STACK (timelapse)**</ins> -> Align each timepoint separately                             |
| Multi-channel (3D --> C > 1, Z = 1, T = 1) | <ins>**PLANE**</ins> only ->  align all channels indentically. The tool does not support separate alignment of channels |
| Multi-channel Z-stack (4D --> C > 1, Z > 1, T = 1) | <ins>**PLANE**</ins> -> align all slices identically / <ins>**STACK (Z-stack)**</ins> -> align Z-slices separately\*                                       |
| Multi-channel timelapse (4D --> C > 1, Z = 1, T > 1) | <ins>**PLANE**</ins> -> align all timepoints identically /  <ins>**STACK (timelapse)**</ins> to align each timepoint separately                            |
| Z-stack with timelapse (4D --> C = 1, Z > 1, T > 1) | <ins>**PLANE**</ins> -> align all slices identically / <ins>**STACK (timelapse)**</ins> : align Z-stack at each timepoint separately                       |
| Multi-channel, Z-stack and Timelapse (5D --> C > 1, Z > 1, T > 1) |<ins> **PLANE**</ins> -> align all slices identically / <ins>**STACK (timelapse)**</ins> : align stack at each timepoint separately                         |
<p align="justify">
\* Slices of a Z-stack should typically be aligned with the same transformation, as they were normally acquired with the same orientation.  
The option to align slices separately is rather here to adress the fact that timelapse are sometimes recognized as Z-stack in ImageJ.   
So you can still align each timepoint separately in that case with the tool, without having to swap dimensions first.  
</p> 

- ## Object alignment settings
  - ### **Tasks**
    After selecting the corresponding images the next step is to selecte the task which you want to perform with this tool.
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_1.png" width="65%" height="65%">
    </p>

  - #### <ins> Move object to image-center </ins>
    This task involves recognizing the object of interest, and calculates its center, followed by aligning it to the image center.
  - #### <ins> Align object to desired orientation </ins>
    <p align="justify">
    This task involves recognizing the object of interest, determines its center and base orientation, and then calculates the necessary rotation angle to align it with either the horizontal or vertical axis, as prompted by the user. The image is then rotated accordingly.
    </p>

  - #### <ins> Center object and then align to orientation </ins>
    <p align="justify">
    This task involves recognizing the object of interest, calculating its center, aligning the image to the center, determining the base orientation of the object, and calculating the rotation angle required to align it with the horizontal or vertical axis, as specified by the user. Subsequently, the image is rotated to achieve this alignment.
    </p>

  - ### **Orientation**
    Desired orientation for aligning the object of interest. 
    - #### <ins> Horizontal </ins>
    - #### <ins> Vertical </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_2.png" width="35%" height="35%">
    </p>
    An illustrative image demonstrating the same sample object centered and aligned in two distinct orientations.


  - ### **Center of rotation**
    Users have the option to specify the rotation center. This feature proves valuable in scenarios when the <ins>**task is  rotation**</ins>. However, when the <ins>**task is centering**</ins> rotation becomes unnecessary, rendering this option redundant. Similarly, in cases of when the <ins>**task is centering+rotation**</ins>, where the object's center is aligned with the image center as the initial step, this option becomes redundant as well.  
    - #### <ins> Object center </ins>
    - #### <ins> Image center </ins>
  
  - ### **Alignment with object pointing to**
    <p align="justify">
    This enables the user to configure the polarity of object of interest, allowing users to define the object's pointing direction. For asymmetrical objects, like a fish with a distinct head and tail, users can specify the desired orientation. For instance, while annotating, marking the head specifically introduces asymmetry in the mask (see the below figure), and the tool aligns the object accordingly with the polarity.
    </p>

    - #### <ins> Any </ins>
    - #### <ins> Left (for horizontal)/Top (for vertical) </ins>
    - #### <ins> Right (for horizontal)/Bottom (for vertical) </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTJ_orientation.png" width="50%" height="50%">
    </p>

  - ### **Fill background with**
    <p align="justify">
    This enables the user to customize the background color by choosing from three options: black, white, and mean. The background color is applied to the alignment operation, and the user's selected color determines the background hue. The "mean" option utilizes the mean intensity of the image to fill the background, offering a unique approach to color customization based on the overall image intensity.
    </p>

    - #### <ins> Black </ins>
    - #### <ins> White </ins>
    - #### <ins> Mean </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_background.png" width="50%" height="50%">
    </p>

- ## Additional options

  - ### **Enlarge image**
    User have the option to enalrge the output image, enlarging the image serves the purpose by minimizing potential loss of critical information around the surrounding area near object of interest.
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_3.png" width="40%" height="40%">
    </p>
  
  - ### **Log File Output**
    <p align="justify">
    Users can choose to generate a log file, including the center coordinates and orientation angle of the detected object.The orientation angle is the smallest angle needed to align the object with the user-defined axis, whether vertical or horizontal. This feature provides users with detailed insights into the processing results for enhanced analysis and documentation.  
    </p>
   
- ## Output configuration
    Exclusive for batch mode
    - ### **Save processed images/masks to**
      Users are prompted to provide the corresponding directory information indicating where they would like to save the output files generated.
    - ### **Save images in format**
      Users can choose the desired image format for saving the output image, with available options including TIFF (tif, tiff), JPEG (jpg, jpeg), PNG (png), and BMP (bmp).
    - ### **Save mask file**
      Users can simply check or uncheck a checkbox to indicate their preference for saving the mask file. If selected, the masks are stored in a folder named **Mask_VOTj** within the 
      specified 
      output directory in the option **Save processed images/masks to**.
    - ### **Save masks in format**
      Users can choose the desired image format for saving the masks, with available options including TIFF (tif, tiff), JPEG (jpg, jpeg), PNG (png), and BMP (bmp).


     



