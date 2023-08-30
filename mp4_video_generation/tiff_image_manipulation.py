import tifffile
import numpy as np
import os
import time

def read_tif_file(file_path, frame_range=[0,0], print_read=True):
    """[summary]

    Args:
        file_path ([type]): [description]
        frame_range (list, optional): [description]. Defaults to [0,0].

    Returns:
        [type]: [description]
    """
    tic = time.perf_counter()
    if not os.path.isfile(file_path):
        raise ValueError(f'The file does not exist: ({file_path})')
    # str_split = file_path.split('\\')
    # file_name = str_split[-1]
    # folder_name = str_split[-2]
    folder_name = os.path.dirname(file_path) #The directory path of the file
    file_name = os.path.basename(file_path)
    if not np.any(frame_range):
        n_frames = 'all'
    else:
        n_frames = len(frame_range)
        # n_frames = frame_range[-1] - frame_range[0] + 1
    if print_read:
        if isinstance(n_frames, str):
            print(f'\tReading {n_frames} frames ({frame_range[0]}-{frame_range[-1]}) file {file_name} in folder {folder_name}')
        else:
            if n_frames > 5:
                    print(f'\tReading {n_frames} frames ({frame_range[0]}-{frame_range[-1]}) file {file_name} in folder {folder_name}')
            else:
                print(f'\tReading {n_frames} frames from file {file_name} in folder {folder_name}:')
                for f in frame_range: print('\t'+f'#{f}')
    #If the selected frames to read are all set to 0, read the full range in all dimensions. Otherwise, read only the selected range of dimensions.
    if not np.any(frame_range):
        img = tifffile.imread(file_path)
    else:
        img = tifffile.imread(file_path, key=frame_range)
    toc = time.perf_counter()
    if len(img.shape) == 2:
        n_frames = 1
    elif len(img.shape) == 3:
        n_frames = img.shape[0]
    elif len(img.shape) == 4:
        n_frames = img.shape[0]
    else:
        ValueError('Loaded image is of the wrong number of dimensions')
        n_frames = -1
    if print_read:
        print(f'\t\tRead {n_frames} {img.dtype} frame(s) from '+file_name+f' in {toc - tic:0.2f} seconds')    
    return img

def write_tif_file(file_path, img, photometric='minisblack'):
    """[summary]

    Args:
        file_path ([type]): [description]
        img ([type]): [description]
        photometric (str, optional): [description]. Defaults to 'minisblack'. Could also be 'rgb'
    """
    # str_split = file_path.split('\\')
    # file_name = str_split[-1]
    # folder_name = str_split[-2]
    dir_file = os.path.dirname(file_path) #The directory path of the file
    file_name = os.path.basename(file_path)
    if len(file_name) > 95:
        raise ValueError('The filename is too long.')
    if (len(img.shape) == 3) or (len(img.shape) == 4):
        n_frames = img.shape[0]
    elif len(img.shape) == 2:
        n_frames = 1
    else:
        raise ValueError('Loaded image is of the wrong number of dimensions')
    print(f'\tWriting {n_frames} {img.dtype} frame(s) to '+file_name+' in folder '+dir_file) 
    tifffile.imwrite(file_path, img, photometric=photometric)