from skimage import exposure
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import mpl_toolkits.axes_grid1.anchored_artists as mpl_aa

import mp4_video_generation.fun_figs as ff
import mp4_video_generation.fun_misc as fun_misc

def enhance_contrast_img_stack(img, d_contrast):
    """"
    Enhances the contrast of an image stack (numpy array)
    """
    if 'set_contrast_based_on_percentiles' in d_contrast:
        set_contrast_based_on_percentiles = d_contrast['set_contrast_based_on_percentiles']
    else:
        set_contrast_based_on_percentiles = False
    if 'set_contrast_based_on_pixel_values' in d_contrast:
        
        set_contrast_based_on_pixel_values = d_contrast['set_contrast_based_on_pixel_values']
    else:
        set_contrast_based_on_pixel_values = False
    if set_contrast_based_on_percentiles:  
        if 'p' in d_contrast:
            p_min, p_max = d_contrast['p']
        else:
            p_min = 2
            p_max = 98
        lim_min = np.percentile(img, p_min)
        lim_max = np.percentile(img, p_max)        
        print(f'\tEnhancing contrast and brightness based on percentiles:\nlower: {p_min}% ({lim_min}),\nupper: {p_max}% ({lim_max})')
        in_range  = (lim_min, lim_max)
        img = exposure.rescale_intensity(img, in_range=in_range, out_range='uint8')
    elif set_contrast_based_on_pixel_values:
        if 'lims' in d_contrast:
            lim_min, lim_max = d_contrast['lims']
            print(f'\tEnhancing contrast and brightness based on limits: {lim_min}, {lim_max}')
            in_range  = (lim_min, lim_max)
            img = exposure.rescale_intensity(img, in_range=in_range, out_range='uint8')
        else:
            raise ValueError('Could not find the pixel value limits (lims) in dictionary')
    else:
        print('\tEnhancing contrast and brightness')
        img = exposure.rescale_intensity(img, out_range='uint8')
    return img

def add_text_stack(img_stack, txt='', text_x_pos=20, text_y_pos=30, text_color='white', font_size=19, alignment='left'):
    """[Adds text to an entire image stack]

    Args:
        img_stack ([3D numpy array]): [Image stack]
        txt (str, optional): [text string to add]. Defaults to ''.
        text_y_pos (int, optional): [Text position in y-direction]. Defaults to 30.

    Returns:
        img_stack [3D numpy array]: [The image stack with an added text]
    """
    #Add text for every frame of the image stack
    for i in range(0,len(img_stack)):
        img_stack[i] = add_text(img_stack[i], txt, text_x_pos=text_x_pos, text_y_pos=text_y_pos, text_color=text_color, font_size=font_size, alignment=alignment)
    return img_stack

def add_text(img, txt='', text_x_pos=20, text_y_pos=30, text_color='white', font_size=19, alignment='left'):
    """Add text to a numpy array"""

    #Rescale the image to uint8 if the input data type is uint16
    if img.dtype == np.uint16:
        pil_img = Image.fromarray(ff.rescale_from_uint16_to_uint8(img))
    else:
        pil_img = Image.fromarray(img)

    # Call draw Method to add 2D graphics in an image
    drawer = ImageDraw.Draw(pil_img)

    #Get the good-looking font Sanspro regular. This font has to be downloaded separately and the directory of the font specified.
    font = get_font_sanspro_regular(font_size=font_size) #Get the good-looking font Sanspro regular. This font has to be downloaded separately and the directory of the font specified.

    #Get text color pixel value
    if text_color == 'white':
        text_pixel_value = 255 #color for the scale bar and the text, 255 = white
    elif text_color == 'black':
        text_pixel_value = 0 #color for the scale bar and the text, 255 = white
    else:
        raise ValueError('Wrong input of text_color, should be either white or black')

    if alignment == 'center':
        w_text, h_text = font.getsize(txt)
        # draw.text(((W-w)/2,(H-h)/2), msg, fill="black")
        # print(f'Center alignment, w_text = {w_text}, h_text = {h_text}')
        text_x_pos = text_x_pos - w_text/2
        text_y_pos = text_y_pos - h_text/2

    #Draw text
    if len(img.shape) == 3: #if RGB image
        drawer.text(xy=(text_x_pos, text_y_pos), text=txt, fill=((text_pixel_value,text_pixel_value,text_pixel_value)), font=font)
    else:
        drawer.text(xy=(text_x_pos, text_y_pos),  text=txt, fill=text_pixel_value, font=font)
    img_stack = np.array(pil_img) #Convert to an unsigned 8-bit integer numpy array
    return img_stack

def get_font_sanspro_regular(main_dir='', font_size=19):
    # """[Get the good-looking font Sanspro regular. This font has to be downloaded separately and the directory of the font specified.]

    # Args:
    #     main_dir (str, optional): [The OS path of the font]. Defaults to ''.

    # Returns:
    #     font [ImageFont]: [font SourceSansPro-Regular]
    # """
    #Get the path of the font
    main_path = os.path.normpath(main_dir)
    # if os.getcwd() == main_path:
    #     base_dir = main_path
    # elif os.path.dirname(os.getcwd()) == main_path:
    #     base_dir = os.path.dirname(os.getcwd())
    dir_utils = os.path.join(main_path, 'utils')
    path_font = os.path.join(dir_utils, 'SourceSansPro-Regular.ttf')
    if os.path.exists(path_font):        
        font = ImageFont.truetype(font=path_font, size=font_size)
    else:
        print(f'Cound not find the path to the font SourceSansPro-Regular: \n{path_font}')
        font = ImageFont.load_default()  
    return font

def add_timestamp(img_stack, fps, pad=41, text_x_pos=20, text_y_pos=-1, text_color='white', font_size=19, nbr_of_decimals=1, d_timestamp={}):
    """[Add timestamp to numpy stack]

    Args:
        img_stack ([3D numpy array]): [Image stack]
        fps ([type]): [Frame rate of the original video]
        pad (int, optional): [Padding from the bottom image border]. Defaults to 41.
        text_x_pos (int, optional): [Text position in x-direction]. Defaults to 20.

    Returns:
        img_stack [3D numpy array]: [The image stack with a timestamp]
    """
    if img_stack.dtype != np.uint8:
        print(f'Wrong datatype of the input image stack ({img_stack.dtype}), it should be np.uint8, rescaling...')
        img_stack = ff.rescale_from_uint16_to_uint8(img_stack)

    if text_y_pos == -1:
        h = img_stack.shape[1] #Height of the image
        text_y_pos = h-pad #position of the text in the y-direction
    if 'text_y_pos' in d_timestamp:
        text_y_pos = d_timestamp['text_y_pos']
    #Add timestamp for every frame of the image stack
    for i in range(0,len(img_stack)):
        t_sec = i/fps #Time in seconds
        txt = f'{t_sec:.{nbr_of_decimals}f} s' #text to add
        img_stack[i] = add_text(img_stack[i], txt, text_x_pos=text_x_pos, text_y_pos=text_y_pos, text_color=text_color, font_size=font_size)
    return img_stack

def add_scalebar_in_place_stack(img_stack, mag, camera_pixel_width, draw_text=True, text_color='white', d_scalebar={}):
    """[Adds a scale bar to a 3D numpy array]

    Args:
        img_stack ([3D numpy array]): [Image stack]
        mag ([str]): [Magnification, e.g. 100x]
        camera_pixel_width ([float]): [Camera Pixel width in microns]

    Returns:
        img_stack [3D numpy array]: [The image stack with added scale bar]
    """
    if img_stack.dtype != np.uint8:
        print(f'Wrong datatype of the input image stack ({img_stack.dtype}), it should be np.uint8, rescaling...')
        img_stack = ff.rescale_from_uint16_to_uint8(img_stack)

    print(f'\t - Adding scale bar to stack, mag. = {mag}, pixel width = {camera_pixel_width} um')
    for i in range(0,len(img_stack)):
        img_stack[i] = add_scalebar_in_place(img_stack[i], 
                                             mag, 
                                             camera_pixel_width, 
                                             draw_text=draw_text, 
                                             text_color=text_color, 
                                             d_scalebar=d_scalebar)
    return img_stack

def add_scalebar_in_place(img, 
                          mag, 
                          camera_pixel_width=16, 
                          draw_text=True, 
                          text_color='white', 
                          width_um_overwrite=-1, 
                          height_overwrite=-1, 
                          position='lower_right_corner', 
                          d_scalebar={}):
    """[Adds a scale bar to a 2D numpy array. 
    Note that you need to download the font SourceSansPro-Regular.ttf in order to run it]

    Args:
        img ([numpy array]): [2D]
        mag ([str]): [Magnification, e.g. 100x]
        camera_pixel_width ([float]): [Camera Pixel width in microns]

    Returns:
        img [uint8 numpy array]: [description]
    """
    if img.dtype != np.uint8:
        print(f'Wrong datatype of the input image ({img.dtype}), it should be np.uint8, rescaling...')
        img = ff.rescale_from_uint16_to_uint8(img)
    if camera_pixel_width < 0:
        raise ValueError(f'Wrong camera pixel width ({camera_pixel_width}), it should be larger than 0')

    im = img.copy()

    if text_color == 'white':
        text_pixel_value = 255 #color for the scale bar and the text, 255 = white
    elif text_color == 'black':
        text_pixel_value = 0 #color for the scale bar and the text, 255 = white
    else:
        raise ValueError('Wrong input of text_color, should be either white or black')

    mag_nbr = int(mag.split('x')[0]) #Extract the value of the magnification (e.g. 100 from the string 100x)
    #Default options
    height = 6 # scale bar height
    pad_text = 40
    pad_y = 15 # padding from the bottom image border for the scale bar
    pad_x = 15
    font_size = 30
    width_factor = 1
    # Set the width and height and text padding of the scale bar (pre-set values that seem good)
    if mag_nbr == 100:
        width_um = 10 
        height = 6    
        pad_text = 10
        pad_y = 10 # padding from the bottom image border for the scale bar
        pad_x = 5
        size_vertical = 2
        font_size = 19
    elif mag_nbr == 60:
        width_um = 10
    elif mag_nbr == 40:
        width_um = 20
        pad_x = 40
        pad_y = 15
        width_factor = 1.25
    elif mag_nbr == 20:
        width_um = 50
    elif mag_nbr == 10:
        width_um = 100
        height = 6 # scale bar height
        pad_text = 30 #40
        pad_y = 15 # padding from the bottom image border for the scale bar
        pad_x = 15
        size_vertical = 4
        font_size = 20 #30
    elif mag_nbr == 4:
        width_um = 500  
        font_size = 20
        pad_text = 30
        height = 4 # scale bar height
        width_factor = 0.75
    elif mag_nbr == 2:
        width_um = 500  
        font_size = 20
        pad_text = 7
        height = 4 # scale bar height
        width_factor = 1
    else:
        raise ValueError(f'Incorrect input of magnification ({mag})')

    #Overwrite variables
    if 'pad_y' in d_scalebar:
        pad_y = d_scalebar['pad_y']
    if 'pad_x' in d_scalebar:
        pad_x = d_scalebar['pad_x']
    if 'width_um' in d_scalebar:
        width_um = d_scalebar['width_um']
    if 'width_factor' in d_scalebar:
        width_factor = d_scalebar['width_factor']
    if 'fontsize' in d_scalebar:
        font_size = d_scalebar['fontsize']
    if 'pad_text' in d_scalebar:
        pad_text = d_scalebar['pad_text']
    if width_um_overwrite > 0:
        width_um = width_um_overwrite
    if height_overwrite > 0:
        height = height_overwrite
    # print('pad_x: ', pad_x)
    if width_um < 1000:
        label=f'{width_um}'+u' \u03BCm' #scale bar label, it should be mu for microns
    else:
        label=f'{int(np.round(width_um/1000))}'+u' mm' #scale bar label, it should be mu for microns
    #Calculate width of the scale bar
    scale_um_per_pixel = mag_nbr/camera_pixel_width
    width_pix = width_um*scale_um_per_pixel
    width_pix = int(width_pix) #Round to an integer

    img_h = img.shape[0]
    img_w = img.shape[1]
    if position == 'lower_right_corner':
        # print(f'\tScale bar position: lower right corner, mag = {mag_nbr},  pad = {pad}')
        x1 = -pad_x-width_pix
        x2 = -pad_x
        # x_text = img_w-pad_x-width_pix*width_factor
    elif position == 'lower_left_corner':
        print('\tScale bar position: lower left corner')        
        x1 = pad_x
        x2 = pad_x+width_pix
        # x_text = pad_x+(x2-x1)*0.2#+width_pix*0.5*width_factor
    
    if x1 < 0:
        x1 = img_w + x1    
    if x2 < 0:
        x2 = img_w + x2    
    x_text = x1 + (x2-x1)*0.5    
    # print(f'x1: {x1}, x2: {x2}, x_text: {x_text}')
    y1 = img_h-height-pad_y
    y2 = img_h-pad_y
    if len(img.shape) == 2: #2d images grayscale
        # Draw scale bar
        # print(f'Drawing scale bar, x:{x1}-{x2},y: {y1}-{y2}')
        # print(f'mag:{mag}, img_w: {img_w}, img_h:{img_h}\npad_x: {pad_x}, pad_y: {pad_y}\nheight:{height}, width:{width_pix}')
        img[y1:y2, x1:x2] = text_pixel_value
    elif len(img.shape) == 3: #2d images grayscale    
        # Draw scale bar
        img[y1:y2, x1:x2,:] = text_pixel_value
    else: #3D images grayscale
         raise ValueError(f'Incorrect shape of image. it should be 2D and not  {len(im.shape)}D')

    if draw_text:
        # Draw the text using PIL
        pil_img = Image.fromarray(img)
        drawer = ImageDraw.Draw(pil_img)
        font = get_font_sanspro_regular(font_size=font_size) #Get the good-looking font Sanspro regular. This font has to be downloaded separately and the directory of the font specified.
        # font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        if len(img.shape) == 2:
            drawer_fill = text_pixel_value
        if len(img.shape) == 3:
            drawer_fill = (text_pixel_value,text_pixel_value,text_pixel_value)
        drawer.text(
            xy=(x_text, y1-pad_text),
            text=label, fill=drawer_fill,
            font=font, align='center', anchor='ms',
        )                
        np_img = np.array(pil_img, dtype=np.uint8) #Convert to an unsigned 8-bit integer numpy array
        return np_img
    else:
        return img

def add_scalebar(axis, len_in_pixels, label=None, position='upper right',
                 color='white', frameon=False, pad=.3, size_vertical=2, **kwargs):
    """
    Written by Wouter Duverger, see https://github.com/wduverger/
    Adds scalebar to a matplotlib plot with sensible default values """

    axis.add_artist(mpl_aa.AnchoredSizeBar(
        axis.transData, len_in_pixels, label, position, color=color,
        frameon=frameon, size_vertical=size_vertical, pad=pad,
        **kwargs
    ))

def add_pressure_vector_to_stack(img_stack,dic_p, text_y_pos=30):
    """[Add a label of the pressure difference in mbar to the image stack]

    Args:
        img_stack ([3D numpy array]): [Image stack]
        dic_p ([dictionary]): [A dictionary containing a verctor of the pressure values ('p') and a vector containing the time in frames]
        text_y_pos (int, optional): [Text position in y-direction]. Defaults to 30.

    Raises:
        ValueError: [description]

    Returns:
        img_stack [3D numpy array]: [The image stack with added pressure values]
    """
    if not dic_p:
        raise ValueError('The dictionary containing the pressure and time vectors is empty.')
    p_vector = dic_p['p'] #pressure vector
    t_frames = dic_p['t_pix'] #time vector

    #Iterate every frame of the image-stack and add the pressure label
    for i in range(0,len(img_stack)):
        inx = fun_misc.find_nearest(t_frames,i)
        p = p_vector[inx]
        txt = f'{int(p)} mbar'
        img_stack[i] = add_text(img_stack[i], txt, text_y_pos=text_y_pos)
    return img_stack