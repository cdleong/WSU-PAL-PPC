from flask import Flask, request, url_for, make_response, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import StringIO
import numpy as np
import matplotlib.pyplot as plt


from pond import Pond

app = Flask(__name__)
app.secret_key = 'This is really unique and secret'



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def indexView():

    return """
        <p>Protoype built in Flask and Python. Click here to see a graph of light in a pond! </p>
        <form method="POST" action="%s" id="form" onchange="check()">
            Mean depth of pond (m): <input type="number" id="meanDepth" name="meanDepth" min="0" max = "500" step="0.1" value = "20.0" required/>
            Maximum depth of pond (m): <input type="number" id="maxDepth" name="maxDepth" min="0" max = "500" step="0.1" value = "20.0" required/>
            Phosphorus (mg/m^3): <input type="number" name="phosphorus" min="0" max = "2000" step="0.1" value = "100.0" required/>
            <input type="submit" value="graph!">
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


if __name__ == '__main__':
	
	
	debug=True
	if (False==debug):
		print("running publically!")
		app.run(host='0.0.0.0') #uncomment to run publically		
	else:
		print("running in debug mode!")
		app.run()



