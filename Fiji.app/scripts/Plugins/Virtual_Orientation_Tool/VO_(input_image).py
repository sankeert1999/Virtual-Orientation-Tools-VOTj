#@ ImagePlus (label="Select the image file") img 
#@ ImagePlus (label="Select the mask file") mask 
#@ String (choices={"Centering", "Rotation","Centering+Rotation"}, label = "Tasks", style="listBox") task
#@ String (choices={"Horizontal", "Vertical"}, label = "Orientation",style="listBox") orientation
#@ String (choices={"Object_center", "Image_center"}, label = "Center of rotation",style="radioButtonHorizontal") center_of_rotation 
#@ String (choices={"Yes", "No"}, label = "Enlarge Image",style="radioButtonHorizontal") enlarge
#@ String (choices={"None","Left-Right/Top-Bottom", "Right-Left/Bottom-Top"}, label = "Object_Polarity",style="listBox") object_polarity

from VOT_Utils import process_input_img,output_image_maker

ip_list = process_input_img(img, mask, task, orientation, center_of_rotation, enlarge,object_polarity)
imp_out = output_image_maker(img, ip_list)
imp_out.show()



