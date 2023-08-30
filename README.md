# mp4_video_generation
While it is easy to save images in python into png or tiff, it is more difficult to save an image stack into a video format. Especially if you need to compress it as so often is required for scientific publication (usually with a maximum size limit of 5-20 MB). This package makes it easy to save image stacks in numpy arrays into mp4-files. Multiple features are included: timestamp, scale bar, text on the video, and adding several image stacks in parallel into a video.

## Generation of a mp4 movie

```python
import mp4_video_generation.tiff_image_manipulation as ti
import mp4_video_generation.video_handling as vid

#Set video file path
file_path = r'C:\Users\example_video\DNA_moving.tif'

#Read tif file
img = ti.read_tif_file(file_path, frame_range=[0,0], print_read=True)
frame_range = [0,0] # if set to [0,0], all available frames will be used

settings = {
    # Basic settings
    'file_path_save' : 'example_video\DNA_moving_output.mp4', #path to save the video
    'frame_rate': 30.82, #frame rate of the video [frames per second]
    'playback_rate':3, #playback rate of the video [frames per second]. If set to -1, the playback rate will be the same as the frame rate 
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

}
vid.save_as_mp4(img, settings)
```

## Extensive settings list
It is possible to modify the output movie in numerable ways. The settings dictionary below show all the possible options. See below for comments on each option.
```python
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
    'd_scalebar':{ #dictionary of scale bar to add to the video
        'pad_y':0, #y padding of the scale bar to the image border
        'pad_x':0, #x padding of the scale bar to the image border
        'width_um':1, #width of the scale bar in microns
        'width_factor':1, #width of the scale bar in pixels
        'fontsize':19, #font size of the scale bar
        'pad_text':0, #padding of the text to the scale bar
    }, 
    'mag':'100x', #magnification of the microscope used to acquire the video
    'camera_pixel_width':16, #camera pixel width in microns

    #Timestamp
    'add_timestamp':True, #add timestamp to the video
    'd_timestamp':{}, #dictionary of timestamp to add to the video
    'nbr_of_decimals_for_timestamp':1, #number of decimals for the timestamp

    #Pressure text
    'add_pressure_vector':False, #add pressure vector to the video
    'dic_p':{ #dictionary of pressure values
        'p':np.array([0,1,2,3,4,5,6,7,8,9,10]), #pressure vector
        't_pix':np.array([0,1,2,3,4,5,6,7,8,9,10]), #time vector
    }, 
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
```
### RGB (color) video
It is possible to use this script for color videos. Just set the 'RGB_video' to True.
```python
    # Video settings
    'RGB_video':False, #is the video in color or not?
```
## A note on the video settings
We can manipulate the quality and thus the size of the output video. Sometimes you want ultra-high resolution and can bear large videos. Other times you need to compress the video as much as possible while still maintaining a decent quality. We can play with the following parameters:

- Resolution (imge dimensions in x and y). Try to minimize as much as possible by cropping the video.
- Frame rate. We can remove frames if the video was recorded with an excessive frame rate.
- crf (int, optional): [Constant rate factor (CRF) which sets the quality of the output video. The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.]. Defaults to 10.
- preset  (str, optional): Speed to compression ratio. the slower the better compression, in princple, default is slow. Options:
    - ultrafast
    - superfast
    - veryfast
    - faster
    - fast
    - medium – default preset
    - slow
    - slower
    - veryslow 
- codex (str, optional): [Codex for writing the video]. Defaults to 'libx264'. For lower quality output (and very small videos), select DIVX or mpeg4. I have always used libx264 as I received errors for other codices. However, this is something one can play with.]
- pix_fmt (str, optional): [Pixel format. yuv420p for the highest compatibility, alternatively yuv444p]. Defaults to 'yuv420p'. Similar to codex, I do not change this, I keep to 'yuv420p']

Note that crf has to be above 10 and preset has to be slow or faster in order to play the video in powerpoint.
other options see [https://trac.ffmpeg.org/wiki/Encode/H.264](https://trac.ffmpeg.org/wiki/Encode/H.264)