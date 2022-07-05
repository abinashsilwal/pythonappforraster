import shapefile
import numpy as np
import geopandas as gpd  #To read/open shapefile
import matplotlib.pyplot as plt
from tkinter import *
from tkinter.filedialog import * 
import rasterio as rio   #raster analysis
#from shapely.geometry import *  #geometric object analysis
#from shapely.geometry.polygon import * #For polygon
from rasterio.plot import show #Display raster image
import tkinter.font as tkFont  #font size
import earthpy.plot as ep   #Functionality around spatial plotting.
import earthpy.spatial as es  #Functions to manipulate spatial raster and vector data.


root=Tk()
root.title("Python Application for Raster Stacking and Clipping")
# fontstyle = tkFont.Font(family="Lucida Grande", size=10)

# label1= Label(root, text= "Spatial Raster Dataset Analysis", font= fontstyle).grid(row=0)

w=Label(root,text="Open Raster File").grid(row=2,column=0)
w2=Label(root,text="Open Shape File").grid(row=4,column=0)

def about():
    root = Tk()
    root.title("About")

 
    # specify size of window.
    root.geometry("250x100")
 
    # Create text widget and specify size.

    T= Label(root, text= """This application is developed by Abinash Silwal 
    from Kathmandu University.""")
    l = Label(root, text = "About Developer")
    l.config(font =("Courier", 14))

 
    # Create an Exit button.
    b9 = Button(root, text = "Back",
            command = root.destroy)

    
    l.pack()
    T.pack()
    b9.pack()

    #tk.mainloop()




def fileopen():
    global extent
    global raster_image
    global file
    file = askopenfilename(defaultextension=".TIF", filetypes=[("All Files","*.*")])
    if file == "":
        print("INVALID FILENAME")
        file = None
    else:

        with rio.open(file) as src:
            #plot_bands expects the number of plot titles 
            #to equal the number of array raster layers.
            raster_image = src.read()[0] 
            extent = rio.plot.plotting_extent(src)
            # meta_profile = src.profile
            # print(meta_profile)



def fileop():
    global shp_file 
    #global num
    file2 = askopenfilename(defaultextension=".shp", filetypes=[("All Files","*.*")])
    if file2 == "": 
        print("INVALID FILENAME")
            # no file to open 
        file2 = None
    else:
        shp_file = gpd.read_file(file2)
        # files = (shapefile.Reader(file2))
        # print (files)

opn=Button(root,text="Open",command=fileopen).grid(row=2,column=3)
opn2=Button(root,text="Open",command=fileop).grid(row=4,column=3)
about1=Button(root,text="About",command=about).grid(row=2,column=12)



def showshape():
    ep.plot_bands(raster_image,
               cmap='terrain',
               extent=extent,
               title="Landsat Image",
               cbar= False
               );

def showshape2():
    #ploting shape file
    fig, ax = plt.subplots(figsize =(6, 6))
    shp_file.plot(ax=ax)
    ax.set_title("Shapefile Imported into Python", 
             fontsize = 16)
    ax.set_axis_off();
    plt.show()

def bothplot():
    #for overlay button
    fig, ax = plt.subplots(figsize=(10, 10))
    ep.plot_bands(raster_image,
              cmap='terrain',
              extent=extent,
              cbar=False,
              ax=ax )
    #alpha=.6 for transparency
    shp_file.plot(ax=ax, alpha=.6, color='g');
    plt.show()

def masked():

    global raster_meta
    global raster_crop
    global raster_crop_ma
    with rio.open(file) as src:
        raster_crop, raster_meta = es.crop_image(src, shp_file)
    # Update the metadata to have the new shape (x and y and affine information)
    raster_meta.update({"driver": "GTiff",
                 "height": raster_crop.shape[1],
                 "width": raster_crop.shape[2],
                 "transform": raster_meta["transform"]})
    
    # generate an extent for the newly cropped object for plotting
    print(raster_meta)
    
    # mask the nodata and plot the newly cropped raster layer
    #This function is a shortcut to masked_where, with condition = (x == value).
    raster_crop_ma = np.ma.masked_equal(raster_crop[0], -9999.0) 

    #plotting cropped image
    ep.plot_bands(raster_crop_ma, cmap='Greys_r', cbar=False);

    print(raster_crop[0])

def save():
    # print(raster_crop)
    path_out = asksaveasfilename(initialfile='raster_crop.tif', defaultextension=".tif", 
        filetypes=[("All Files","*.*"), ("Images","*.tif")]) 
    with rio.open(path_out, 'w', **raster_meta) as ff:
        ff.write(raster_crop[0], 1)

shpe=Button(root,text="Show Raster Image",command=showshape).grid(row=6,column=10)
shpe2=Button(root,text="Show Shapefile",command=showshape2).grid(row=8,column=10)
shpe3=Button(root,text="Overlay Both",command=bothplot).grid(row=10,column=10)
shpe4=Button(root,text="Clipped Output",command= masked).grid(row=11,column=10)
shpe5=Button(root,text="Save Output",command= save).grid(row=11,column=12)
shpe6=Button(root,text="Quit",command= root.destroy).grid(row=13,column=12)



#------------Stacking Part---------Above one is for clipping----
num=int()
c=[]
files=[]
List=[]
output_stack= " "
def fileopen3():
    global List
    #to get no. of band as input
    num = int(text_area.get("1.0", 'end-1c'))
    print("Input = ", num)
    for i in range(num):
        
        file = askopenfilename(defaultextension=".TIF", filetypes=[("All Files","*.*")])
        if file == "": 
            print("INVALID FILENAME")
            # no file to open 
            file = None
        else: 
            files.append(file)
            # with rio.open(file) as src:
            
            #     c = src.read()[0]
            #     List.append(c)

def stack():
    global output_stack
    global stack_image

    # Read metadata of first file
    with rio.open(files[0]) as src0:
        meta = src0.meta
        print(meta)

    # Update meta due to stacking
    meta.update({"count" : len(files), #set the number of stack layers
        "driver": "GTiff"}) #set the input is ENVI format
    print(meta)
    
    #Read each layer and write it to stack 
    output_stack = asksaveasfilename(initialfile='stacked.tif', defaultextension=".tif", 
    filetypes=[("All Files","*.*"), ("Images","*.tif")])

    with rio.open(output_stack, 'w', **meta) as dst:
        for id, layer in enumerate(files):
            # Read each layer and write it to stack
            with rio.open(layer) as src1:
                stack_image = src1.read()[0]
  
                dst.write_band(id + 1, stack_image)
                # add source dataset description
                # dst.set_band_description(id+1 , src1.descriptions[0])
                # print (dst)

def plotstack():
    ep.plot_bands(stack_image, cmap='Greys_r', cbar=False);


def plot():
    with rio.open(output_stack) as src:
        landsat_post = src.read()
    # Plot all bands using earthpy
    band_titles=[]
    for i in range(num):

        band_titles.append("Band "+ str(i+1))

    ep.plot_bands(landsat_post,
              title=band_titles, cbar=False)
    plt.show()


w=Label(root,text="Enter no. of bands").grid(row=13,column=0)
text_area=Text(root,width=3,height=1)
text_area.grid(row=13,column=1)
b1=Button(root,text="Open",command=fileopen3).grid(row=13,column=3)
b2=Button(root,text="Stack",command=stack).grid(row=13,column=6)
b3=Button(root,text="Plot Stack",command=plotstack).grid(row=13,column=8)
b4=Button(root,text="plotbands",command=plot).grid(row=13,column=9)

root.mainloop()