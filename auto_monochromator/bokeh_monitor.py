from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from random import random
from functools import partial
from collections import deque
from pcdsdevices import beam_stats
from auto_monochromator.rapid_stats import RapidHist
import numpy as np

def modify_doc(doc,incident):
    
    #d = figure(x_range=(0, 100), y_range=(0, 100))
    #d = figure()
    d = figure(x_range=(510, 550),y_range=(-50,500))
    k = d.quad(
        top=[],
        bottom=[],
        left=[],
        right=[],
        fill_color="#036564",
        line_color="#033649"
    )
    ks = k.data_source
    class s:
        pass
    
    m = s()
    m.i = 0

    hist = RapidHist(
        # 1000 just seems to be the magic number for the accel_ev 
        maxlen=1000,
        bins = np.arange(510,550,.5)
    )
        

    def callback(k_obj,ds,hist):
        k_obj.i += 1
        hist.push(ds)
        print(k_obj.i,"\t",len(hist._data),"\t",len(ds))
        ds.clear()
        nd = dict()
        hs, bins = hist.hist()
        # nd['top'] = [random()*100]
        # nd['bottom'] = [random()*100]
        # nd['left'] = [random()*100]
        # nd['right'] = [random()*100]
        nd['top'] = hs
        nd['bottom'] = np.zeros(len(hs))
        nd['left'] = bins[:-1]
        nd['right'] = bins[1:]
        ks.data = nd
    
    
    # add a button widget and configure with the call back
    # button = Button(label="Press Me")
    # button.on_click(callback)
    doc.add_periodic_callback(partial(callback,k_obj=m,ds=incident,hist=hist),100)
    # put the button and plot in a layout and add to the document
    doc.add_root(column(d))
    
# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
def launch_server():

    inc_data_block = deque(maxlen=1000)
    stats = beam_stats.BeamStats()

    def append_to_data_block(*args,**kwargs):
        kwargs['inc_data_block'].append(kwargs['value'])
    
    stats.accel_ev.subscribe(
        partial(append_to_data_block,inc_data_block=inc_data_block)
    )
   

    server = Server(
        {'/': partial(modify_doc,incident=inc_data_block)},
        num_procs=1
   )
    server.start()


    print('Opening Bokeh application on http://localhost:5006/')
    
    #server.io_loop.add_callback(server.show, "/")
    try:
        server.io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        server.io_loop.stop()
