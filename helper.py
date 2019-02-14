import os
import shutil
import pathlib
import subprocess
import requests
import time
import hashlib

from constant import *

def exists_path(path):
	return os.path.exists(path)

def remove_directory(directory_path):
	if (os.path.exists(directory_path)):
		shutil.rmtree(directory_path)

def make_directory(directory_path):
	remove_directory(directory_path)
	pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True) 

def list_directory(directory_path):
	return os.listdir(directory_path)

def run_command(args, timeout):
	process = subprocess.Popen(args)
	try:
		process.communicate(timeout=timeout)
	except TimeoutExpired:
		print(args + ' timeout!')
	process.kill()

def beautify_slash(string):
	return '\\\\'.join(string.split('/'))

def convert_to_pdf(temp_file, pdf_file):
	run_command(['powershell', '-executionpolicy', 'bypass', '-File', POWERSHELL_FILE, beautify_slash(temp_file), beautify_slash(pdf_file)], 1800)

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
	#      raise Exception('Could not call REST endpoint: ' + path)

def create_page_path(base_path, name, page):
	unix_time = int(time.time())
	string = name + '-' + str(page + unix_time)
	hash_string = hashlib.sha256(string.encode('utf-8')).hexdigest()
	return base_path + '/' + hash_string