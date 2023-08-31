#Module: video_handling
#Version: 0.0
#Created: November 2021 by Oskar Ström
#Content: Functions to handle videos. Writing, reading, and displaying them.

#Dependencies:

#Public modules
import os
import time
import matplotlib.pyplot as plt
# from regex import D
from skimage import exposure
# import skvideo
# skvideo.setFFmpegPath(r'C:\Users\os4875st\Anaconda3\Lib\site-packages\skvideo\io')
import skvideo.io

import numpy as np
from PIL import Image, ImageDraw

#Personal modules
import mp4_video_generation.image_manipulation as image_manipulation
# import nd2_handling2
# import tiff_image_manipulation as ti
import mp4_video_generation.fun_figs as ff
import mp4_video_generation.fun_misc as fun_misc
from PIL import Image

def resize_img(img, resize=(360,480)):
    if len(img.shape) == 3: #Grayscale image
        n,h,w = img.shape
        h2 = resize[0]
        w2 = resize[1]
        h2_center = int(np.round(h2/2))
        img2 = np.zeros([n,h2,w2]).astype(img.dtype)
        print(f'Resizing image, from {h}x{w} to {h2}x{w2}')
        for i in range(n):
            img_2D = img[i]
            image = Image.fromarray(img_2D)
            image.thumbnail((480,360)) #width, height
            np_img = np.array(image, dtype=np.uint8) #Convert to an unsigned 8-bit integer numpy array
            h3,w3 = np_img.shape
            h_half = int(np.round(h3/2))
            y1 = h2_center-h_half
            y2 = h2_center+h_half+1
            img2[i,y1:y2,:] = np_img
    elif len(img.shape) == 4: #Color image
        5
        # n,h,w,_ = img.shape
        # M = -1
        # h2,w2 = h*M, w*M
        # img2 = np.zeros([n,h2,w2,3]).astype(img.dtype)
        # print(f'\tEnlarging image, from {h}x{w} to {h2}x{w2}')
        # for i in range(n):
        #     for row in range(h):
        #         for col in range(w):
        #             rows = np.arange(row*M,(row+2)*M)
        #             cols = np.arange(col*M,(col+2)*M)
        #             img2[i,rows[0]:rows[-1],cols[0]:cols[-1],:] = img[i,row,col,:]
    else:
        raise ValueError('Incorrect number of dimensions')
    return img2

def add_arrow_sinewave(img, p_vid, frame, x, y, length_max = 100):    
    p_max = np.max(p_vid)
    # print(p_vid, frame)
    p = p_vid[frame]
    length = length_max * p / p_max
    if length < 0:
        length = np.abs(length)
        x = x - length
    img = add_arrow(img,x,y, d = length, fillcolor='white', width=10)

    return img

def add_arrow(img,x,y, d = 30, fillcolor='white', width=10):
    x1 = x
    x2 = x + d
    if y > 0:
        y1 = y
        y2 = y
        shape = [(x1, y1), (x2, y2)] 
        # create line image
        pil_img = Image.fromarray(img)
        drawer = ImageDraw.Draw(pil_img)
        
        drawer.line(shape, fill = fillcolor, width = width)
        img = np.array(pil_img) #Convert to an unsigned 8-bit integer numpy array
    return img

def add_arrow_stack(img_stack, d_arrow):
    
    if 'x' in d_arrow:
        x = d_arrow['x']
    else:
        x = 10
    p_vid = d_arrow['p_vid']
    if 'add_arrow_sinewave' in d_arrow:
        add_arrow_sinewave_bool = d_arrow['add_arrow_sinewave']
    else:
        add_arrow_sinewave_bool = False 
    if not add_arrow_sinewave_bool:
        y_list = d_arrow['y_list']       
    for i in range(0,len(img_stack)):        
        if add_arrow_sinewave_bool:
            h = img_stack.shape[1] #Height of the image
            y = h-40
            x = 300
            img_stack[i] = add_arrow_sinewave(img_stack[i], p_vid, i, x, y, length_max = 100)

            font_size = d_arrow['fontsize']
            txt = f'{p_vid[i]:.0f} mbar'
            text_color = 'white'
            text_x_pos = x
            text_y_pos = h - 20
            img_stack[i] = image_manipulation.add_text(img_stack[i], txt, text_x_pos=text_x_pos, text_y_pos=text_y_pos, text_color=text_color, font_size=font_size, alignment='center')        
        else:
            y = y_list[i]
            img_stack[i] = add_arrow(img_stack[i],x,y)    
    return img_stack

def save_as_mp4(img, settings):
    """[Saves an image stack (grayscale) into mp4 at the destination 'path_out' with the default codex 'libx264']

    Args:
        img ([numpy array]): [description]
        settings ([dict]): [dictionary containing the settings for the video]
            frame_rate ([float]): [Frame rate of the original video]
            path_out ([os.path]): [File path to save the video]
            codex (str, optional): [Codex for writing the video]. Defaults to 'libx264'. For lower quality output (and very small videos), select DIVX or mpeg4]
            RGB_video (bool, optional): [Is the image stack in RGB (color)?]. Defaults to False.
            enhance_contrast (bool, optional): [Enhance the contrast]. Defaults to True.
            disp_first_frame (bool, optional): [Display the first frame to see the contrast/brightness outcome    ]. Defaults to False.
            camera_pixel_width (int, optional): [Camera pixel width in microns]. Defaults to 16.
            mag ([str]): [Magnification, e.g. 100x]
            playback_rate (int, optional): [Frame rate of the resulting video when being played]. Defaults to -1 which results in real-time playback rate.
            crf (int, optional): [Constant rate factor (CRF) which sets the quality of the output video. The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.]. Defaults to 10.
            preset (str, optional): [Speed to compression ratio. the slower the better compression, in princple, default is slow]. Defaults to 'slow'.
            dic_p (dict, optional): [Dictionary containing details of the pressure labeling]. Defaults to {}.
    """
    if not 'codex' in settings:
        settings['codex'] = 'libx264'
    if not 'RGB_video' in settings:
        settings['RGB_video'] = False
    if not 'file_path_save' in settings:
        raise ValueError('The file_path_save is not defined')
    if not 'frame_rate' in settings:
        raise ValueError('The framer rate is not defined')
    
    print(f"Creating video object (\n\t- Image shape: {img.shape}\n\t- data type: {img.dtype}\n\t- codex: {settings['codex']}\n\t- color: {settings['RGB_video']}\n\t- enhance contrast: {settings['enhance_contrast']}\n\t)")
    tic = time.perf_counter()

    #Range of frames to be included, if equal to [0,0], all available frames will be processed
    if not 'frame_range' in settings:
        settings['frame_range'] = [0,0]
    frame_range = settings['frame_range']
    if frame_range[-1] == 0:
        img = img.copy()
    else:
        img = img[frame_range,:,:].copy()

    #Sometimes the brightness and contrast is bad. Enhance it to make the video look nicer
    if 'enhance_contrast' in settings:
        if not 'd_contrast' in settings:
            settings['d_contrast'] = {}

        if settings['enhance_contrast']:       
            img = image_manipulation.enhance_contrast_img_stack(img, settings['d_contrast'])
        
    if 'mirror_image_after_rotation' in settings:
        if settings['mirror_image_after_rotation']:
            img = np.flip(img,2)

    if 'enlarge_image' in settings:
        if settings['enlarge_image']:        
            img = ff.enlarge_img(img, enlargement=10)

    if 'final_size_2D' in settings:
        if len(settings['final_size_2D']) > 0:
            img = enlarge_vid(img, settings)

    if 'd_title_text_box' in settings:
        if len(settings['d_title_text_box']) > 0:
            img = add_title_text_box(img, settings)

    if 'd_extra_text' in settings:
        if len(settings['d_extra_text']) > 0:
            img = add_extra_text(img, settings)

    if 'd_scalebar' in settings:
        if len(settings['d_scalebar']) > 0: #Add scale bar                         
            img = image_manipulation.add_scalebar_in_place_stack(img, 
                                                                 settings['d_scalebar'], 
                                                                 text_color=settings['text_color'])

    if 'd_pressure' in settings:
        if len(settings['d_pressure']) > 0: #Add pressure label (in mbar)
            img = image_manipulation.add_pressure_vector_to_stack(img,
                                                                  settings['d_pressure'])
    if 'd_arrow' in settings:
        if len(settings['d_arrow']) > 0:
            add_arrow_stack(img, settings['d_arrow'])

    if 'd_timestamp' in settings:
        if len(settings['d_timestamp']) > 0: #Add time stamp
            add_timestamp_to_vid(img, settings)

    if not 'return_img' in settings:
        settings['return_img'] = False

    if settings['return_img']:
        return img    
    else:
        #Display the first frame to see the contrast/brightness outcome    
        if 'disp_first_frame' in settings:
            if settings['disp_first_frame']:
                disp_first_frame_fun(img, settings)
            
        #If the playback rate has not been set (=-1), set it to the same as the frame rate (real time)
        if 'playback_rate' in settings:
            if settings['playback_rate'] == -1:
                settings['playback_rate'] = settings['frame_rate']

        if not 'frame_rate_final' in settings:
            settings['frame_rate_final'] = -1

        if settings['frame_rate_final'] != -1:
            img = remove_frames(img, settings['frame_rate'], settings['frame_rate_final'])
            settings['playback_rate'] = settings['frame_rate_final']

        extra_arg = {}
        if 'codex' in settings:
            extra_arg['codex'] = settings['codex']
        if 'crf' in settings:
            extra_arg['crf'] = settings['crf']
        if 'preset' in settings:
            extra_arg['preset'] = settings['preset']

        #Write video using scikit-video
        write_video_FFmpeg_skvideo(img, 
                                   settings['file_path_save'], 
                                   settings['playback_rate'], **extra_arg) #, codex=codex, pix_fmt=pix_fmt, crf=crf, preset=preset)

        #open the destination path folder    
        os.startfile(os.path.dirname(settings['file_path_save'])) 

        toc = time.perf_counter()
        n_frames = img.shape[0]
        print(f'\t- Created video object of {n_frames} {img.dtype} frame(s) to file '+os.path.basename(settings['file_path_save'])+f' in {toc - tic:0.1f} seconds')    
        print('== Finished writing video file ==')

def enlarge_vid(img, settings):
    """Enlarge video to final size"""
    n,h,w = img.shape
    h_final, w_final = settings['final_size_2D']
    n_enlargement = np.int(np.floor(w_final/w))        
    img = ff.enlarge_img(img, enlargement=n_enlargement)
    n,h,w = img.shape
    missing_rows = h_final - h   
    img2 = np.zeros([n,h+missing_rows,w],dtype=img.dtype)  
    img2[:,0:h,:] = img   
    return img2

def add_timestamp_to_vid(img, settings):
    """Add timestamp to video"""

    d_timestamp = settings['d_timestamp']
    if not 'd_scalebar' in settings:
        raise ValueError('The d_scalebar is not defined. It is needed for timestamp.')
    d_scalebar = settings['d_scalebar']
    mag = d_scalebar['mag']
    if 'pad_timestamp' in d_timestamp:
        pad_timestamp = d_timestamp['pad_timestamp']
    else:
        if mag == '4x':
            pad_timestamp = 30+6/2
        elif mag == '100x':
            pad_timestamp = 25
        elif mag == '10x':
            pad_timestamp = 70
        else:
            pad_timestamp = 41
    if 'font_size' in d_timestamp:
        font_size_timestamp = d_timestamp['font_size']
    else:
        font_size_timestamp = 19
    img = image_manipulation.add_timestamp(img, 
                                           settings['frame_rate'], 
                                           pad=pad_timestamp, 
                                           text_color=settings['text_color'], 
                                           nbr_of_decimals=d_timestamp['nbr_of_decimals_for_timestamp'], 
                                           font_size=font_size_timestamp, 
                                           d_timestamp=d_timestamp)

def add_extra_text(img, settings):
    d = settings['d_extra_text']

    img, extra_text_y_pos, font_size = add_box(img, settings['d_extra_text'])
    if extra_text_y_pos == -1:
        extra_text_y_pos = d['text_x_pos']

    img = image_manipulation.add_text_stack(img, 
                                             txt=d['text'], 
                                             text_x_pos=d['text_x_pos'], 
                                             text_y_pos=extra_text_y_pos, 
                                             text_color=settings['text_color'], 
                                             font_size=font_size)
    return img

def add_title_text_box(img, settings):
    d = settings['d_title_text_box']
    if len(d) > 0:
        
        if not 'extra_text_y_pos' in settings:
            settings['extra_text_y_pos'] = 30

        box_color = 'black'
        if 'h_box' in d:
            h_box = d['h_box']
        else:
            h_box = 60    
        if 'w_box' in d:
            w_box = d['w_box']
        else:
            w_box = 60    
        if 'box_color' in d:
            box_color = d['box_color']
        else:
            box_color = 'black' 

        if 'padding_h' in d:
            padding_h = d['padding_h']
        else:
            padding_h = 10 

        if 'text' in d:
            text = d['text']
        else:
            text = 'text'

        if 'text_color' in d:
            text_color = d['text_color']
        else:
            text_color = 'black'
        if 'font_size' in d:
            font_size = d['font_size']
        else:
            font_size = 20

        if len(img.shape) == 3: #Grayscale image   
            n,h_img,w_img = img.shape 
        elif len(img.shape) == 4: #Color image
            n,h_img,w_img,n_colors = img.shape

        w_half = int(np.round(w_img/2))
        if w_box == 'full':
            w_box = w_img
            x1 = 0
            x2 = w_img
        else:           
            w_box_half = int(np.round(w_box/2))
            x1 = w_half - w_box_half
            x2 = w_half + w_box_half

        y1 = padding_h
        y2 = padding_h + h_box

        print(f'Inserting title text box of height {h_box} and width {w_box}\nimg shape = {img.shape}\nimg dtype = {img.dtype}')

        if len(img.shape) == 3: #Grayscale image   
            img_box = np.zeros([n,h_box, w_box],dtype=img.dtype)
            if box_color == 'white':
                img_box = img_box + 255
            elif box_color == 'gray':
                img_box = img_box + 127
            img[:,y1:y2,x1:x2] = img_box


            # img_box[:,0:h_img,x1:x2] = img

        # elif len(img.shape) == 4: #Color image
        #     img2 = np.zeros([n,h_img+h_box,w_box, n_colors],dtype=img.dtype)
        #     if box_color == 'white':
        #         img2 = img2 + 255
        #     img2[:,0:h_img,:,:] = img 
        # y_shift_text = 15
        text_x_pos = w_half
        extra_text_y_pos = int(np.round((padding_h + h_box/2)))
        img = image_manipulation.add_text_stack(img, 
                                                txt=text, 
                                                text_x_pos=text_x_pos, 
                                                text_y_pos=extra_text_y_pos, 
                                                text_color=text_color, 
                                                font_size=font_size, 
                                                alignment='center')

    return img

def add_box(img, d_extra_text):

    if 'text_in_box_below' in d_extra_text:
        if d_extra_text['text_in_box_below'] == True:             
            if 'box_color' in d_extra_text:
                box_color = d_extra_text['box_color']
            else:
                box_color = 'black'
            if 'h_box' in d_extra_text:
                h_box = d_extra_text['h_box']
            else:
                h_box = 60
            print(f'Inserting black box of height {h_box}')
            if len(img.shape) == 3: #Grayscale image
                n,h,w = img.shape                    
                img2 = np.zeros([n,h+h_box,w],dtype=img.dtype)
                if box_color == 'white':
                    img2 = img2 + 255
                img2[:,0:h,:] = img
            elif len(img.shape) == 4: #Color image
                n,h,w,n_colors = img.shape
                img2 = np.zeros([n,h+h_box,w, n_colors],dtype=img.dtype)
                if box_color == 'white':
                    img2 = img2 + 255
                img2[:,0:h,:,:] = img   
            img = img2

            #Updated values
            h = img.shape[1]
            extra_text_y_pos = int(h - h_box)
    else: 
        extra_text_y_pos = -1        
    if 'font_size' in d_extra_text:
        font_size = d_extra_text['font_size']
    else:
        font_size = 15
    return img, extra_text_y_pos, font_size

def disp_first_frame_fun(img, settings):
    if 'frame_disp' in settings['d_contrast']:
        d_contrast = settings['d_contrast']
        frame_disp = d_contrast['frame_disp']
    else:
        frame_disp = 0
    
    print(f'\tDisplaying frame #{frame_disp}:')
    fig,ax = plt.subplots(figsize=(10,10))
    plt.imshow(img[frame_disp], vmin=0, vmax=255, cmap='gray')    
    plt.title(f'frame #{0}')
    ax.axis('off')
    plt.show()

def write_video_FFmpeg_skvideo(img, 
                               path_out, 
                               frame_rate, 
                               codex='libx264', 
                               pix_fmt='yuv420p', 
                               crf=10, 
                               preset='slow'):
    """[Writing a video file with Sci-kit image and FFmpeg codex]

    Args:
        img ([type]): [description]
        path_out ([type]): [description]
        frame_rate ([type]): [description
        codex (str, optional): [Codex for writing the video]. Defaults to 'libx264'. For lower quality output (and very small videos), select DIVX or mpeg4]
        pix_fmt (str, optional): [Pixel format. yuv420p for the highest compatibility, alternatively yuv444p]. Defaults to 'yuv420p'.]
        crf (int, optional): [Constant rate factor (CRF) which sets the quality of the output video. 
        The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.]. Defaults to 10.

        preset  (str, optional): Speed to compression ratio. the slower the better compression, in princple, default is slow
        # Options:
            # ultrafast
            # superfast
            # veryfast
            # faster
            # fast
            # medium – default preset
            # slow
            # slower
            # veryslow 

            Note that crf has to be above 10 and preset has to be slow or faster in order to play the video in powerpoint.
            other options see https://trac.ffmpeg.org/wiki/Encode/H.264
    """
    path_length_limit = 255
    if len(path_out) > path_length_limit:
        raise ValueError(f'The path length ({len(path_out)}) is too long (need to be lower than {path_length_limit})')

    if len(img.shape) == 3:
        n_frames,h,w = img.shape
    elif len(img.shape) == 4:
        print('image shape = ', img.shape)
        img = img.transpose(0,2,3,1)
        print('image shape after transpose = ', img.shape)
        n_frames,h,w,n_colors = img.shape

    #If the dimensions are uneven, set them to even. Otherwise FFMPEG will crash...
    if h%2 == 1:
        print(f'Warning: Dimensions of the image must be of even numbers: ({h},{w})... Adding a last black row....')
        newrow = np.zeros_like(img[:,0,:])
        img = np.insert(img,-1,newrow,axis=1)  
    if w%2 == 1:
        print(f'Warning: Dimensions of the image must be of even numbers: ({h},{w})... Adding a last black column....')
        newrow = np.zeros_like(img[:,:,0])
        img = np.insert(img,-1,newrow,axis=2)

    print(f'\t Writing video file with Scikit-video and FFmpeg\n\t- path: {path_out}\n\t- playback rate: {frame_rate} fps\n\t- image shape: {img.shape}\n\t- number of frames: {n_frames}\n\t- data type: {img.dtype}\n\t- total duration: {n_frames/frame_rate:.1f} s')

    if codex != 'mpeg4' and codex != 'libx264':
        raise ValueError(f'Wrong codex input: {codex}. It should be libx264, alternatively mpeg4 if you are ok with bad quality')

    if path_out[-4:] != '.mp4':
        raise ValueError('The file does not end with .mp4')

    #Set the output dictionary to the FFmpegWriter
    outputdict={   
        '-framerate': str(frame_rate),   
        '-vcodec': codex,  #use the libx264, h.264 codec, alternatives:  DIVX, mpeg4 
        '-pix_fmt': pix_fmt, #yuv420p for the highest compatibility, alternatively yuv444p
        '-crf': str(crf), #The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.
        '-preset':preset, #Speed to compression ratio. the slower the better compression, in princple, default is slow
        '-async': '1',
        '-vsync': '1'
        }

    #Set the FFmpegWriter
    writer = skvideo.io.FFmpegWriter(path_out, inputdict={
      '-r': str(frame_rate),
    }, outputdict=outputdict, verbosity=1) #

    #Print the output dictionary
    print('\nOutput settings to FFmpegWriter:')
    fun_misc.print_dic(outputdict)

    #Create the video file
    for i,frame in enumerate(img):
        writer.writeFrame(frame) # writing to a image array
    writer.close() #close the writer

    print('Finished writing video file')

# def save_to_vid_video_obj(v, 
#                         frame_range=[0,0], 
#                         codex='libx264', 
#                         playback_rate=-1, 
#                         settings_general={}, 
#                         RGB_video=False, 
#                         add_timestamp=True, 
#                         add_scale_bar=True, 
#                         enhance_contrast=True, 
#                         camera_pixel_width=16, 
#                         crf=10, preset='slow', 
#                         add_pressure_vector=False, 
#                         dic_p={}, 
#                         crop_imageJ=np.array([0]), 
#                         text_color='white', 
#                         d_vid_settings={}, 
#                         nbr_of_decimals_for_timestamp=1, 
#                         extra_text='', 
#                         extra_text_y_pos=30, 
#                         mirror_image_after_rotation=False, 
#                         file_name_label='', 
#                         d_extra_text={}, 
#                         add_image_file_name_to_video_file_name='True', 
#                         return_img=False, 
#                         show_img=True, 
#                         enlarge_image=False, 
#                         final_size_2D=(), 
#                         d_timestamp={}, 
#                         dir_save='', 
#                         file_name_full='',
#                         d_title_text_box={}, 
#                         d_scalebar={}, 
#                         d_arrow={},
#                         remove_frames_to_achieve_frame_rate=-1,):
    
#     """[Save the image of the video object to a video file]

  
#     Args:
#         v ([Video (class)]): [Video object]
#         frame_range (list, optional): [Range of frames to be included]. Defaults to [0,0] which results in all available frames.
#         codex (str, optional): [Codex for writing the video]. Defaults to 'libx264'.
#         playback_rate (int, optional): [Frame rate of the resulting video when being played]. Defaults to -1 which results in real-time playback rate.
#         settings_general (dict, optional): [Dictionary containing general settings]. Defaults to {}.
#         RGB_video (bool, optional): [Is the image stack in RGB (color)?]. Defaults to False.
#         add_timestamp (bool, optional): [Add timestamp to resulting video]. Defaults to True.
#         add_scale_bar (bool, optional): [Add scale bar to resulting video]. Defaults to True.
#         enhance_contrast (bool, optional): [Enhance the contrast]. Defaults to True.
#         camera_pixel_width (int, optional): [Camera pixel width in microns]. Defaults to 16.
#         crf (int, optional): [Constant rate factor (CRF) which sets the quality of the output video. The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, and 51 is worst quality possible.]. Defaults to 10.
#         preset (str, optional): [Speed to compression ratio. the slower the better compression, in princple, default is slow]. Defaults to 'slow'.
#         add_pressure_vector (bool, optional): [Add pressure label to video]. Defaults to False.
#         dic_p (dict, optional): [Dictionary containing details of the pressure labeling]. Defaults to {}.
#     """
    
#     #Add extra label to the output file name depending on the experiment type and analysis settings
#     str_extra = ''
#     if settings_general:
#         if 'mode_pixelation' in settings_general:
#             if settings_general['mode_pixelation'] != 'none':
#                 str_extra = settings_general['mode_pixelation']

#     #Range of frames to be included, if equal to [0,0], all available frames will be processed
#     if frame_range[-1] == 0:
#         img = v.img.copy()
#     else:
#         img = v.img[frame_range,:,:].copy()

#     #If the playback rate has not been set (=-1), set it to the same as the frame rate (real time)
#     if playback_rate == -1:
#         playback_rate = v.frame_rate

#     if len(file_name_full) == 0:
#         #Set save file path
#         if add_image_file_name_to_video_file_name:
#             file_name = v.file_name0
#         else:
#             file_name = ''
#         file_name_video = f'{file_name_label}_{str_extra}_{frame_range[0]}-{frame_range[-1]}_{file_name}_{playback_rate}fps.mp4'
#     else:
#         file_name_video = file_name_full
    
    
#     if len(dir_save) == 0:
#         dir_save = v.dir_video_files
#     path_out = os.path.join(dir_save,file_name_video)
    
#     #Crop image according to a rectangle coordinates in imageJ
#     print('crop_imagej: ',crop_imageJ)
#     if not crop_imageJ[-1] == 0:
#         img = ff.crop_image(img, crop_imageJ) 

#     #Save to video
#     img = save_as_mp4(img, v.frame_rate, path_out, codex=codex, RGB_video=RGB_video, enhance_contrast=enhance_contrast, disp_first_frame=True, add_scale_bar=add_scale_bar, camera_pixel_width=camera_pixel_width, mag=v.mag, add_timestamp=add_timestamp, playback_rate=playback_rate,crf=crf, preset=preset, add_pressure_vector=add_pressure_vector, dic_p=dic_p, text_color=text_color, d_vid_settings=d_vid_settings, nbr_of_decimals_for_timestamp=nbr_of_decimals_for_timestamp, extra_text=extra_text, extra_text_y_pos=extra_text_y_pos, mirror_image_after_rotation=mirror_image_after_rotation, d_extra_text=d_extra_text, return_img=return_img, enlarge_image=enlarge_image, final_size_2D=final_size_2D, d_timestamp=d_timestamp,d_title_text_box=d_title_text_box, d_scalebar=d_scalebar, d_arrow=d_arrow, remove_frames_to_achieve_frame_rate=remove_frames_to_achieve_frame_rate,)
    
#     if return_img:
#         if show_img:
#             ff.show_img(img[0],sz=3,cmap='gray')
#         return img

# def save_as_mp4_video_obj(dir_exp, 
#                           file_nbr, 
#                           frame_range=[0,0], 
#                           codex='libx264', 
#                           playback_rate=-1, 
#                           settings_general={}):
#     """[Save image stack as mp4]

#     Args:
#         dir_exp ([str]): [Path of the video file experiment]
#         file_nbr ([str]): [File number (Nikon NIS-elements microscopy GUI always gives each file in an experiment series a file number starting from 001)]
#         frame_range (list, optional): [Range of frames to be included]. Defaults to [0,0] which results in all available frames.
#         codex (str, optional): [Codex for writing the video]. Defaults to 'libx264'.
#         playback_rate (int, optional): [Frame rate of the resulting video when being played]. Defaults to -1 which results in real-time playback rate.
#     """
#     #Acquire the video object
#     v = nd2_handling2.get_Video(dir_exp, file_nbr, read_img_directly=True, frame_range = frame_range)

#     #Save the image of the video object to a video file
#     save_to_vid_video_obj(v, frame_range=frame_range, codex=codex, playback_rate=playback_rate, settings_general=settings_general)

# def load_and_merge_two_imgs(dir_path, file_nbr, frame_range, settings_get_video):
#     v = nd2_handling2.get_Video(dir_path, file_nbr, read_img_directly=True, frame_range = frame_range, settings_get_video=settings_get_video)
#     img1 = v.img
#     #Rotate image if it is specified in the settings
#     if len(settings_get_video) > 0:
#         if 'rot' in settings_get_video:
#             img1 = ff.transform_img(img1, angle=settings_get_video['rot'],transform_mode='rot')
#     settings_get_video2 = settings_get_video.copy()       
#     settings_get_video2['video_prefix'] = settings_get_video2['video_prefix2']
#     v2 = nd2_handling2.get_Video(dir_path, file_nbr, read_img_directly=True, frame_range = frame_range, settings_get_video=settings_get_video2)
#     img2 = v2.img
#     #Rotate image if it is specified in the settings
#     if len(settings_get_video) > 0:
#         if 'rot' in settings_get_video:
#             img2 = ff.transform_img(img2, angle=settings_get_video['rot'],transform_mode='rot')
#     img = np.transpose([img1, img2, np.zeros_like(img1)], (1, 2, 3, 0))
#     return v, img

# def concatenate_img_stacks(file_nbrs, dir_path, frame_range,show_imgs = False, add_text=True, text_y_pos = 30, settings_get_video={}, settings_general={}):
#     img_list = []
#     for file_nbr in file_nbrs:
#         if len(settings_get_video) > 0:
#             if 'mode' in settings_get_video:
#                 if settings_get_video['mode'] == 'merge_ch_red_green':
#                     v, img = load_and_merge_two_imgs(dir_path, file_nbr, frame_range, settings_get_video)
#                     photometric='rgb'
#         else:
#             v = nd2_handling2.get_Video(dir_path, file_nbr, read_img_directly=True, frame_range = frame_range, settings_get_video=settings_get_video)
#             img = v.img
#             if frame_range[-1] == 0:
#                 img = v.img
#             else:
#                 img = v.img[frame_range,:,:]

#             #Rotate image if it is specified in the settings
#             if len(settings_get_video) > 0:
#                 if 'rot' in settings_get_video:
#                     img = ff.transform_img(img, angle=settings_get_video['rot'],transform_mode='rot')
#             photometric='minisblack'
#             if settings_general:
#                 if settings_general['mode_pixelation'] == 'dead_zone':
#                     img = ff.enlarge_img(img, enlargement=10)
#         if add_text:
#             img = image_manipulation.add_text_stack(img, txt=f'{v.p} mbar', text_y_pos=text_y_pos)
#         img_list.append(img)
#     imgs = np.vstack(img_list)
#     print('shape = ',imgs.shape)
#     if add_text:
#         file_name = f'stack_{frame_range}-frames-each_text.tif'
#     else:
#         file_name = f'stack_{frame_range}-frames-each.tif'
#     file_path = os.path.join(dir_path, file_name)
#     ti.write_tif_file(file_path, imgs, photometric=photometric)
#     os.startfile(dir_path)

def remove_frames(img, frame_rate_vid, frame_rate_final):
    if frame_rate_vid > frame_rate_final:
        print(f'Removing frames to the frame rate is lowered from {frame_rate_vid} fps to {frame_rate_final} fps')
        r = frame_rate_vid / frame_rate_final
        n_frames = img.shape[0]
        n_frames_final = int(np.floor(n_frames / r))
        frames = np.linspace(0,n_frames-1,n_frames_final, dtype=int)
        img = img[frames,:,:]
    return img

def concatenate_img_stacks_from_np_arrays(list_settings, 
                                        list_imgs, 
                                        codex='libx264', 
                                        playback_rate=-1, 
                                        crf=10, 
                                        preset='slow', 
                                        merge_horizontally=False, 
                                        merge_vertically=False, 
                                        file_path_save = 'unlabeled.mp4',
                                        play_back_rates=[], 
                                        return_img=False,
                                        resize=(),
                                        frame_rate_final=-1,
                                        ):


    if len(play_back_rates) > 0:
        list_imgs = list_imgs.copy()
        img1 = list_imgs[0]
        img2 = list_imgs[1]
        n_img1 = img1.shape[0]
        n_img2 = img2.shape[0]
        print('n_img1: ', n_img1, 'n_img2: ', n_img2)
        pbr1 = play_back_rates[0]
        pbr2 = play_back_rates[1]        
        if  n_img1 > n_img2:
            k = int(round(pbr1/pbr2)) #Ratio between the play back speeds
            n_img2_new = int(round(n_img1/k))
            print('k = ',k)
            img2_new = np.zeros([n_img1, img2.shape[1], img2.shape[2],3], dtype=img2.dtype)
            #Duplicate each frame k times in the video with higher frame rate so the total number of frames is same for both videos
            for i in range(0,n_img2_new):
                img2_new[i*k:(i+1)*k,:,:,:] = np.tile(img2[i,:,:,:], (k,1,1,1))
        print(f'img1.shape: {img1.shape}, dtype: {img1.dtype},\nimg2.shape: {img2_new.shape}, dtype: {img2_new.dtype} (new)')
        list_imgs[1] = img2_new

        #Playback rate of the highest frame rate
        playback_rate = pbr1
    else:
        #If the playback rate has not been set (=-1), set it to the same as the frame rate (real time)
        if playback_rate == -1:
            playback_rate = list_settings[0]['playback_rate']

    if merge_horizontally:
        if len(list_imgs) > 2:
            img = list_imgs[0]
            for i in range(len(list_imgs)-1):                
                img = np.concatenate((img, list_imgs[i+1]), axis=2)
        elif len(list_imgs) == 2:
            img = np.concatenate((list_imgs[0], list_imgs[1]), axis=2)
        print(f'After merging the images horizontally:\n\timg.shape: {img.shape}, dtype: {img.dtype}')
    elif merge_vertically:
        img = np.concatenate((list_imgs[0], list_imgs[1]), axis=1)
        print(f'After merging the images vertically:\n\timg.shape: {img.shape}, dtype: {img.dtype}')
    else:
        img = np.vstack(list_imgs)

    print(f'\tDisplaying frame #{0}:')
    fig,ax = plt.subplots(figsize=(10,10))
    plt.imshow(img[0], vmin=0, vmax=255, cmap='gray')    
    plt.title(f'frame #{0}')
    ax.axis('off')
    plt.show()

    if len(resize) > 0:
        img = resize_img(img)
    if frame_rate_final != -1:
        img = remove_frames(img, list_settings[0]['frame_rate'], frame_rate_final)
        playback_rate = frame_rate_final
    toc = time.perf_counter()
    # n_frames = img.shape[0]
    # print(f'\t- Created video object of {n_frames} {img_stack.dtype} frame(s) to file '+os.path.basename(path_out)+f' in {toc - tic:0.1f} seconds')    
    print('== Finished writing video file ==')
    if return_img:
        ff.show_img(img[0],sz=3,cmap='gray')
        return img
    else:
        #Write video using scikit-video
        write_video_FFmpeg_skvideo(img, file_path_save, playback_rate, codex=codex,crf=crf, preset=preset)

        #open the destination path folder    
        os.startfile(os.path.dirname(file_path_save)) 

def concatenate_img_stacks_from_v_list(list_v, settings_general, frame_range, show_imgs = False, RGB_video=False, add_text=True, add_timestamp=True, text_y_pos = 30, settings_get_video={}, enhance_contrast=True, enhance_contrast_for_all_imgs_together=True, crop_imageJ=np.array([0]), text_color='white', add_pressure_vector=False,codex='libx264', playback_rate=-1, camera_pixel_width=16,crf=10, preset='slow', dic_p={}, d_vid_settings={}):
    """Concatenates videos from video objects from the list list_v. 
    
    Right now only black and white images.
    """
    text_extra_file_name = ''
    tic = time.perf_counter() #start time counting
    img_list = []
    if enhance_contrast_for_all_imgs_together:
        p = ff.calc_percentiles(list_v[-1].img, min=0.5, max=99.5)

    print('Concatenating image stacks into a video')
    for i,v in enumerate(list_v):
        print(f'\t{v.p} mbar ({i+1}/{len(list_v)})')
        # if len(settings_get_video) > 0:
        #     if 'mode' in settings_get_video:
        #         if settings_get_video['mode'] == 'merge_ch_red_green':
        #             v, img = load_and_merge_two_imgs(dir_path, file_nbr, frame_range, settings_get_video)
        #             photometric='rgb'
        # else:
        photometric='minisblack' #Black and white image, not color
        img = v.img

        #Rotate image if it is specified in the settings
        if len(settings_get_video) > 0:
            if 'rot' in settings_get_video:
                img = ff.transform_img(img, angle=settings_get_video['rot'],transform_mode='rot')
        
        #Set the frame range. If the last cell of the list is set to 0, the entire frame range is selected
        if frame_range[-1] == 0:
            img = v.img
        else:
            img = v.img[frame_range,:,:]    

        #Crop image according to a rectangle coordinates in imageJ
        if np.all(crop_imageJ) == 0:
            img = ff.crop_image(img, crop_imageJ) 

        if settings_general:
            #Enlarge image if small to make it look better when running the mp4-file
            if settings_general['mode_pixelation'] == 'dead_zone':
                img = ff.enlarge_img(img, enlargement=10)
                text_extra_file_name = 'pix_dead_zones_'
            
        #Sometimes the brightness and contrast is bad. Enhance it to make the video look nicer
        if enhance_contrast:
            print('\tEnhancing contrast and brightness')
            if enhance_contrast_for_all_imgs_together:
                img = exposure.rescale_intensity(img, in_range=(p[0], p[1]), out_range='uint8')
            else:
                img = exposure.rescale_intensity(img, out_range='uint8')
            
        if add_text:
            img = image_manipulation.add_text_stack(img, txt=f'{v.p} mbar', text_y_pos=text_y_pos, text_color=text_color)

        if add_timestamp:
            img = image_manipulation.add_timestamp(img, v.frame_rate, pad=41, text_color=text_color)
        img_list.append(img)

    #Concatenate images
    imgs = np.vstack(img_list)
    print('\tshape = ',imgs.shape)
    if add_text:
        file_name = f'{text_extra_file_name}_{frame_range}-frames-each_text_{v.file_name0}.mp4'
    else:
        file_name = f'{text_extra_file_name}_{frame_range}-frames-each_{v.file_name0}.mp4'
    
    #Create path for the video file
    dir_video_dir = os.path.join(v.dir_exp, 'video_mp4_seq')
    if not os.path.exists(dir_video_dir):
        os.mkdir(dir_video_dir)
    file_path = os.path.join(dir_video_dir, file_name)

    kwargs = {'playback_rate':-1, 
            'codex':'libx264',
            'crf':10,
            'preset':'slow',
            'add_timestamp':False, 
            'enhance_contrast':False, 
            'RGB_video': False,
            'text_color':text_color,
            'camera_pixel_width':16,            
            'mag':v.mag}

    #Save to file
    save_as_mp4(imgs, v.frame_rate, file_path, **kwargs)
    toc = time.perf_counter()
    print(f'Finished creating the concatenated video file in {toc - tic:0.2f} seconds')   

