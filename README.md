# Virtual Orienation Tool FIJI
This tool is designed to center and align objects of interest both horizontally and vertically from their base orientation. It requires an input image and a corresponding mask that defines the object of interest within the image.
This tool is adapted at aligning a single object in each image, and this alignment can seamlessly propagate across multiple channels in the case of multichannel images. 
It offers compatibility across a wide range of image types, including 2D, 3D, 4D, and 5D data.
![Intro Image](https://github.com/sankeert1999/Virtual_orienation_tool_FIJI/blob/main/VOT.png)
# Tool Overview
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
  - ### Centering
    This task involves recognizing the object of interest, and calculates its center, followed by aligning it to the image center.
  - ### Rotation
    This task involves recognizing the object of interest, determines its center and base orientation, and then calculates the necessary rotation angle to align it with either the horizontal or vertical axis, as prompted by the user. The image is then rotated accordingly.
  - ### Centering+Rotation
    This task involves recognizing the object of interest, calculating its center, aligning the image to the center, determining the base orientation of the object, and calculating the rotation angle required to align it with the horizontal or vertical axis, as specified by the user. Subsequently, the image is rotated to achieve this alignment.

