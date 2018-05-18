from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from random import random

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
i=0
def modify_doc(doc):
    # create a plot and style its properties
    p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
    p.border_fill_color = 'black'
    p.background_fill_color = 'black'
    p.outline_line_color = None
    p.grid.grid_line_color = None
    
    
    
    
    # add a text renderer to our plot (no data yet)
    r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="20pt",
               text_baseline="middle", text_align="center")
    
    i = 0
    
    ds = r.data_source
    
    # create a callback that will add a number in a random location
    def callback():
        global i
    
        # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['x'] = ds.data['x'] + [random()*70 + 15]
        new_data['y'] = ds.data['y'] + [random()*70 + 15]
        new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
        new_data['text'] = ds.data['text'] + [str(i)]
        ds.data = new_data
    
        i = i + 1
    
    
    
    d = figure(x_range=(0, 100), y_range=(0, 100))
    
    k = d.quad(
        top=[],
        bottom=[],
        left=[],
        right=[],
        fill_color="#036564",
        line_color="#033649"
    )
    ks = k.data_source
    
    def cb():
        global i
        nd = dict()
        nd['top'] = [random()*100]
        nd['bottom'] = [random()*100]
        nd['left'] = [random()*100]
        nd['right'] = [random()*100]
        ks.data = nd
    
    
    # add a button widget and configure with the call back
    # button = Button(label="Press Me")
    # button.on_click(callback)
    doc.add_periodic_callback(callback,100)
    doc.add_periodic_callback(cb,740)
    # put the button and plot in a layout and add to the document
    doc.add_root(column(d,p))
    
# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
def go():
    server = Server({'/': modify_doc}, num_procs=1)
    server.start()
    
    print('Opening Bokeh application on http://localhost:5006/')
    
    #server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
