import os

import traceback
from flask import Flask, request, url_for, render_template, redirect, Response, session, make_response
import StringIO
from data_reader import DataReader
import xlwt #excel writing. used for the excel output.
import sys
import mimetypes
from werkzeug.datastructures import Headers #used for exporting files
import jsonpickle #lets us transfer Pond object between views. 

#for graphing
#we need to import matplotlib and set which renderer to use before we use pyplot. This allows it to work without a GUI installed on the OS.
import matplotlib as mpl 
mpl.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

##############################################################
#IMPORTANT VARIABLES
#
##############################################################

#How to work with file uploads http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# This is the path to the upload directory


ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'csv'])
TEMPLATE_FILE = 'template.xls'
TEMPLATE_FILE_ROUTE = '/'+TEMPLATE_FILE
EXAMPLE_FILE = 'example_data.xls'
EXAMPLE_FILE_ROUTE = '/'+EXAMPLE_FILE
INTERNAL_SERVER_ERROR_TEMPLATE_FILE = "500.html"
INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE = '/'+INTERNAL_SERVER_ERROR_TEMPLATE_FILE

FIRST_DATA_ROW_FOR_EXPORT = 1


#SESSION KEYS
PICKLED_POND_LIST_KEY = 'pickled_pond_list'


# Initialize the Flask application
app = Flask(__name__)

random_number = os.urandom(24)
app.secret_key = random_number

# These are the extension that we are accepting to be uploaded
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #arbitrary 16 megabyte upload limit







def getPondList():
    #SALAMANDER
    pond_list = unpickle_pond_list()
    return pond_list
    





#used for making it possible to get numbers from python, and put them in HTML
#Got this from http://blog.bouni.de/blog/2013/04/24/call-functions-out-of-jinjs2-templates/
@app.context_processor
def my_utility_processor():

    def ponds():
        print "running ponds method"
        pond_list = getPondList()
        print "length of pond list: ", len(pond_list)
        return pond_list

            
    return dict(ponds=ponds)




           
           

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def indexView():
    '''
    Renders the template for the index.
    '''
#     if 'pond_pic_visible' not in session:
#         session['pond_pic_visible']='visible'
        
    
    
    #http://runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-uploaded_file-to-the-server-in-flask-for-python
    if request.method == 'POST': #true if the button "upload" is clicked
        # Get the name of the uploaded uploaded_file
        uploaded_file = request.files['uploaded_file']
        

        
        
        
        # Check if the uploaded_file is one of the allowed types/extensions
        if uploaded_file and allowed_file(uploaded_file.filename):
            
            
            
            pond_file = request.files['uploaded_file']

            try:                   
                reader = DataReader("") #I don't plan on using this filename, thanks
                pond_list = reader.readFile(pond_file.read()) #read method is http://werkzeug.pocoo.org/docs/0.10/datastructures/#werkzeug.datastructures.FileStorage,                 
            except Exception as e:
                print "error in getPondList"
                print str(e)
                return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))
            





            

            
            ##################################################################
            #let's try something. AARDVARK <--easy to search for this
            #(this might be more work than making Pond objects serializable)
            ##################################################################
            ##trying http://jsonpickle.github.io/
            pickle_pond_list(pond_list)         
            




            return redirect(url_for("primary_production"))

        else:
            error_message = "Apologies, that file extension is not allowed. Please try one of the allowed extensions."
            return render_template('home_with_error.html', template_file_route = TEMPLATE_FILE_ROUTE, example_file_route = EXAMPLE_FILE_ROUTE,error_message=error_message)

    return render_template('home.html', template_file_route = TEMPLATE_FILE_ROUTE, example_file_route = EXAMPLE_FILE_ROUTE)




@app.route(TEMPLATE_FILE_ROUTE, methods=['GET', 'POST'])
def template():
    '''
    Used to offer template data file
    #http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask    
    '''
    try:
        return app.send_static_file(TEMPLATE_FILE)
    except Exception as e:
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))



@app.route(EXAMPLE_FILE_ROUTE, methods=['GET', 'POST'])
def example_file_view():
    '''
    Used to offer example data file
    #http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
    '''
    try:
        return app.send_static_file(EXAMPLE_FILE)
    except Exception as e:
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))

################################################################
#renders the primary_production template.
################################################################
@app.route('/primary_production', methods=['GET', 'POST'])
@app.route('/primary_production.html', methods=['GET', 'POST'])
def primary_production():
    '''
    Renders the primary_production template, which shows calculated values and a button to download them.
    '''
    print "primary_production view"
    try:
        return render_template("primary_production.html")
    except Exception as e:
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))


#c.f. flask quickstart "variable rules"
# @app.route('/graph/<pond_key>/<int:layer>')
# @app.route('/graph')
@app.route('/graph/<pond_key>/<int:layer_index>')
def hourly_ppr_in_layer_graph(pond_key="", layer_index = 0):
    '''
    #TODO: comments
    '''
    #get the correct pond from the list in the session dict
    
    print "***************"
    print "pond_key is ", pond_key
    print "layer_index is ", layer_index
    
    try:
        pond = retrieve_pond(pond_key)
        times  = pond.get_list_of_times()
        ppr_values = pond.calculate_hourly_phytoplankton_primary_production_rates_list_over_whole_day_in_thermal_layer(layer_index)
        x_values = times
        y_values = ppr_values
#         print "x values: ", x_values
#         print "x length: ", len(x_values)
#         print "y values: ", y_values
#         print "y length: ", len(y_values)
        
        
        
        x_label = "hour"
        y_label  = "PPPR (mgC*m^-3)"
        graph_title = "PPPR, ", pond.get_lake_id(), " layer ", layer_index+1
        return graph(x_values,y_values,x_label, y_label,graph_title)        
    except:
        print "Unexpected error:", sys.exc_info()[0]
        #return error graphic
        #TODO: an error graphic
        return app.send_static_file('graph_error.png')
    

    
    

  



@app.route('/export')
def export_view():
    '''
    Code to make an excel file for download.
    Modified from...
    http://snipplr.com/view/69344/create-excel-file-with-xlwt-and-insert-in-flask-response-valid-for-jqueryfiledownload/    
    '''
    print "export"
    #########################
    # Code for creating Flask
    # response
    #########################
    response = Response()
    response.status_code = 200


    ##################################
    # Code for creating Excel data and
    # inserting into Flask response
    ##################################

    #.... code here for adding worksheets and cells
    #Create a new workbook object
    workbook = xlwt.Workbook()

    #Add a sheet
    daily_worksheet = workbook.add_sheet('Daily Statistics')
    
    #columns to write to
    year_column = 0
    lake_ID_column = year_column+1
    day_of_year_column = lake_ID_column+1
    bppr_column = day_of_year_column+1
    pppr_column = bppr_column+1        
         
    #get data from session, write to daily_worksheet
    #PLATYPUS
    pond_list  = unpickle_pond_list()

    
    year_list = []
    lake_id_list = []
    day_of_year_list = []
    bpprList =[]
    ppprList = []
    
    for pond in pond_list:
        year = pond.get_year()
        lake_id = pond.get_lake_id()
        day_of_year = pond.get_day_of_year()
        bppr = pond.calculate_daily_whole_lake_benthic_primary_production_m2()
        pppr = pond.calculate_daily_whole_lake_phytoplankton_primary_production_m2()
        
        year_list.append(year)
        lake_id_list.append(lake_id)
        day_of_year_list.append(day_of_year)
        bpprList.append(bppr)
        ppprList.append(pppr)
    
 
    write_column_to_worksheet(daily_worksheet, year_column, "year", year_list)
    write_column_to_worksheet(daily_worksheet, lake_ID_column, "Lake ID", lake_id_list)
    write_column_to_worksheet(daily_worksheet, day_of_year_column, "day of year", day_of_year_list)
    write_column_to_worksheet(daily_worksheet, bppr_column, "bppr_m2", bpprList)
    write_column_to_worksheet(daily_worksheet, pppr_column, "pppr_m2", ppprList)

    
    #Add another sheet
    hourly_worksheet = workbook.add_sheet('Hourly Statistics')
    
    
    
    #columns
    year_column = 0
    lake_ID_column = year_column+1
    day_of_year_column = lake_ID_column+1    
    layer_column = day_of_year_column+1
    hour_column = layer_column+1
    hourly_ppr_rates_column = hour_column+1
   
        
    #lists
    year_list = []
    lake_id_list = []
    day_of_year_list = []    
    layer_list = []
    hour_list = []
    hourly_ppr_rates_list = []
    counter = 0
    for pond in pond_list:
        year = pond.get_year()
        lake_id = pond.get_lake_id()
        day_of_year = pond.get_day_of_year()        
        for layer in range (0, len(pond.get_thermal_layer_depths())):              
            hourly_ppr_in_this_layer_list = []                      
            hourly_ppr_in_this_layer_list = pond.calculate_hourly_phytoplankton_primary_production_rates_list_over_whole_day_in_thermal_layer(layer)
            hour = 0.0
            time_interval = pond.get_time_interval()
            for hourly_ppr in hourly_ppr_in_this_layer_list:
                year_list.append(year)
                lake_id_list.append(lake_id)
                day_of_year_list.append(day_of_year)
                layer_list.append(layer)
                hour_list.append(hour)
                hourly_ppr_rates_list.append(hourly_ppr)
                hour+=time_interval
                counter+=1
                if(counter>10000):
                    raise Exception("too big! The ouput is too big!!!")
                    sys.exit()
                    exit()
                    
    #write to columns
    write_column_to_worksheet(hourly_worksheet, year_column, "year", year_list)
    write_column_to_worksheet(hourly_worksheet, lake_ID_column, "lake", lake_id_list)
    write_column_to_worksheet(hourly_worksheet, day_of_year_column, "day", day_of_year_list)
    write_column_to_worksheet(hourly_worksheet, layer_column, "layer", layer_list)
    write_column_to_worksheet(hourly_worksheet, hour_column, "hour", hour_list)
    write_column_to_worksheet(hourly_worksheet, hourly_ppr_rates_column, "ppr_m3", hourly_ppr_rates_list)


    #This is the magic. The workbook is saved into the StringIO object,
    #then that is passed to response for Flask to use.
    output = StringIO.StringIO()
    workbook.save(output)
    response.data = output.getvalue()

    ################################
    # Code for setting correct
    # headers for jquery.fileDownload
    #################################
    filename = "export.xls"
    mimetype_tuple = mimetypes.guess_type(filename)

    #HTTP headers for forcing file download
    response_headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': mimetype_tuple[0],
            'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
        })

    if not mimetype_tuple[1] is None:
        response.update({
                'Content-Encoding': mimetype_tuple[1]
            })

    response.headers = response_headers

    #as per jquery.fileDownload.js requirements
    response.set_cookie('fileDownload', 'true', path='/')

    ################################
    # Return the response
    #################################
    return response




@app.errorhandler(413)
def request_entity_too_large(error):
    '''
    Error handler view. Should display when files that are too large are uploaded.
    '''
    return 'File Too Large'

@app.errorhandler(404)
def pageNotFound(error):
    
    return "Page not found"

@app.errorhandler(500)
def internalServerError(internal_exception):
    '''
    Prints internal program exceptions so they are visible by the user. Stopgap measure for usability.
    
    '''
    
    #TODO: more and better errors, so that when specific parts of the data are wrong, users can figure it out.
    traceback.print_exc()
    print str(internal_exception)
    return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(internal_exception))


#HELPER METHODS
def write_column_to_worksheet(worksheet,column_number=0, column_header = "", values_list=[]):
    '''
    Prepends a column header and puts the data in values_list into worksheet at the specified column
    @param worksheet: An xlrd worksheet to write to.
    @param column_number: Column number to write to.
    @param column_header: Header to put at the top of the column.
    @param values_list: list of values to put in the column.
    '''
    print "writing column to worksheet"
    values_list.insert(0, column_header) #stick the column header at the front.
    numRows = len(values_list)


    for i in range(0, numRows):
        row = i
        column = column_number
        value=values_list[row]
        worksheet.write(row,column,value)



def retrieve_pond(pond_key = ""):
    
    #pickled pond list from session
    print "retrieve pond", pond_key
    pond_list = unpickle_pond_list()
    try:
        pond = next(pond for pond in pond_list if pond.get_key()==pond_key)
    except: 
        raise Exception("Could not find pond")    
    print "found pond"
    return pond
    
        
      

def unpickle_pond_list():    
    
    pickled_ponds_list = session[PICKLED_POND_LIST_KEY]
    pond_list = []
    for pickled_pond in pickled_ponds_list:
        pond = jsonpickle.decode(pickled_pond, keys=True) #BEWARE! THIS TURNS ALL THE KEYS IN BATHYMETRIC POND SHAPE TO STRINGS
        pond_list.append(pond)      
        
    return pond_list
    
def pickle_pond_list(pond_list = []):
    pickled_ponds_list = []
    for pond in pond_list:
        pickled_pond = jsonpickle.encode(pond,keys=True) #make it NOT SET THE KEYS TO STRINGS
        
        pickled_ponds_list.append(pickled_pond)
        
    session[PICKLED_POND_LIST_KEY] = pickled_ponds_list             


def graph(x_vals=[],y_vals=[],x_label = "x label", y_label="y label", graph_title = "graph_title", graph_line_width=3):
    print "graphing"
    
#         #get arguments.
#     graph_type = request.args.get('graph_type')
    
    
    #make the figure
    fig = plt.figure() 
#     fig = plt.Figure()
    
    
    #make the graph.
    f_subplot = fig.add_subplot(1, 1, 1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111
    
     #setup y_vals-f_subplot
    if(len(x_vals)<2):
        x_vals=np.arange(0.0, 8.0, 0.01)
     
     #Setup x_vals-f_subplot
#     y_vals=[]
    if(len(y_vals)<2):
        y_vals = np.sin(2*np.pi*x_vals)
    
    
    #set labels and graph_title
    #fancy number formatting from http://stackoverflow.com/questions/21226868/superscript-in-python-plots
    f_subplot.set_xlabel(x_label)
    f_subplot.set_ylabel(y_label)
    f_subplot.set_title(graph_title)
    
    #plot
    f_subplot.plot(x_vals, y_vals, linewidth = graph_line_width)
    
    
    #package up the image and send it back. All of this replaces the ".show()" step.
    #figure to canvas. canvas with StringIO to png. png passed to make_response.
    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response  
    
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS








if __name__ == '__main__':

    print "a random number is: ", random_number
    
    
    print "secret key is", app.secret_key
    debug_mode = False
    i_am_sure_i_want_to_let_people_execute_arbitrary_code = "no" #"yes" for yes.
    i_want_an_externally_visible_site = True
    if(debug_mode and "yes"==i_am_sure_i_want_to_let_people_execute_arbitrary_code):
        print "running in debug mode"
        app.run(debug=True)
        print "stopped running app"
    elif(i_want_an_externally_visible_site):
        app.run(host='0.0.0.0')
    else:
        app.run()