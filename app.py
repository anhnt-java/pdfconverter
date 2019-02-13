import pyrebase
import pathlib
import os
import shutil
import subprocess
import requests
import time
import hashlib
import logging

# Firebase
config = {
  'apiKey': 'AIzaSyDYC3lEXGcYalZRvnP8cV44ec5ts1j0o0I',
  'authDomain': 'ashina-26.firebaseapp.com',
  'databaseURL': 'https://ashina-26.firebaseio.com',
  'storageBucket': 'ashina-26.appspot.com',
  'serviceAccount': 'firebase.json'
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

# Constants
BASE_DIRECTORY = 'E:/temp'
POWERSHELL_FILE = 'E:/convert.ps1'
GHOSTSCRIPT_FILE = 'C:/Program Files/gs/gs9.26/bin/gswin64c.exe'
REST_ENDPOINT = ''
DOCUMENT_STATUS = {
	'CONVERTED': 0,
	'SUCCESSFUL': 1,
	'FAILED': 2
}
MAX_RETRY_COUNT = 3

def make_directory(path):
	if (os.path.exists(path)):
		shutil.rmtree(path)
	pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

def run_command(args, timeout):
	process = subprocess.Popen(args)
	try:
		process.communicate(timeout=timeout)
	except TimeoutExpired:
		print(args + ' timeout!')
		process.kill()

def convert_to_pdf(temp_file, pdf_file):
	run_command(['powershell', '-executionpolicy', 'bypass', '-File', POWERSHELL_FILE, temp_file, pdf_file], 1800)

def convert_to_images(pdf_file, images_directory):
	run_command([GHOSTSCRIPT_FILE, '-dNOPAUSE', '-dBATCH', '-sDEVICE=jpeg', '-dTextAlphaBits=4', '-dGraphicsAlphaBits=4', '-r300', 
		'-sOutputFile=' + images_directory + '/%03d.jpg', pdf_file], 1800)

def update_document_status(path, status, pages):
	print(path)
	print(status)
	print(pages)
	# body = {'path': path, 'status': status, 'pages': pages}
	# response = requests.post(REST_ENDPOINT, json=body)
	# if response.status_code != 200:
 #    	raise Exception('Could not call REST endpoint: ' + path)

def create_page_path(base_path, name, page):
	unix_time = int(time.time())
	string = name + '-' + str(page + unix_time)
	hash_string = hashlib.sha256(string.encode('utf-8')).hexdigest()
	return base_path + '/' + hash_string

def stream_listener(message):
	if (message['data'] != None):
		print(message['data'])
		path = message['data']['path']
		extension = message['data']['extension']
		name = message['data']['name']

		base_path = path[:path.rfind('/')]
		temp_directory = BASE_DIRECTORY + '/' + base_path
		temp_file = temp_directory + '/temp.' + extension
		pdf_file = temp_directory + '/temp.pdf'
		images_directory = temp_directory + '/images'
		pages = {}

		retry_count = 0;

		while retry_count <= MAX_RETRY_COUNT:
			success_flag = True

			try:
				print('Start process at ' + str(retry_count + 1) + ' times: ' + path)

				# Make temporary directory
				print('Start make temporary directory: ' + path)
				make_directory(temp_directory)
				if (not os.path.exists(temp_directory)):
					raise Exception('Make temporary directory failed: ' + path)
				print('Make temporary directory done: ' + path)

				# Download original file
				print('Start download original file: ' + path)
				storage.child(path).download(temp_file)
				print('Download original file done: ' + path)

				# Convert to PDF if not PDF
				print('Start convert to PDF: ' + path)
				if (extension != 'pdf'):
					convert_to_pdf(temp_file, pdf_file)
				if (not os.path.exists(pdf_file)):
					raise Exception('Convert to PDF failed: ' + path)
				print('Convert to PDF done: ' + path)
				update_document_status(path, DOCUMENT_STATUS['CONVERTED'], pages)

				# Make images directory
				print('Start make images directory: ' + path)
				make_directory(images_directory)
				if (not os.path.exists(images_directory)):
					raise Exception('Make images directory failed: ' + path)
				print('Make images directory done: ' + path)

				# Convert PDF to images
				print('Start convert to images: ' + path)
				convert_to_images(pdf_file, images_directory)
				if not os.listdir(images_directory):
					raise Exception('Convert to images failed: ' + path)
				print('Convert to images done: ' + path)

				# Upload pages
				print('Start upload pages: ' + path)
				image_files = sorted(os.listdir(images_directory))
				for page_number, image_file in enumerate(image_files):
					print('Start upload page ' + str(page_number + 1) + ': ' + path)
					page_path = create_page_path(base_path, name, page_number + 1)
					storage.child(page_path).put(images_directory + '/' + image_file)
					print('Upload page ' + str(page_number + 1) + ' done: ' + path)
					pages[page_number + 1] = page_path
				print('Upload pages done: ' + path)
			except Exception as e:
				logging.error(e)
				print('Process at ' + str(retry_count + 1) + ' times failed: ' + path)
				retry_count = retry_count + 1
				success_flag = False
			finally:
				shutil.rmtree(temp_directory)

			if success_flag == True:
				print('Process at ' + str(retry_count + 1) + ' times done: ' + path)
				break

		if retry_count <= MAX_RETRY_COUNT:
			update_document_status(path, DOCUMENT_STATUS['SUCCESSFUL'], pages)
		else:
			update_document_status(path, DOCUMENT_STATUS['FAILED'], pages)

db.child('documents').stream(stream_listener)