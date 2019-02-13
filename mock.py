import pyrebase

config = {
  'apiKey': 'AIzaSyDYC3lEXGcYalZRvnP8cV44ec5ts1j0o0I',
  'authDomain': 'ashina-26.firebaseapp.com',
  'databaseURL': 'https://ashina-26.firebaseio.com',
  'storageBucket': 'ashina-26.appspot.com',
  'serviceAccount': 'firebase.json'
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

db.child('documents').child('1').set({
	'path': 'meeting/document/1/doc.doc',
	'extension': 'doc',
  'name': 'doc'
})