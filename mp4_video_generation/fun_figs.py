import time
import math
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from skimage import exposure

def transform_img(img, angle=0, transform_mode='rot90', fillcolor=None):
    """
    Transforms an image by rotation

    img (np.array, uint8)
    Bilinear rotation of image
    angle: in degrees, counter-clockwise
    
    Note: quite slow as I rotate frame by frame in a for loop using PIL. Might be a faster way with Open CV. 
    However, I did not find a way to perform bilinear or bicubic interpolation with it.
    """
    if transform_mode == 'rot90':
        raise ValueError('This mode (rot90) has not been tested')
    elif transform_mode == 'flipHor':
        raise ValueError('This mode (flipHor) has not been tested')
    if not math.isnan(angle) or angle == 0:
        print(f'\tRotating the image {angle} degrees counter-clockwise')
        tic = time.perf_counter()
        #Rotating frame by frame...
        if len(img.shape) == 2:
            n_frames = 1
            img1 = Image.fromarray(img) #Convert to a PIL Image from a numpy array (must be 8-bit unsigned)
            img1 = img1.rotate(angle, resample=Image.BILINEAR, expand=True, translate=None, fillcolor=fillcolor) 
            img1 = np.array(img1) #Convert from a PIL Image to a numpy array
            img_rot = np.zeros([img1.shape[0], img1.shape[1]], dtype=np.uint8)
            img_rot[:,:] = img1               
        elif len(img.shape) == 3:
            n_frames = img.shape[0]
            img1 = Image.fromarray(img[0]) #Convert to a PIL Image from a numpy array (must be 8-bit unsigned)
            img1 = img1.rotate(angle, resample=Image.BILINEAR, expand=True, translate=None, fillcolor=fillcolor) 
            img1 = np.array(img1) #Convert from a PIL Image to a numpy array
            img_rot = np.zeros([n_frames, img1.shape[0], img1.shape[1]], dtype=np.uint8)
            for i in range(n_frames):            
                img1 = Image.fromarray(img[i]) #Convert to a PIL Image from a numpy array (must be 8-bit unsigned)
                img1 = img1.rotate(angle, resample=Image.BILINEAR, expand=True, translate=None, fillcolor=fillcolor) 
                img1 = np.array(img1) #Convert from a PIL Image to a numpy array
                img_rot[i] = img1
        elif len(img.shape) == 4:
            n_frames = img.shape[0]
            img1 = Image.fromarray(img[0]) #Convert to a PIL Image from a numpy array (must be 8-bit unsigned)
            img1 = img1.rotate(angle, resample=Image.BILINEAR, expand=True, translate=None, fillcolor=fillcolor) 
            img1 = np.array(img1) #Convert from a PIL Image to a numpy array
            img_rot = np.zeros([n_frames, img1.shape[0], img1.shape[1], img1.shape[2]], dtype=np.uint8)
            for i in range(n_frames):            
                img1 = Image.fromarray(img[i]) #Convert to a PIL Image from a numpy array (must be 8-bit unsigned)
                img1 = img1.rotate(angle, resample=Image.BILINEAR, expand=True, translate=None, fillcolor=fillcolor) 
                img1 = np.array(img1) #Convert from a PIL Image to a numpy array
                img_rot[i] = img1
        else:            
            raise ValueError(f'Wrong image shape: {img.shape}, len = {len(img.shape)}')
        toc = time.perf_counter()
        print(f'\t\tRotated {n_frames} frame(s) in {toc - tic:0.2f} seconds')
    return img_rot

def enlarge_img(img, enlargement=10):
    """ Enlarges image by a factor of enlargement"""

    if len(img.shape) == 3: #Grayscale image
        n,h,w = img.shape
        M = enlargement
        h2,w2 = h*M, w*M
        img2 = np.zeros([n,h2,w2]).astype(img.dtype)
        print(f'\tEnlarging image (x{enlargement}), from {h}x{w} to {h2}x{w2}')
        for i in range(n):
            for row in range(h):
                for col in range(w):
                    rows = np.arange(row*M,(row+2)*M)
                    cols = np.arange(col*M,(col+2)*M)
                    img2[i,rows[0]:rows[-1],cols[0]:cols[-1]] = img[i,row,col]

    elif len(img.shape) == 4: #Color image
        n,h,w,_ = img.shape
        M = enlargement
        h2,w2 = h*M, w*M
        img2 = np.zeros([n,h2,w2,3]).astype(img.dtype)
        print(f'\tEnlarging image, from {h}x{w} to {h2}x{w2}')
        for i in range(n):
            for row in range(h):
                for col in range(w):
                    rows = np.arange(row*M,(row+2)*M)
                    cols = np.arange(col*M,(col+2)*M)
                    img2[i,rows[0]:rows[-1],cols[0]:cols[-1],:] = img[i,row,col,:]
    else:
        raise ValueError('Incorrect number of dimensions')
    return img2

def calc_percentiles(img, min=2, max=98):
    """
    Calculates the percentiles of a numpy array.
    Parameters:
        img: numpy array
        min: the lower percentile
        max: the higher percentile
    """
    min_val = np.percentile(img,min)
    max_val = np.percentile(img,max)
    return min_val, max_val

def crop_image(img, crop_array_imageJ, color=False):
    """
    Crops a 3D-array according to the following (from ImageJ's homepage):
    Creates a rectangular selection, where x and y are
    the coordinates (in pixels) of the upper left corner
    of the selection. The origin (0,0) of the coordinate 
    system is the upper left corner of the image. 

    Format: x, y, width, height

    Args:
        img ([type]): [description]
        crop_array_imageJ ([type]): [description]

    Returns:
        [type]: [description]
    """
    if isinstance(crop_array_imageJ, list):
        crop_array_imageJ = np.array(crop_array_imageJ)
    if not np.all(crop_array_imageJ == 0):
        if len(img.shape) == 2:
            h_img = img.shape[0]
            w_img = img.shape[1]   
        elif len(img.shape) > 2:

            if color:
                h_img = img.shape[0]
                w_img = img.shape[1] 
            else:
                h_img = img.shape[1]
                w_img = img.shape[2] 
        x1 = crop_array_imageJ[0]
        width = crop_array_imageJ[2]
        x2 = x1 + width
        y1 = crop_array_imageJ[1]
        height = crop_array_imageJ[3]
        y2 = y1 + height
        print(f'\tCropping image according to: {crop_array_imageJ} x=({x1},{x2}), y = ({y1},{y2})')
        if height > h_img:
            raise Exception(f'The cropping rectangle height ({height}) cannot be larger than the image height ({h_img})!')
        if width > w_img:
            raise Exception(f'The cropping rectangle width ({width}) cannot be wider than the image width ({w_img})!')
        #print(f'\tImage w = {img.shape[2]}, h = {img.shape[1]}')
        #print(f'\tx = [{x1}, {x2}], y = [{y1}, {y2}]')    
        if len(img.shape) == 3:
            if color:
                return img[y1:y2, x1:x2,:]
            else:
                return img[:, y1:y2, x1:x2]

        elif len(img.shape) == 4:
            return img[:, y1:y2, x1:x2,:]
        else:
            return img[y1:y2, x1:x2]
    else:
        return img


def show_img(I, title_text = '', title='', cmap='gray', sz=10, fsz = 15, vmin=-1, vmax=-1, xlim=[-1,-1], ylim=[-1,-1], show_axis=False, p = [], I_lims=[], save_img=False, file_path='', ar = -1, add_colorbar = False, d_colorbar = {}):

    """
    Displays a 2D-array using matplotlib.pyplot with the axis off. 10x10 inches
    
    Colormaps I like are: "gray", "viridis", "inferno"
    For a selection of colormaps, see https://matplotlib.org/stable/tutorials/colors/colormaps.html
    """
    
    #width=10
    #height=10
    if len(p) > 0:
        I_lims = calc_percentiles(I, min=p[0], max=p[1])
        print(f'Enhancing contrast, percentiles = ({p[0]}, {p[1]})')
    if len(I_lims) > 0:        
        print(f'Intensity display limits: {I_lims[0]:.2f}, {I_lims[1]:.2f}')
        I = exposure.rescale_intensity(I.copy(), in_range=(I_lims[0], I_lims[1]), out_range='uint8')

    fig = plt.figure(figsize=(sz, sz))  # create a figure object
    ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure
    if not show_axis:
        ax.axis('off')
    if vmin >= 0 and vmax > 0:
        imgplot = ax.imshow(I, cmap=cmap, vmin=vmin, vmax=vmax) 
    else:
        imgplot = ax.imshow(I, cmap=cmap) 
    if len(title) > 0:
        plt.title(title, fontsize=fsz)
    elif len(title_text) > 0:
        plt.title(title_text, fontsize=fsz)
    if not ylim[-1] == -1:
        plt.ylim(ylim)
    if not xlim[-1] == -1:
        plt.xlim(xlim)
    # plt.style.use('general') 
    if ar > 0:
        ax.set_aspect(ar)
    if add_colorbar:
        add_color_bar(fig, ax, mappable=imgplot, **d_colorbar)
    if save_img:
        plt.savefig(file_path, bbox_inches="tight") #Save figure 
        print(f'Saved image to {file_path}')
    plt.show()   



def add_color_bar(fig, ax, mappable, position=[0.95, 0.3, 0.075, 0.4], ticks=[0, 0.5, 1], dic_colorbar={}, format='% 1.2f', yticklabels=[], labelsize=20, label='', labelpad=30):
    cax = plt.axes(position)
    # aspect = 20
    # pad_fraction = 0.5
    # # create an axes on the right side of ax. The width of cax will be 10%
    # # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    # divider = make_axes_locatable(ax)
    # width = axes_size.AxesY(ax, aspect=1./aspect)
    # pad = axes_size.Fraction(pad_fraction, width)
    # cax = divider.append_axes("right", size=width, pad=pad)
    kwargs_cbar = {
        'format':format,
        'orientation':'vertical',
    }
    if len(ticks) > 0:
        kwargs_cbar['ticks'] = ticks

    cbar = plt.colorbar(mappable, cax=cax, ax=ax, **kwargs_cbar)
    cbar.ax.tick_params(labelsize=labelsize) 

    if len(yticklabels) > 0:
        cbar.ax.set_yticklabels(yticklabels, fontsize=labelsize)  # vertically oriented colorbar

    # if 'label' in dic_colorbar:
    #     label = dic_colorbar['label']
    #     fontsize = 10
    #     cbar.set_label(label=label,size=fontsize)
    if len(label) > 0:
        cbar.set_label(label=label,size=labelsize, labelpad=labelpad)


def rescale_from_uint16_to_uint8(img):
    """
    Rescales a numpy array from uint16 to uint8
    """
    print(f'\tRescaling image {img.shape} from uint16 to uint8')
    if img.dtype != 'uint16':
        raise Exception(f'Data type should be be uint16 and not {img.dtype}...')
    return (img.astype(np.float32) * 255.999 / (2**16)).astype(np.uint8)
    