#%%
import os
import numpy as np
import importlib
import mp4_video_generation.video_handling as vid
import mp4_video_generation.fun_figs as ff
import mp4_video_generation.fun_misc as fun_misc
import mp4_video_generation.image_manipulation as image_manipulation
import mp4_video_generation.tiff_image_manipulation as ti
importlib.reload(vid)
importlib.reload(fun_misc)
importlib.reload(ff)
importlib.reload(image_manipulation)

base_path = r'C:\Users\os4875st\Dropbox\PhD Tegenfeldt\.py\waves projects_shared\mp4_video_generation'
file_path = os.path.join(base_path,r'DNA_moving.tif')# Org path : E:\DNADLD_2022\T4_2022-06-15_2,3nguL\5mbar\100x_5mbar_out_013.nd2
#Read tif file
img = ti.read_tif_file(file_path, frame_range=[0,0], print_read=True)
frame_range = [0,0] # if set to [0,0], all available frames will be used

crop_imageJ = ([255, 2, 189, 510])
img = ff.crop_image(img, crop_imageJ)


settings1 = {
    # Basic settings
    'file_path_save' : os.path.join(base_path,'output_contrast.mp4'), #path to save the video
    'frame_rate': 30.8, #frame rate of the video
    'playback_rate':15, #playback rate of the video. If set to -1, the playback rate will be the same as the frame rate 
    'frame_range':frame_range, #frame range for the video, if set to [0,0], all available frames will be used
    # Video Quality
    'crf':20, #crf used to save the video
    'preset':'fast', #preset used to save the video

    # Contrast settings
    'enhance_contrast':True, #enhance contrast of the video

    # General text settings
    'text_color':'white', #color of the text

    #Scale bar
    'd_scalebar':{ #dictionary of scale bar to add to the video
        'mag':'100x', #magnification of the microscope used to acquire the video
        'camera_pixel_width':16, #camera pixel width in microns
    }, 
    #Timestamp    
    'd_timestamp':{
        'nbr_of_decimals_for_timestamp':1, #number of decimals for the timestamp
        'pad_timestamp_y':10, #y padding of the timestamp to the image border
        'font_size':19, #font size of the timestamp
        'text_y_pos':10, #y position of the timestamp
        'text_x_pos':10, #y position of the timestamp
    }, #dictionary of timestamp to add to the video

    'return_img':True,#return the image with the text and scale bar added

}
img1 = vid.save_as_mp4(img, settings1)

settings2 = {
    # Basic settings
    'file_path_save' : os.path.join(base_path,'output_contrast.mp4'), #path to save the video
    'frame_rate': 30.8, #frame rate of the video
    'playback_rate':15, #playback rate of the video. If set to -1, the playback rate will be the same as the frame rate 
    'frame_range':frame_range, #frame range for the video, if set to [0,0], all available frames will be used
    # Video Quality
    'crf':20, #crf used to save the video
    'preset':'fast', #preset used to save the video

    # Contrast settings
    'enhance_contrast':True, #enhance contrast of the video
    'd_contrast':{ #dictionary of contrast settings. Choose basing the contrast settings between percentiles and pixel values
        'set_contrast_based_on_pixel_values':True, #set contrast based on pixel values
        'lims':np.array([190,255]), #pixel values used to set the contrast
    }, #dictionary of contrast settings

    # General text settings
    'text_color':'white', #color of the text

    #Scale bar
    'd_scalebar':{ #dictionary of scale bar to add to the video
        'mag':'100x', #magnification of the microscope used to acquire the video
        'camera_pixel_width':16, #camera pixel width in microns
    }, 
    #Timestamp    
    'd_timestamp':{
        'nbr_of_decimals_for_timestamp':1, #number of decimals for the timestamp
        'pad_timestamp_y':10, #y padding of the timestamp to the image border
        'font_size':19, #font size of the timestamp
        'text_y_pos':10, #y position of the timestamp
        'text_x_pos':10, #y position of the timestamp
    }, #dictionary of timestamp to add to the video

    'return_img':True,#return the image with the text and scale bar added

}
img2 = vid.save_as_mp4(img, settings2)

#%%

importlib.reload(vid)
importlib.reload(image_manipulation)
list_settings = [settings1, settings2]
list_imgs = [img1, img2]
kwargs = {
        'file_path_save' : os.path.join(base_path,'output_concat.mp4'), #path to save the video
        'playback_rate':15, 
        'crf':10, # The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.]
        'preset':'slow',
        'merge_horizontally':True,
        'merge_vertically':False,
        }
vid.concatenate_img_stacks_from_np_arrays(list_settings, 
                                                      list_imgs, 
                                                      **kwargs)
#%%

importlib.reload(vid)
importlib.reload(image_manipulation)
list_settings = [settings1, settings2]
list_imgs = [img1, img2]
dir_save = r'C:\Users\os4875st\Dropbox\PhD Tegenfeldt\Projects\Oskar All\Paper - DNA DLD\manuscript DNA DLD\Micromachines submission\ESI movies'
kwargs = {
        'file_path_save' : os.path.join(base_path,'output_concat_time.mp4'), #path to save the video
        'playback_rate':60, 
        # #Compression
        # 'crf':23, # The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.]
        'merge_horizontally':False,
        'merge_vertically':False,
        'return_img':False
        }
img_low_u = vid.concatenate_img_stacks_from_np_arrays(list_settings, 
                                                      list_imgs, 
                                                      **kwargs)
#%%