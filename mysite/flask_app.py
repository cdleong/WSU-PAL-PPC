import os
import shutil
import tempfile
import traceback
from flask import Flask, request, url_for, make_response, render_template, redirect, send_from_directory, Response, session
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from werkzeug.utils import secure_filename

import StringIO
import uuid
import json



from data_reader import DataReader

#used for the excel output.
import xlwt #excel writing
import mimetypes
from werkzeug.datastructures import Headers #used for exporting files?
from fileinput import filename
from flask.json import tojson_filter


##############################################################
#IMPORTANT VARIABLES
#
##############################################################

#How to work with file uploads http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# This is the path to the upload directory

# UPLOAD_FOLDER = '/tmp/' #this one works on Linux.
# UPLOAD_FOLDER = 'tmp' #this one works on Windows.
UPLOAD_FOLDER = tempfile.mkdtemp() #this works on either, and doesn't seem to need Admin rights
ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'csv'])
TEMPLATE_FILE = 'template.xls'
TEMPLATE_FILE_ROUTE = '/'+TEMPLATE_FILE
EXAMPLE_FILE = 'example_data.xls'
EXAMPLE_FILE_ROUTE = '/'+EXAMPLE_FILE
INTERNAL_SERVER_ERROR_TEMPLATE_FILE = "500.html"
INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE = '/'+INTERNAL_SERVER_ERROR_TEMPLATE_FILE

FIRST_DATA_ROW_FOR_EXPORT = 1


# Initialize the Flask application
app = Flask(__name__)

random_number = os.urandom(24)
app.secret_key = random_number

# These are the extension that we are accepting to be uploaded
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #arbitrary 16 megabyte upload limit



def get_rounded_BPPR_list(filename=TEMPLATE_FILE):
    '''
    returns list of double values, rounded to two decimal places
    '''
    print "running get_rounded_BPPR_list"
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
    '''
    '''
    print "running getPondList method"
    try:
        pond_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print "pond_file type is ", type(pond_file)
        reader = DataReader(pond_file)
    except Exception as e:
        print "error in getPondList"
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))
    # Check if the file is one of the allowed types/extensions
    pondList = reader.read()
    return pondList



#used for making it possible to get numbers from python, and put them in HTML
#Got this from http://blog.bouni.de/blog/2013/04/24/call-functions-out-of-jinjs2-templates/
@app.context_processor
def my_utility_processor():

    #returns a list of floats.
    def bppr(filename):
        print "running bppr method"
        bpprList = get_rounded_BPPR_list(filename)
        return bpprList

    def ponds(filename=None):
        print "running ponds method"
        pondList = []
        if(filename is not None):
            pondList = getPondList(filename)
            
        else:
            pondList = session['pond_id_list']
        print "in ponds method, pondList is ", pondList
        return len(pondList)

    return dict(bppr=bppr, ponds=ponds)




# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
           
           
def jsonify_pond(pondList=[]):
    jsonified_pond_list = []
    
    return jsonified_pond_list

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def indexView():
    print "running index view"
    
    print "session is", session
    print "session current object is", session._get_current_object()
    
    #http://runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-uploaded_file-to-the-server-in-flask-for-python
    if request.method == 'POST': #true if the button "upload" is clicked
        # Get the name of the uploaded uploaded_file
        uploaded_file = request.files['uploaded_file']
        

        
        
        
        print type(uploaded_file)
        # Check if the uploaded_file is one of the allowed types/extensions
        if uploaded_file and allowed_file(uploaded_file.filename):
            
            
            
            pond_file = request.files['uploaded_file']
            print "pond_file type: ", type(pond_file)
            print "pond_file content_length= ", pond_file.content_length, ", content_type= ", pond_file.content_type            
    #         print "pond_file.read()", pond_file.read()
    #         print "type(pond_file.read())", type(pond_file.read())
            try:
                print "trying to parse and read"
     
                   
                reader = DataReader("sdflkjsdflkj") #I don't plan on using this filename, thanks
                pondList = reader.readFile(pond_file.read())                     
            except Exception as e:
                print "error in getPondList"
                print str(e)
                return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))
            # Check if the file is one of the allowed types/extensions
        
            print "in indexView. pondlist is: ", pondList                    
#             session['pondList'] = pondList #doesn't work. Ponds are not JSON serializable. And it would be huge pain to make them so.
            pond_id_list = []
            pond_day_list = []
            pond_bppr_list = []
            pond_pppr_list = []
            for pond in pondList:
                pond_id_list.append(pond.get_lake_id())
                pond_day_list.append(pond.get_day_of_year())
                pond_bppr_list.append(pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared())
                pond_pppr_list.append(pond.calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared())
                
            print "pond id list", pond_id_list
            print "pond day list", pond_day_list
            session['pond_id_list'] = pond_id_list
            session['pond_day_list'] = pond_day_list
            session['pond_bppr_list'] = pond_bppr_list
            session['pond_pppr_list'] = pond_pppr_list
            
            #BELOW THIS LINE, CODE INVOLVING SAVING THE DATA TO A FILE JUST TO PASS IT BETWEEN VIEWS
            
            
            # Make the filename safe, remove unsupported chars
#             filename = secure_filename(uploaded_file.filename)
            #on second thought, let's not trust the user and secure_filename to give us something safe
            
#             #let's make up something
#             print "generating filename"
#             filename = str(uuid.uuid4())
#             print "filename generated was: ", filename
            
            
            
#             
#             thing = session['user_uploaded_pond_file'].filename
#             print "type of session['user_uploaded_pond_file'].filename", type(thing)             
#             otherthing = session['user_uploaded_pond_file']
#             print "type of session['user_uploaded_pond_file']", type(otherthing)

            
            

            # Move the uploaded_file from  the temporal folder to
            # the upload folder we setup
#             uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            




            return redirect(url_for("bpprtest",filename=filename))

        else:
            error_message = "Apologies, that file extension is not allowed. Please try one of the allowed extensions."
            return render_template('home_with_error.html', template_file_route = TEMPLATE_FILE_ROUTE, example_file_route = EXAMPLE_FILE_ROUTE,error_message=error_message)

    return render_template('home.html', template_file_route = TEMPLATE_FILE_ROUTE, example_file_route = EXAMPLE_FILE_ROUTE)








################################################################################################################################
# used to offer template file
#http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
################################################################################################################################
@app.route(TEMPLATE_FILE_ROUTE, methods=['GET', 'POST'])
def template():
    print "running template method"
    try:
        return app.send_static_file(TEMPLATE_FILE)
    except Exception as e:
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))


################################################################################################################################
# used to offer template file
#http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
################################################################################################################################
@app.route(EXAMPLE_FILE_ROUTE, methods=['GET', 'POST'])
def example_file_view():
    print "running example_file_view method"
    try:
        return app.send_static_file(EXAMPLE_FILE)
    except Exception as e:
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))

################################################################
#renders the bpprtest template.
################################################################
@app.route('/bpprtest', methods=['GET', 'POST'])
@app.route('/bpprtest.html', methods=['GET', 'POST'])
def bpprtest():
    print "running bpprtest method"
     
    print "request method: ", request.method
#     print "request.files['uploaded_file']", request.files['uploaded_file']
#     print "request.files['uploaded_file'].filename", request.files['uploaded_file'].filename
     


#     @after_this_request
#     def cleanup(response):
#         print "******************"
#         print "cleanup routine stub"
#         print "******************"
#
#         #deletes all the contents of the folder nicely, which makes downloading the data afterwards impossible.
#         dirPath = UPLOAD_FOLDER
#         fileList = os.listdir(dirPath)
#         for fileName in fileList:
#             os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
#         shutil.rmtree(UPLOAD_FOLDER+"/") #should delete contents of upload folder, but deletes the whole folder.
#         return response
    try:
        return render_template("bpprtest.html")
    except Exception as e:
        print str(e)
        return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))







################################################################################################################################
#code to make an excel file for download.
#modified from...
#http://snipplr.com/view/69344/create-excel-file-with-xlwt-and-insert-in-flask-response-valid-for-jqueryfiledownload/
################################################################################################################################
@app.route('/export')
def export_view():
    print "running export_view method"
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



    #################
    #add values
    #################
#     #get inputs
#     inputFile = ""
#     try:
#             inputFile = request.args.get('filename')
#     except Exception as e:
#         print str(e)
#         return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(e))
# 
# 
# 
#     pondlist = getPondList(inputFile)
#     lake_id_list = []
#     day_of_year_list = []
#     bpprList = []
#     ppprList = []
#     for pond in pondlist:
#         lake_id = pond.get_lake_id()
#         lake_id_list.append(lake_id)
#         day_of_year = pond.get_day_of_year()
#         day_of_year_list.append(day_of_year)
#         bppr = pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
#         bpprList.append(bppr)
#         pppr = pond.calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared()
#         ppprList.append(pppr)
    
        #.... code here for adding worksheets and cells
    #Create a new workbook object
    workbook = xlwt.Workbook()

    #Add a sheet
    worksheet = workbook.add_sheet('Statistics')
    
    #columns to write to
    lake_ID_column = 0
    day_of_year_column = lake_ID_column+1
    bppr_column = day_of_year_column+1
    pppr_column = bppr_column+1        
        
    lake_id_list = session['pond_id_list']
    day_of_year_list = session['pond_day_list']
    bpprList = session['pond_bppr_list']
    ppprList = session['pond_pppr_list']

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


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large'

@app.errorhandler(404)
def pageNotFound(error):
    return "Page not found"

@app.errorhandler(500)
def internalServerError(internal_exception):
    traceback.print_exc()
    print str(internal_exception)
    return render_template(INTERNAL_SERVER_ERROR_TEMPLATE_ROUTE, error = str(internal_exception))





if __name__ == '__main__':
    print "upload folder is ", UPLOAD_FOLDER
    print "a random number is: ", random_number
    
    
    print app.secret_key
    debug_mode = False
    i_am_sure_i_want_to_let_people_execute_arbitrary_code = "no" #"yes" for yes.
    i_want_an_externally_visible_site = False
    if(debug_mode and "yes"==i_am_sure_i_want_to_let_people_execute_arbitrary_code):
        print "running in debug mode"
        app.run(debug=True)
        print "stopped running app"
    elif(i_want_an_externally_visible_site):
        app.run(host='0.0.0.0')
    else:
        app.run()