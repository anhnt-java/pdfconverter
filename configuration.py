import logging
import pyrebase

from constant import *

# Logging configuration
logging.basicConfig(filename=LOGGING_FILE, level=logging.INFO, format=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)

# Firebase configuration
firebase = pyrebase.initialize_app({
	'apiKey': FIREBASE_API_KEY,
	'authDomain': FIREBASE_AUTH_DOMAIN,
	'databaseURL': FIREBASE_DATABASE_URL,
	'storageBucket': FIREBASE_STORAGE_BUCKET,
	'serviceAccount': FIREBASE_SERVICE_ACCOUNT
})
db = firebase.database()
storage = firebase.storage()