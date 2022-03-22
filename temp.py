#from flask import Flask
import PIL
import requests
import pytineye
from flask import Flask,render_template,url_for,request,redirect,session,flash,session
from flask.wrappers import Request, Response
from pytineye import TinEyeAPIRequest
from werkzeug.utils import secure_filename
from PIL import Image
from os import rename,remove

app = Flask(__name__)
app.secret_key = '@HMagdy'

#Api TinEye
api_key = 'nYCMEHnWC*juHZRuuJTB_Sy,alMreegasfLdaIFu'
api = TinEyeAPIRequest(
    'https://api.tineye.com/rest/',
    api_key
)


def TinEye_api(link=None,Ufile=None,sort=None,order=None,limit=None):
    try:
        if link:
            response = api.search_url(url=link, sort='crawl_date', order='asc', limit= limit)
        elif Ufile :
            with open(Ufile, 'rb') as fp:
                data = fp.read()
                #response = api.search_data(data=data, sort='crawl_date', order='asc') #Original function
                try:
                    if sort:
                        response = api.search_data(data=data, sort=sort, order=order,limit= limit)
                    elif order and sort and limit==None:
                        response = api.search_data(data=data, sort='crawl_date', order=order, limit= limit)
                except Exception as e:
                    response = api.search_data(data=data, sort='crawl_date', order='desc', limit= limit)
        try:
            results=[response.matches,response.stats]
        except:
            results=[[],[]]

        return results
        
    except pytineye.exceptions.TinEyeAPIError:

        return redirect('/')

def remain():
    rem = api.remaining_searches()
    return rem

def img_fn(imgfile=None,imgname=None,sort=None,order=None, limit=None):
    try:
        if imgfile:
            imgfile.save(secure_filename(imgfile.filename))
            rename(imgfile.filename,"./sImages/"+imgfile.filename)
            basewidth = 5000
            img = Image.open(r"./sImages/"+imgfile.filename)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save("./sImages/"+imgfile.filename)
            results=TinEye_api(Ufile="./sImages/"+imgfile.filename, sort=sort, order=order, limit=limit)
            remove("./sImages/"+imgfile.filename)
        elif imgname:
            basewidth = 1000
            img = Image.open(r"./sImages/"+imgname)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save("./sImages/"+imgname)
            results=TinEye_api(Ufile="./sImages/"+imgname, sort=sort, order=order, limit=limit)
            remove("./sImages/"+imgname)
        
        return results
    except UnboundLocalError:
        return redirect('/')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'),404


'''#For TinEye_api(link) in line 22;
@app.route('/search')
def show_results(labelname=None):
    #results1 = request.args.get('results1', '0-100')
    imgurl=request.args.get('imgurl')
    # imgurl = Image.thumbnail((300,300))
    session['imgurl']=imgurl
    results=TinEye_api(link=imgurl)
    return render_template('index.html',posts=[results, remain()])
''' 

@app.route("/getimage",methods=['POST'])
def getimage():
    sort=request.form['sort']
    order=request.form['order']
    limit=request.form['limit']
    imgurl=request.form['imgurl']
    response=requests.get(imgurl,timeout=60)
    imgfile=open('./sImages/file1.png','wb')
    imgfile.write(response.content)
    imgfile.close()
    results=img_fn(imgname='file1.png',sort=sort,order=order, limit=limit)
    session['imgurl']=imgurl
    return render_template('index.html',posts=[results, remain()])

@app.route("/searchimg",methods=['POST'])
def searchimg():
    try:
        sort=request.form['sort']
        order=request.form['order']
        limit=request.form['limit']
        imgfile = request.files['imgfile']
        results=img_fn(imgfile=imgfile,sort=sort,order=order, limit=limit)
        return render_template('index.html',posts=[results, remain()])
    except (FileNotFoundError, UnboundLocalError):
        return redirect('/')


@app.route("/")
@app.route("/index")
def home():
    imgurl=session.get('imgurl')
    if not imgurl:
        results=[[],[]]
    else:
        results=TinEye_api(link=imgurl)
    return render_template('index.html',posts=[results, remain()],title="iTechsEye")

@app.route('/clear',methods=['GET'])
def clear():
    session.clear()
    return redirect('/')

theport=4000
if __name__ == '__main__':
    app.register_error_handler(404,not_found)
    app.run(host="0.0.0.0",port=theport,debug=True,use_reloader=False)
    #app.run(host="0.0.0.0",use_reloader=False)