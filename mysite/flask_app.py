from flask import Flask, request, url_for, make_response, render_template, redirect, send_from_directory, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from werkzeug.utils import secure_filename

import StringIO
import numpy as np
import matplotlib.pyplot as plt
import os




from pond import Pond
from data_reader import DataReader

#used for the excel output.
import xlwt #excel writing
import mimetypes
from werkzeug.datastructures import Headers #used for exporting files?


##############################################################
#IMPORTANT VARIABLES
#
##############################################################

#How to work with file uploads http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# This is the path to the upload directory
UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['txt', 'xls', 'xlsx', 'csv'])
TEMPLATE_FILE = 'template.xls'
TEMPLATE_FILE_ROUTE = '/'+TEMPLATE_FILE

FIRST_DATA_ROW_FOR_EXPORT = 1

# Initialize the Flask application
app = Flask(__name__)

app.secret_key = 'This is really unique and secret'

# These are the extension that we are accepting to be uploaded
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #arbitrary 16 megabyte upload limit
#app.debug=True


def get_rounded_BPPR_list(filename=TEMPLATE_FILE):
    '''
    returns list of double values, rounded to two decimal places
    '''
    # Check if the file is one of the allowed types/extensions
    pondList = getPondList(filename)
    pond = pondList[0]
    bpprList =[]
    doyList =[]
    for pond in pondList:
        bppr = pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared() #uses quarter-hours by default
        bpprFloat = float("{0:.2f}".format(bppr)) #round to two decimal places
        bpprList.append(bpprFloat)
        doy =pond.get_day_of_year()
        doyList.append(doy)
    return bpprList

def getPondList(filename = TEMPLATE_FILE):
    reader = DataReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # Check if the file is one of the allowed types/extensions
    pondList = reader.read()
    return pondList    
    


#used for making it possible to get numbers from python, and put them in HTML
#Got this from http://blog.bouni.de/blog/2013/04/24/call-functions-out-of-jinjs2-templates/
@app.context_processor
def my_utility_processor():
    
    #returns a list of floats.
    def bppr(filename):
        bpprList = get_rounded_BPPR_list(filename)
        return bpprList
    
    def ponds(filename):
        pondList = getPondList(filename)
        return pondList


    return dict(bppr=bppr, ponds=ponds)




# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def indexView():
    #http://runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-uploaded_file-to-the-server-in-flask-for-python
    if request.method == 'POST': #true if the button "upload" is clicked
        # Get the name of the uploaded uploaded_file
        uploaded_file = request.files['uploaded_file']
        # Check if the uploaded_file is one of the allowed types/extensions
        if uploaded_file and allowed_file(uploaded_file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(uploaded_file.filename)
            # Move the uploaded_file form the temporal folder to
            # the upload folder we setup
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            reader = DataReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            pondList = reader.read()
            bpprList =[]
            doyList =[]
            for pond in pondList:
                bppr = pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
                bpprList.append(bppr)
                doy =pond.get_day_of_year()
                doyList.append(doy)




            return redirect(url_for("bpprtest",filename=filename))
    return render_template('home.html', route = TEMPLATE_FILE_ROUTE)






# This route is expecting a parameter containing the name
# of a uploaded_file. Then it will locate that uploaded_file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/tmp/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                              filename)

################################################################################################################################
# used to offer template file
#http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
################################################################################################################################
@app.route(TEMPLATE_FILE_ROUTE, methods=['GET', 'POST'])
def template():
    return app.send_static_file(TEMPLATE_FILE)


################################################################
#renders the bpprtest template.
################################################################
@app.route('/bpprtest', methods=['GET', 'POST'])
@app.route('/bpprtest.html', methods=['GET', 'POST'])
def bpprtest():
    return render_template("bpprtest.html")






################################################################################################################################
#code to make an excel file for download.
#modified from...
#http://snipplr.com/view/69344/create-excel-file-with-xlwt-and-insert-in-flask-response-valid-for-jqueryfiledownload/
################################################################################################################################
@app.route('/export')
def export_view():
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
    worksheet = workbook.add_sheet('Statistics')

    #################
    #add values
    #################
    #get inputs
    inputFile = ""
    try:
            inputFile = request.args.get('filename')
    except:
        #redundant. TODO: better except
            inputFile = TEMPLATE_FILE
    
    lake_ID_column = 0
    day_of_year_column = lake_ID_column+1
    bppr_column = day_of_year_column+1
    pppr_column = bppr_column+1
    
    pondlist = getPondList(inputFile)
    lake_id_list = []
    day_of_year_list = []
    bpprList = []
    ppprList = []
    for pond in pondlist:
        lake_id = pond.get_lake_id()
        lake_id_list.append(lake_id)
        day_of_year = pond.get_day_of_year()
        day_of_year_list.append(day_of_year)
        bppr = pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
        bpprList.append(bppr)
        pppr = pond.calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared()
        ppprList.append(pppr)

    
    write_column_to_worksheet(worksheet, lake_ID_column, "Lake ID", lake_id_list)
    write_column_to_worksheet(worksheet, day_of_year_column, "day of year", day_of_year_list)
    write_column_to_worksheet(worksheet, bppr_column, "BPPR", bpprList)
    write_column_to_worksheet(worksheet, pppr_column, "PPPR", ppprList)
    

    # workbook.save('statistics.xls')


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

def write_column_to_worksheet(worksheet,column_number=0, column_header = "", values_list=[]):
    '''
    Prepends a column header and puts the data in values_list into worksheet at the specified column
    '''
    print "writing column to worksheet"
    values_list.insert(0, column_header) #stick the column header at the front.
    numRows = len(values_list)
    
    
    for i in range(0, numRows):
        row = i
        column = column_number
        value=values_list[row]
        worksheet.write(row,column,value)
    
    



if __name__ == '__main__':
    debug_mode = False
    if(debug_mode):
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')
