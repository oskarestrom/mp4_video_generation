#%%
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

file_path = r'C:\Users\os4875st\Dropbox\PhD Tegenfeldt\.py\waves projects_shared\mp4_video_generation\mp4_video_generation\example_video\DNA_moving.tif'
# Org path : E:\DNADLD_2022\T4_2022-06-15_2,3nguL\5mbar\100x_5mbar_out_013.nd2
#Read tif file
img = ti.read_tif_file(file_path, frame_range=[0,0], print_read=True)
frame_range = range(0,300) #frame range for the video
frame_range = [0,0] # if set to [0,0], all available frames will be used

settings = {
    # Basic settings
    'file_path_save' : 'example_video\DNA_moving_output.mp4', #path to save the video
    'frame_rate': 30.82, #frame rate of the video
    'playback_rate':3, #playback rate of the video. If set to -1, the playback rate will be the same as the frame rate 
    #'codex':'libx264', #codex used to save the video
    
    # Video Quality
    'crf':10, #crf used to save the video
    'preset':'slow', #preset used to save the video

    # Video settings
    'RGB_video':False, #is the video in color or not?

    # Contrast settings
    'enhance_contrast':True, #enhance contrast of the video
    'd_contrast':{ #dictionary of contrast settings. Choose basing the contrast settings between percentiles and pixel values
        'set_contrast_based_on_percentiles':True, #set contrast based on percentiles
        'p':np.array([0.1,99.9]), #percentiles used to set the contrast
        'set_contrast_based_on_pixel_values':False, #set contrast based on pixel values
        'lims':np.array([40,200]), #pixel values used to set the contrast
    }, #dictionary of contrast settings

    # General text settings
    'text_color':'white', #color of the text
    'font_size':19, #font size of the text
    'text_x_pos':80, #x position of the text

    # Video editing
    'remove_frames_to_achieve_frame_rate':-1, #remove frames to achieve the desired frame rate. If set to -1, no frames will be removed
    'mirror_image_after_rotation':False, #mirror image after rotation
    'enlarge_image':False, #enlarge image
    'final_size_2D':(), #final size of the image in 2D

    #Scale bar
    'add_scale_bar':True, #add scale bar to the video
    # 'd_scalebar':{ #dictionary of scale bar to add to the video
    #     'pad_y':0, #y padding of the scale bar to the image border
    #     'pad_x':0, #x padding of the scale bar to the image border
    #     'width_um':1, #width of the scale bar in microns
    #     'width_factor':1, #width of the scale bar in pixels
    #     'fontsize':19, #font size of the scale bar
    #     'pad_text':0, #padding of the text to the scale bar
    # }, 
    'mag':'100x', #magnification of the microscope used to acquire the video
    'camera_pixel_width':16, #camera pixel width in microns

    #Timestamp
    'add_timestamp':True, #add timestamp to the video
    'd_timestamp':{}, #dictionary of timestamp to add to the video
    'nbr_of_decimals_for_timestamp':1, #number of decimals for the timestamp

    #Pressure text
    'add_pressure_vector':False, #add pressure vector to the video
    # 'dic_p':{ #dictionary of pressure values
    #     'p':np.array([0,1,2,3,4,5,6,7,8,9,10]), #pressure vector
    #     't_pix':np.array([0,1,2,3,4,5,6,7,8,9,10]), #time vector
    # }, 
    #Extra text e.g. a title
    'd_extra_text':{}, #dictionary of extra text to add to the video
    'extra_text':'', #extra text to add to the video
    'extra_text_y_pos':0, #y position of the extra text
    'd_title_text_box':{}, #dictionary of title text box to add to the video
    'd_arrow':{ #dictionary of arrows to add to the video (see video for symmetry)
        'x':10, #x position of the arrow
        'p_video':200, #pressure value of the video in mbar
        'fontsize':19, #font size of the arrow text
    }, #dictionary of arrows to add to the video

    #Miscellaneous
    'return_img':False, #return the image instead of saving it

}


vid.save_as_mp4(img, settings)

#%%
