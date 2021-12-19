import os
import json
from collections import Counter, OrderedDict

from werkzeug.utils import secure_filename
from flask import Flask, render_template, flash, request, redirect, url_for

import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go

from app import app

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'doc', 'docs', 'docx'}

app.secret_key = b'_5#y2L"F4Qkqghv671gs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_ext(filename: str):
	return ('.' in filename) and (filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS)


@app.route('/uploads/<name>')
def process_file(name):
	stats: None
	with open(os.path.join(app.config['UPLOAD_FOLDER'], name), 'r') as f:

		cnt = Counter()
		for c in f.read():
			if c in '123456789':
				cnt[int(c)] += 1
		total = cnt.total()

		digits = np.arange(1, 10)
		freqs = list(OrderedDict(sorted({d: round(k / total, 4) for d, k in cnt.items()}.items())).values())
		benford = np.round(np.log(1 + 1 / digits) / np.log(10), 4)

		fig = go.Figure(data=[
			go.Bar(name='Benford\'s', x=digits, y=benford, opacity=0.8),
			go.Bar(name='Yours', x=digits, y=freqs, opacity=0.8)
		])
		fig.update_layout(title="Let's compare:", barmode='group', template='plotly_dark')

		graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
		stats = render_template('file_stat.html', graphJSON=graphJSON)

	if stats is not None:
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'], name))
		return stats
	return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if 'file' not in request.files:
			return render_template('index.html')
		file = request.files['file']
		if file.filename == '':
			return render_template('index.html')
		if file and allowed_ext(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('process_file', name=filename, _external=True))
	return render_template('index.html')
