import os
from flask import Flask, render_template, request
from sightengine.client import SightengineClient

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# You'll need to register for sightengine
#client = SightengineClient('<id>', '<secret>')

if (__name__ == "__main__"):
	app.run(host='0.0.0.0', port=5001)

def is_it_trump(faces, prob=0.8):
	invalid = True
	reason = "Not Donald J. Trump"
	for i, face in enumerate(faces):
		if 'celebrity' in face:
			if face['celebrity'][0]['prob'] > prob and face['celebrity'][0]['name'] == "Donald J. Trump":
				reason = "Contains Donald J. Trump"
				print(reason)
				invalid = False
			if face['celebrity'][0]['prob'] > 0.90 and face['celebrity'][0]['name'] == "Vladimir Putin":
				faces.pop(i)
				return is_it_trump(faces, 0.1)
	return invalid, reason


@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
	file = request.files['image']
	f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

	if len(request.form) > 0:
		token = request.form['token']
		if token != "RDRDRD":
			reason = "Wrong Token"
			return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)
	else:
		reason = "Missing Token"
		return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)
		

	#jtoken = request.files['token']
	#print(token)

	# validate image
	print(file.filename)

	file.save(f)
	invalid = True
	reason = "Not Donald J. Trump"

	output = client.check('nudity', 'wad', 'celebrities', 'face-attributes').set_file(f)

	print(output)

	if output['status'] == "failure":
		os.remove(f)
		reason = output['error']['message']
		print(reason)
		return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)
	
	if len(output['faces']) < 1:
		os.remove(f)
		reason = "Not Donald J. Trump"
		print(reason)
		return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)
		
	if output['nudity']['safe'] <= output['nudity']['partial'] and output['nudity']['safe'] <= output['nudity']['raw']:
		reason = "Contains Nudity"
		print(reason)
		invalid = True

	if output['weapon'] > 0.2 or output['alcohol'] > 0.2 or output['drugs'] > 0.2:
		reason = "Contains Weapons, Alcohol, or Drugs"
		print(reason)
		invalid = True

	# is it trump
	invalid, reason = is_it_trump(output['faces'])

	if 'faces' in output:
		if output['faces'][0]['attributes']['minor'] > 0.85:
			reason = "Contains a child"
			print(reason)
			invalid = True
	 	
	if invalid:
		os.remove(f)

	f = '' + f
	return render_template('index.html', invalidImage=invalid, reason=reason, init=True, filename=f)

