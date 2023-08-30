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

file_path = r'C:\Users\os4875st\Dropbox\PhD Tegenfeldt\.py\waves projects_shared\mp4_video_generation\DNA_moving.tif'
# Org path : E:\DNADLD_2022\T4_2022-06-15_2,3nguL\5mbar\100x_5mbar_out_013.nd2
#Read tif file
img = ti.read_tif_file(file_path, frame_range=[0,0], print_read=True)
frame_range = range(0,300) #frame range for the video
frame_range = [0,0] # if set to [0,0], all available frames will be used

settings = {
    # Basic settings
    'file_path_save' : r'C:\Users\os4875st\Dropbox\PhD Tegenfeldt\.py\waves projects_shared\mp4_video_generation\output_title.mp4', #path to save the video
    'frame_rate': 30.8, #frame rate of the video
    'playback_rate':5, #playback rate of the video. If set to -1, the playback rate will be the same as the frame rate 
    'frame_range':frame_range, #frame range for the video, if set to [0,0], all available frames will be used
    # Video Quality
    'crf':10, #crf used to save the video
    'preset':'slow', #preset used to save the video

    # Contrast settings
    'enhance_contrast':True, #enhance contrast of the video

    # General text settings
    'text_color':'white', #color of the text

    #Scale bar
    'add_scale_bar':True, #add scale bar to the video
    'mag':'100x', #magnification of the microscope used to acquire the video
    'camera_pixel_width':16, #camera pixel width in microns

    #Timestamp
    'add_timestamp':True, #add timestamp to the video
    'nbr_of_decimals_for_timestamp':1, #number of decimals for the timestamp

    'd_title_text_box':{
        'h_box':50, #height of the black box
        'w_box':100, #width of the black box        
        'box_color':'black', #color of the box
        'padding_h':0, #horizontal padding of the text to the box
        'text':r'Single T4-DNA strands', #text to add to the video
        'text_color':'white', #color of the text
        'font_size':19, #font size of the text
    }, #dictionary of title text box to add to the video

}
vid.save_as_mp4(img, settings)

#%%
