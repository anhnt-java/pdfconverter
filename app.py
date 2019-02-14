import pyrebase
import logging

from constant import *
from configuration import *
from helper import *

def stream_listener(message):
	if (isinstance(message['data'], dict)):
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
				logging.info('[%s] Start process at %d times', path, retry_count + 1)

				# Make temporary directory
				logging.info('[%s] Start make temporary directory', path)
				make_directory(temp_directory)
				if (not exists_path(temp_directory)):
					raise Exception('[%s] Make temporary directory failed' % path)
				logging.info('[%s] Make temporary directory done', path)

				# Download original file
				logging.info('[%s] Start download original file', path)
				storage.child(path).download(temp_file)
				logging.info('[%s] Download original file done', path)

				# Convert to PDF if not PDF
				logging.info('[%s] Start convert to PDF', path)
				if (extension != 'pdf'):
					convert_to_pdf(temp_file, pdf_file)
				if (not exists_path(pdf_file)):
					raise Exception('[%s] Convert to PDF failed' % path)
				logging.info('[%s] Convert to PDF done', path)
				update_document_status(path, DOCUMENT_STATUS['CONVERTED'], pages)

				# Make images directory
				logging.info('[%s] Start make images directory', path)
				make_directory(images_directory)
				if (not exists_path(images_directory)):
					raise Exception('[%s] Make images directory failed' % path)
				logging.info('[%s] Make images directory done', path)

				# Convert PDF to images
				logging.info('[%s] Start convert to images', path)
				convert_to_images(pdf_file, images_directory)
				image_files = list_directory(images_directory)
				if not image_files:
					raise Exception('[%s] Convert to images failed' % path)
				logging.info('[%s] Convert to images done', path)

				# Upload pages
				logging.info('[%s] Start upload pages', path)
				sorted_image_files = sorted(image_files)
				for page_number, image_file in enumerate(sorted_image_files):
					logging.info('[%s] Start upload page %d', path, page_number + 1)
					page_path = create_page_path(base_path, name, page_number + 1)
					storage.child(page_path).put(images_directory + '/' + image_file)
					logging.info('[%s] Upload page %d done', path, page_number + 1)
					pages[page_number + 1] = page_path
				logging.info('[%s] Upload pages done', path)
			except Exception as e:
				logging.error(e)
				logging.info('[%s] Process at %d times failed', path, retry_count + 1)
				retry_count = retry_count + 1
				success_flag = False
			finally:
				remove_directory(temp_directory)

			if success_flag == True:
				logging.info('[%s] Process at %d times done', path, retry_count + 1)
				break

		if retry_count <= MAX_RETRY_COUNT:
			update_document_status(path, DOCUMENT_STATUS['SUCCESSFUL'], pages)
		else:
			update_document_status(path, DOCUMENT_STATUS['FAILED'], pages)

db.child('documents').stream(stream_listener)