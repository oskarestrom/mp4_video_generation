#%%
import os
import numpy as np
import matplotlib.pyplot as plt
import tifffile
from skimage import exposure

import importlib
import mp4_video_generation.video_handling as vid
import mp4_video_generation.fun_figs as ff
import mp4_video_generation.fun_misc as fun_misc
import mp4_video_generation.image_manipulation as image_manipulation
import mp4_video_generation.tiff_image_manipulation as ti
importlib.reload(vid)
importlib.reload(fun_misc)
importlib.reload(ff)

#Set the path to the tif file
base_path = r'C:\Users\os4875st\Dropbox\PhD Tegenfeldt\.py\waves projects_shared\mp4_video_generation'
file_path = os.path.join(base_path,r'raw.tif')# Org path : E:\DNADLD_2022\T4_2022-06-15_2,3nguL\5mbar\100x_5mbar_out_013.nd2

#Read tif file

img = tifffile.imread(file_path)

#Show image
fig, ax = plt.subplots(figsize=(5,5))
ax.axis('off')
ax.imshow(img, cmap='gray') 
plt.title('Raw image')
plt.show()

#Histogram
fontsize = 15
fig, ax = plt.subplots(figsize=(5,2))
I = img.ravel()
I = I[I != 0] 
plt.hist(I,bins=256, color='k', range=(0,1.5*2**16))
plt.title(f'Histogram\nRaw Image', fontsize=fontsize)
plt.xlabel('pixel value')
plt.ylabel('count')  
plt.show()

#%%

#Select the percentile values to use for the limits
min = 10 #
max = 99 #99.9
min_val = np.percentile(img,min) #Returns the 10-th percentile of the array elements.
max_val = np.percentile(img,max) #Returns the 99-th percentile of the array elements.

#Show limits on the raw image histogram
fontsize = 15
fig, ax = plt.subplots(figsize=(5,2))
I = img.ravel()
I = I[I != 0] 
plt.hist(I,bins=256, color='k', range=(0,1.5*2**16))
plt.title(f'Histogram\nRaw Image', fontsize=fontsize)
plt.xlabel('pixel value')
plt.ylabel('count')  
plt.axvline(min_val, color='r', linestyle='dashed', linewidth=1, label=f'{min}th percentile')
plt.axvline(max_val, color='b', linestyle='dashed', linewidth=1, label=f'{max}th percentile')
plt.legend()
plt.show()

img_perc = exposure.rescale_intensity(img.copy(), in_range=(min_val, max_val), out_range='uint8')

#Show image
fig, ax = plt.subplots(figsize=(5,5))
ax.axis('off')
ax.imshow(img_perc, cmap='gray') 
plt.title('Contrast-enhanced image')
plt.show()

#Histogram
fontsize = 15
fig, ax = plt.subplots(figsize=(5,2))
I = img_perc.ravel()
I = I[I != 0] 
plt.hist(I,bins=256, color='k', range=(0,255))
plt.title(f'Histogram\nContrast-enhanced image', fontsize=fontsize)
plt.xlabel('pixel value')
plt.ylabel('count')  
plt.show()

#%%
#Select the pixel values to use for the limits
min_val = 20000
max_val = 30000

#Show limits on the raw image histogram
fontsize = 15
fig, ax = plt.subplots(figsize=(5,2))
I = img.ravel()
I = I[I != 0] 
plt.hist(I,bins=256, color='k', range=(0,1.5*2**16))
plt.title(f'Histogram\nRaw Image', fontsize=fontsize)
plt.xlabel('pixel value')
plt.ylabel('count')  
plt.axvline(min_val, color='r', linestyle='dashed', linewidth=1, label=f'{min_val}, min limit')
plt.axvline(max_val, color='b', linestyle='dashed', linewidth=1, label=f'{max_val}, max limit')
plt.legend()
plt.show()

img_lims = exposure.rescale_intensity(img.copy(), in_range=(min_val, max_val), out_range='uint8')

#Show image
fig, ax = plt.subplots(figsize=(5,5))
ax.axis('off')
ax.imshow(img_lims, cmap='gray') 
plt.title('Contrast-enhanced image 2')
plt.show()

#Histogram
fontsize = 15
fig, ax = plt.subplots(figsize=(5,2))
I = img_lims.ravel()
I = I[I != 0] 
plt.hist(I,bins=256, color='k', range=(0,255))
plt.title(f'Histogram\nContrast-enhanced image 2', fontsize=fontsize)
plt.xlabel('pixel value')
plt.ylabel('count')  
plt.show()