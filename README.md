# Virtual Orientation Tool for FIJI (VOTj)
This tool is designed to center and align objects of interest both horizontally and vertically from their base orientation. It requires an input image and a corresponding mask that defines the object of interest within the image.
This tool is adapted at aligning a single object in each image, and this alignment can seamlessly propagate across multiple channels in the case of multichannel images. 
It offers compatibility across a wide range of image types, including 2D, 3D, 4D, and 5D data.
![Intro Image](https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT.png)


# VOTj Modes
The Virtual Orientation Tool for Fiji (VOTj) offers two distinct modes:
- ## Single Mode
  In this mode, users can orient a single image at a time. This mode provides two suboptions.
  - ### VOTj Direct User Input
    In this specific operational mode of the VOTj tool, the user is prompted to select an input image (the image to be aligned) and an associated mask (2D or 3D stack) that corresponds to       the input image. The tool then proceeds to generate the output image after collecting essential alignment information from the user.
    [GUI configuration overview](#VOTj-GUI-Overview)
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_input_image.png" width="50%" height="50%">
    </p>
  
  - ### VOTj Annotation Assisted Alignment
    In this specific operational mode of the VOTj tool, the user is prompted to annoate the object of interest and based on these annotations 
    the input image is alingned.
    - #### <ins> Selecting the input image </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_1.png" width="50%" height="50%">
    </p>
      
    - #### <ins> Selecting the annotation mode </ins>
      User would be prompted with a window to select the annotation mode (only for images with dimensionality > 3).
      There are two annoation mode Single-Slice-Annotation and Multi-Slice-Annotation.
      - ##### **Single-Slice-Annotation**
        **Single-Slice-Annotation** is ideal when you want to align a single slice of your input image. This mode is useful in 
        various situations. For example, if you have a 3D stack with multiple Z slices and want to align the entire stack based 
        on a single annotated slice, this mode 
        allows you to annotate that specific slice (typically the most focused one).
      - ##### **Multi-Slice Annotation**
        **Multi-Slice-Annotation**, on the other hand, allows you to annotate multiple slices to achieve image alignment. This 
        mode is beneficial when your image data is more complex. For instance, if you have a 5D stack containing 3 channels, 10 
        slices, and 20 timepoints, choosing 
        **Multi-Slice-Annotation** lets you select both the channel and the slice number to annotate across all timepoints. The 
        tool then aligns the image based on this comprehensive annotation across the specified slices, ensuring precise 
        alignment even in complex 5D datasets.

      These two annotation modes provide you with the flexibility to align images efficiently based on your specific image 
      characteristics and alignment requirements. In essence, through annotation, you create a mask file that guides the 
      alignment process. To better understand how to design your mask according to your input,[consult the following table](#Select-the-mask),which          outlines the different mask files expected by the tool for various input image scenarios.
      <p align="center">
      <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_2.png" width="50%" height="50%">
      </p>
      
    - #### <ins> Selecting appropriate Slice/Stack for annotation </ins>
      After selecting the appropriate annotation mode, the user will be prompted to choose the image or stack for annotation. Depending on 
      whether you've chosen **Single-Slice-Annotation** or **Multi-Slice-Annotation**, the tool will guide you accordingly. For instance, if 
      you have a 3D stack with multiple Z slices and opt for **Single-Slice-Annotation** mode, you will be prompted to select the specific Z 
      slice you wish to annotate.
      <p align="center">
      <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_3.png" width="50%" height="50%">
      </p>

    - #### <ins> Annotating the object of interest </ins> 
      Once you've selected the image for annotation, the tool will present the image or stack for annotation, and the paintbrush tool will be 
      automatically activated with a white color. To adjust the brush width, simply double-click on the paintbrush tool icon. It's important 
      to note that drawing on the image before confirming the width will make the annotation permanent and irreversible.
      Here are some tips for effective annotation:
        - When marking the object of interest, ensure it covers the orientation you want to align.
        - Try to position the annotation somewhat centered on the object of interest.
        - For multi-slice annotation, aim for a consistent drawing that doesn't drastically change across the stack, particularly at the 
          centers."
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
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_B_DUI.png" width="40%" height="40%">
    </p>

  - ### VOTj Batch Custom Macro
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_B_CM.png" width="40%" height="40%">
    </p>

  - ### VOTj Batch Annotation Assisted Alignment
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTj_B_AAA.png" width="40%" height="40%">
    </p> 


# VOTj GUI Overview

- ## Input Configuration
  - ### **Select the image** 
    Input image to be aligned (compatibile across a wide range of image types, including 2D, 3D, 4D, and 5D data.)
  - ### **Select the mask** 
    Corresponding mask file for the input image representing the object of interest within the image. The table below outlines the various scenarios in which this tool is compatible and the corresponding mask file expectations for the respective input files.
    | INPUT (C,Z,T) | INPUT IMAGE TYPE| Binary Mask | Output |
    |-----------------|-----------------|-----------------|-----------------|
    | C > 1, Z > 1, T > 1 |	5D | 2D/3D | HyperStack (5D) |
    | C > 1, Z > 1, T = 1 | 4D | 2D/3D | HyperStack (4D) |
    | C > 1, Z = 1, T = 1 |	3D | 2D | Stack (3D) |
    | C = 1, Z = 1, T = 1 |	2D | 2D | IMG (2D) |
    | C > 1, Z = 1, T > 1 |	4D | 2D/3D | HyperStack (4D) |
    | C = 1, Z = 1, T > 1 |	3D | 2D/3D | Stack (3D) |
    | C = 1, Z > 1, T > 1 |	4D | 2D/3D | HyperStack (4D) |
    | C = 1, Z > 1, T = 1 |	3D | 2D/3D | Stack (3D) |


- ## Object alignment settings
  - ### **Tasks**
    After selecting the corresponding images the next step is to selecte the task which you want to perform with this tool.
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_1.png" width="65%" height="65%">
    </p>

  - #### <ins> Move object to image-center </ins>
    This task involves recognizing the object of interest, and calculates its center, followed by aligning it to the image center.
  - #### <ins> Align object to desired orientation </ins>
    This task involves recognizing the object of interest, determines its center and base orientation, and then calculates the necessary rotation angle to align it with either the horizontal or vertical axis, as prompted by the user. The image is then rotated accordingly.
  - #### <ins> Center object and then align to orientation </ins>
    This task involves recognizing the object of interest, calculating its center, aligning the image to the center, determining the base orientation of the object, and calculating the rotation angle required to align it with the horizontal or vertical axis, as specified by the user. Subsequently, the image is rotated to achieve this alignment.
  - ### **Orientation**
    Desired orientation for aligning the object of interest. 
    - #### <ins> Horizontal </ins>
    - #### <ins> Vertical </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_2.png" width="35%" height="35%">
    </p>
    An illustrative image demonstrating the same sample object centered and aligned in two distinct orientations.


  - ### **Center of rotation**
    Users have the option to specify the rotation center. This feature proves valuable in scenarios when the **task is  rotation**. However, when the **task is centering** rotation becomes unnecessary, rendering this option redundant. Similarly, in cases of when the **task is centering+rotation**, where the object's center is aligned with the image center as the initial step, this option becomes redundant as well.  
    - #### <ins> Object center </ins>
    - #### <ins> Image center </ins>
  
  - ### **Alignment with object pointing to**
    This enables the user to configure the polarity of object of interest, allowing users to define the object's pointing direction. For asymmetrical objects, like a fish with a distinct head and tail, users can specify the desired orientation. For instance, while annotating, marking the head specifically introduces asymmetry in the mask (see the below figure), and the tool aligns the object accordingly with the polarity.
    - #### <ins> Any </ins>
    - #### <ins> Left (for horizontal)/Top (for vertical) </ins>
    - #### <ins> Right (for horizontal)/Bottom (for vertical) </ins>
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOTJ_orientation.png" width="50%" height="50%">
    </p>

  - ### **Fill background with**
    This enables the user to customize the background color by choosing from three options: black, white, and mean. The background color is applied to the alignment operation, and the user's selected color determines the background hue. The "mean" option utilizes the mean intensity of the image to fill the background, offering a unique approach to color customization based on the overall image intensity.
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
    Users can choose to generate a log file, including the center coordinates and orientation angle of the detected object.The orientation angle is the smallest angle needed to align the object with the user-defined axis, whether vertical or horizontal. This feature provides users with detailed insights into the processing results for enhanced analysis and documentation.  
   
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


     



