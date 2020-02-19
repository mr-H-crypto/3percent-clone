from flask import render_template , jsonify, request
from app import app
from werkzeug.utils import secure_filename
from .pdfWR import PDF
import json
import os
import sys
import pandas as pd

app.config['UPLOAD_FOLDER'] = 'app/temp/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','xlsx'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

@app.route('/signUp')
def signUp():
    return render_template('form.html')

@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    user =  request.form['username']
    password = request.form['password']
    return json.dumps({'status':'OK','user':user,'pass':password})

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/python-flask-files-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'files[]' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	
	files = request.files.getlist('files[]')
	
	errors = {}
	success = False

	for file in files:
		if file and allowed_file(file.filename):
    		## Upload file :
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			## Read file
			Entities =  pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename),
			sheet_name = 'Entities information')

			## Process file
			app.logger.info(int(Entities['Siret Number for French entities'][0]))
			
			cerfa = PDF('2746-sd_2589')
			cerfa.read_template()
			cerfa.fill_at('year',2020)
			cerfa.fill_at('siret',int(Entities['Siret Number for French entities'][0]))
			cerfa.write_pdf()

			## Remove uploaded file
			os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			success = True
		else:
			errors[file.filename] = 'File type is not allowed'
	
	if success and errors:
		errors['message'] = 'File(s) successfully uploaded'
		resp = jsonify(errors)
		resp.status_code = 206
		return resp
	if success:
		resp = jsonify({'message' : 'Files successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify(errors)
		resp.status_code = 400
		return resp