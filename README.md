# Virtual Orienation Tool FIJI (VOTj)
This tool is designed to center and align objects of interest both horizontally and vertically from their base orientation. It requires an input image and a corresponding mask that defines the object of interest within the image.
This tool is adapted at aligning a single object in each image, and this alignment can seamlessly propagate across multiple channels in the case of multichannel images. 
It offers compatibility across a wide range of image types, including 2D, 3D, 4D, and 5D data.
![Intro Image](https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT.png)

# Virtual Orientation Tool Overview
The tool starts with a GUI asking for 
## Input image 
Input image to be aligned (compatibile across a wide range of image types, including 2D, 3D, 4D, and 5D data.)
## Mask 
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



## Tasks
After selecting the corresponding images the next step is to selecte the task which you want to perform with this tool.
<p align="center">
<img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_1.png" width="65%" height="65%">
  </p>
  
  - ### Centering
    This task involves recognizing the object of interest, and calculates its center, followed by aligning it to the image center.
  - ### Rotation
    This task involves recognizing the object of interest, determines its center and base orientation, and then calculates the necessary rotation angle to align it with either the horizontal or vertical axis, as prompted by the user. The image is then rotated accordingly.
  - ### Centering+Rotation
    This task involves recognizing the object of interest, calculating its center, aligning the image to the center, determining the base orientation of the object, and calculating the rotation angle required to align it with the horizontal or vertical axis, as specified by the user. Subsequently, the image is rotated to achieve this alignment.
## Orientation
 Desired orientation for aligning the object of interest. 
   - ### Horizontal
  - ### Vertical
<p align="center">
<img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_2.png" width="35%" height="35%">
  </p>
  An illustrative image demonstrating the same sample object centered and aligned in two distinct orientations.

    
## Center of rotation
 Users have the option to specify the rotation center. This feature proves valuable in scenarios when the **task is  rotation**. However, when the **task is centering** rotation becomes unnecessary, rendering this option redundant. Similarly, in cases of when the **task is centering+rotation**, where the object's center is aligned with the image center as the initial step, this option becomes redundant as well.  
   - ### Object center
   - ### Image center
 
## Enlarge image
User have teh option to enalrge the output image, enlarging the image serves the purpose by minimizing potential loss of critical information around the surrounding area near object of interest.
<p align="center">
<img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_3.png" width="40%" height="40%">
  </p>

# VOTj Modes
- ## VO (input image)
  In this specific operational mode of the VOTj tool, the user is prompted to select an input image (the image to be aligned) and an associated mask (image or 3D stack) that corresponds to the input image. The tool then proceeds to generate the output image after collecting essential alignment information from the user. [Virtual Orientation Tool Overview](#virtual-orientation-tool-overview)
<p align="center">
<img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_input_image.png" width="50%" height="50%">
  </p>
  
- ## VO (user annotation)
   In this specific operational mode of the VOTj tool, the user is prompted to annoate the object of interest and based on these annotations the input image is alingned.
  - ### Selecting the input image
    <p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_1.png" width="50%" height="50%">
      </p>
  - ### Selecting the annotation mode
    User would be prompted with a window to select the annotation mode (only for images with dimensionality > 3).
    There are two annoation mode Single-Slice-Annotation and Multi-Slice-Annotation.
    - #### **Single-Slice-Annotation**
      **Single-Slice-Annotation** is ideal when you want to align a single slice of your input image. This mode is useful in 
      various situations. For example, if you have a 3D stack with multiple Z slices and want to align the entire stack based 
      on a single annotated slice, this mode 
      allows you to annotate that specific slice (typically the most focused one).
    - #### **Multi-Slice Annotation**
      **Multi-Slice-Annotation**, on the other hand, allows you to annotate multiple slices to achieve image alignment. This 
      mode is beneficial when your image data is more complex. For instance, if you have a 5D stack containing 3 channels, 10 
      slices, and 20 timepoints, choosing 
      **Multi-Slice-Annotation** lets you select both the channel and the slice number to annotate across all timepoints. The 
      tool then aligns the image based on this comprehensive annotation across the specified slices, ensuring precise 
      alignment even in complex 5D datasets.

    These two annotation modes provide you with the flexibility to align images efficiently based on your specific image 
    characteristics and alignment requirements. In essence, through annotation, you create a mask file that guides the 
    alignment process. To better understand how to design your mask according to your input,[consult the following table](#mask), which outlines the different mask files expected by the tool for various input image scenarios.
<p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_2.png" width="50%" height="50%">
      </p>
      
  - ### Selecting appropriate Slice/Stack for annotation
    After selecting the appropriate annotation mode, the user will be prompted to choose the image or stack for annotation. Depending on whether you've chosen Single-Slice-Annotation or Multi-Slice-Annotation, the tool will guide you accordingly. For instance, if you have a 3D stack with multiple Z slices and opt for Single-Slice-Annotation mode, you will be prompted to select the specific Z slice you wish to annotate.
<p align="center">
    <img src="https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT_U_annot_3.png" width="50%" height="50%">
      </p>
     



