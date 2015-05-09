from flask import Flask, abort, request, url_for, make_response, render_template, redirect, send_from_directory, jsonify, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from werkzeug import secure_filename

import StringIO
import numpy as np
import matplotlib.pyplot as plt
import os

#used for the excel output.
import StringIO
import mimetypes
from werkzeug.datastructures import Headers #used for exporting files?

from pond import Pond
from data_reader import DataReader
import xlrd, xlwt #reading and writing, respectively.



#http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# This is the path to the upload directory
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'xls', 'xlsx', 'csv'])

# Initialize the Flask application
app = Flask(__name__)

app.secret_key = 'This is really unique and secret'

# These are the extension that we are accepting to be uploaded
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #arbitrary 16 megabyte upload limit
#app.debug=True


#used for making it possible to get numbers from python, and put them in HTML
#Got this from http://blog.bouni.de/blog/2013/04/24/call-functions-out-of-jinjs2-templates/
@app.context_processor
def my_utility_processor():

    def bppr(filename):
        reader = DataReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Check if the file is one of the allowed types/extensions
        pondList = reader.read()
        pond = pondList[0]
        bpprList =[]
        doyList =[]
        for pond in pondList:
            bppr = pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(0.25) #use quarter-hours
            bpprList.append(bppr)
            doy =pond.getDayOfYear()
            doyList.append(doy)
        return bpprList

    return dict(bppr=bppr)




# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def indexView():
    if request.method == 'POST':
         # Get the name of the uploaded file
        file = request.files['file']
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file form the temporal folder to
            # the upload folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            reader = DataReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            pondList = reader.read()
            bpprList =[]
            doyList =[]
            for pond in pondList:
                bppr = pond.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(0.25) #use quarter-hours
                bpprList.append(bppr)
                doy =pond.getDayOfYear()
                doyList.append(doy)




            # Redirect the user to the uploaded_file route, which
            # will basically show on the browser the uploaded file
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            return redirect(url_for("bpprtest",filename=filename))
    return """
        <h2>Protoype built in Flask and Python. Click here to see a graph of light in a pond! </h2>

<!--
        <form method="POST" action="%s" id="form" onchange="check()">
            Mean depth of pond (m): <input type="number" id="meanDepth" name="meanDepth" min="0" max = "500" step="0.1" value = "20.0" required/>
            Maximum depth of pond (m): <input type="number" id="maxDepth" name="maxDepth" min="0" max = "500" step="0.1" value = "20.0" required/>
            Phosphorus (mg/m^3): <input type="number" name="phosphorus" min="0" max = "2000" step="0.1" value = "100.0" required/>
            <input type="submit" value="graph!">
        </form>
-->

        <p>[Removed for now]</p>

        <h2>Prototype 2: Upload Data File</h2>
        <p>Download example data <a href="inputs_pruned.xlsx" download="example_data.xlsx">here</a></p>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>

        <script language='javascript' type='text/javascript'>
        function check() {
            if (document.getElementById('maxDepth').value < document.getElementById('meanDepth').value) {
                <!--document.getElementById('maxDepth').value=document.getElementById('meanDepth').value-->
                document.getElementById('maxDepth').setCustomValidity('The max depth must be greater than or equal to the mean depth');
            } else {
                // input is valid -- reset the error message
                document.getElementById('maxDepth').setCustomValidity('');
           }
        }
        </script>

        """ % (url_for('lightGraph'))




# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/tmp/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                              filename)

#http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
@app.route('/inputs_pruned.xlsx', methods=['GET', 'POST'])
def template():
    return app.send_static_file('inputs_pruned.xlsx')



@app.route('/bpprtest', methods=['GET', 'POST'])
@app.route('/bpprtest.html', methods=['GET', 'POST'])
def bpprtest():
    return render_template("bpprtest.html")







#code to make an excel file for download.
#modified from http://snipplr.com/view/69344/create-excel-file-with-xlwt-and-insert-in-flask-response-valid-for-jqueryfiledownload/
@app.route('/export/')
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
    workbook = xlwt.Workbook()

    #.... code here for adding worksheets and cells
    #Create a new workbook object
    workbook = xlwt.Workbook()

    #Add a sheet
    worksheet = workbook.add_sheet('Statistics')

    #Add some values
    for x in range(0, 10):
        for y in range(0,10):
            worksheet.write(x,y,x*y)

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







#######################################################################


@app.route('/lightGraph', methods=['GET', 'POST'])
@app.route('/lightGraph.html', methods=['GET', 'POST'])
def lightGraph():
    return render_template("lightGraph.html")


@app.route('/dailyTPPGraph', methods=['GET', 'POST'])
@app.route('/dailyTPPGraph.html', methods=['GET', 'POST'])
def dailyTPPGraph():
    return render_template("lightGraph.html")



@app.route('/pondlight.png', methods=['GET', 'POST'])
def pondLight():

    #default values
    meanDepth = 20.0 #meters
    maxDepth = 20.0 #meters
    phosphorus = 100.0 #mg/m^3

    #get inputs
    try:
        stringMeanDepth = request.args.get('meanDepth')
        stringMaxDepth = request.args.get('maxDepth')
        stringPhosphorus = request.args.get('phosphorus')
        meanDepth = float(stringMeanDepth)
        maxDepth = float(stringMaxDepth)
        phosphorus = float(stringPhosphorus)
    except:
        #redundant. TODO: better except
        meanDepth = 20.0 #meters
        maxDepth = 20.0 #meters
        phosphorus = 100.0 #mg/m^3


    #validate inputs
    #error checking
    if(maxDepth<=0):
        maxDepth = 20.0

    if(meanDepth>maxDepth):
        meanDepth=maxDepth

    if(meanDepth<=0):
        meanDepth=maxDepth

    if(phosphorus<=0):
        phosphorus=100.0


    #setup pond object
    pond = Pond(meanDepth,maxDepth)
    pond.setBackgroundLightAtten(0.05)




    #figures, subplots, other magic graphing stuff
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111

    #setup y-axis
    depths = np.linspace(0, maxDepth, 500) #500 points spaced from 0.0 to max depth
    y = depths

    #Setup x-axis
    #plot the extreme (example) values
    pond.setTotalPhos(500.0)
    x1 =np.multiply((pond.lightAtDepthZAndTimeT(depths,6.0)/pond.lightAtDepthZAndTimeT(0.0,6.0)),100)
    pond.setTotalPhos(3.0)
    x2 =np.multiply((pond.lightAtDepthZAndTimeT(depths,6.0)/pond.lightAtDepthZAndTimeT(0.0,6.0)),100)









    #set labels for graph legend
    #fancy number formatting from http://stackoverflow.com/questions/21226868/superscript-in-python-plots
    label1 = "500 $mg/m^3$"
    label2 = "3.0 $mg/m^3$"


    ax.plot(x1, y, 'k--', label= label1)
    ax.plot(x2, y, 'k:', label= label2)


    #try graphing user input.
    try:
        pond.setTotalPhos(phosphorus)
        x3 = np.multiply((pond.lightAtDepthZAndTimeT(depths,6.0)/pond.lightAtDepthZAndTimeT(0.0,6.0)),100) #6.0 = halfway through 12-hour day = noon.
        label3 = "%.1f $mg/m^3$" %phosphorus #fancy %f stuff learned from http://stackoverflow.com/questions/6649597/python-decimal-places-putting-floats-into-a-string
        ax.plot(x3, y, 'r-', label= label3)

    except:
        label3 = "ERROR: invalid input?"



    ax.set_xlabel('light percentage')

    ax.set_xlim([1,100])

    plt.grid(True)


    plt.ylabel('depth (m)')

    fig.gca().invert_yaxis() #make 0 be at the top, rather than the borrom

#    plt.legend((l1, l2), ('Line 1', 'Line 2'), 'upper left')
    legend = plt.legend(loc='lower right', shadow=True)
    frame  = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width


    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/dailyTPP.png', methods=['GET', 'POST'])
def dailyTPP():

    #figures, subplots, other magic graphing stuff
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111


    #default values
    meanDepth = 20.0 #meters
    maxDepth = 20.0 #meters
    phosphorus = 100.0 #mg/m^3

    #TODO:try to get user value of phosphorus.
        #get inputs
    try:
        stringMeanDepth = request.args.get('meanDepth')
        stringMaxDepth = request.args.get('maxDepth')
        stringPhosphorus = request.args.get('phosphorus')
        meanDepth = float(stringMeanDepth)
        maxDepth = float(stringMaxDepth)
        phosphorus = float(stringPhosphorus)
    except:
        #redundant. TODO: better except
        meanDepth = 20.0 #meters
        maxDepth = 20.0 #meters
        phosphorus = 100.0 #mg/m^3

    #input validation
    if(maxDepth<=0):
        maxDepth = 20.0

    if(meanDepth>maxDepth):
        meanDepth=maxDepth

    if(meanDepth<=0):
        meanDepth=maxDepth

    if(phosphorus<=0):
        phosphorus=100.0




    exampleSmallPhosVal=3.0
    exampleLargePhosVal=500.0
    lightIntensityAtOnsetOfSaturation = 180.0






    pond = Pond(meanDepth,maxDepth)




    #setup y-axis
    depths = np.linspace(0, maxDepth, 500) #500 points spaced from 0.0 to max depth
    y = depths
    print len(y)

    #Setup x-axis
    #plot the extreme (example) values
    pond.setTotalPhos(exampleLargePhosVal)
    x1 =pond.dailyPPatDepthZ(0.25,0.1, lightIntensityAtOnsetOfSaturation, depths) #deltaT, deltaZ, light intensity at onset of saturation, depths
    pond.setTotalPhos(exampleSmallPhosVal)
    x2 =pond.dailyPPatDepthZ(0.25,0.1, lightIntensityAtOnsetOfSaturation, depths) #deltaT, deltaZ, light intensity at onset of saturation, depths
    pond.setTotalPhos(phosphorus)
    x3 =pond.dailyPPatDepthZ(0.25,0.1, lightIntensityAtOnsetOfSaturation, depths) #deltaT, deltaZ, light intensity at onset of saturation, depths

    print len(x1)

    #set labels for graph legend
    #fancy number formatting from http://stackoverflow.com/questions/21226868/superscript-in-python-plots
    label1 = "%.1f $mg/m^3$" %exampleLargePhosVal #fancy %f stuff learned from http://stackoverflow.com/questions/6649597/python-decimal-places-putting-floats-into-a-string
    label2 = "%.1f $mg/m^3$" %exampleSmallPhosVal
    label3 = "%.1f $mg/m^3$" %phosphorus


    #graph lines here
    ax.plot(x1, y, 'k--', label= label1)
    ax.plot(x2, y, 'k:', label= label2)
    ax.plot(x3, y, 'r-', label= label3)










    ax.set_xlabel('Daily Pelagic Primary Productivity (mg C*$m^{-3}*d^{-1}$) for different phosphorus levels')

    #set x scale
    allXValues = x1+x2+x3
    maxValue=np.amax(allXValues)
    ax.set_xlim([1,maxValue])

    plt.grid(True)

    plt.ylabel('depth (m)')

    fig.gca().invert_yaxis() #make 0 be at the top, rather than the borrom

    legend = plt.legend(loc='lower right', shadow=True)
    frame  = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width


    #Source of sorcery: https://gist.github.com/liuyxpp/1250396
    #figure to canvas, canvas to buffer, buffer to png, png to response. magic!
    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response



