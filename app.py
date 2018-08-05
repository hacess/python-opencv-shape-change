# -*- coding: utf-8 -*-
# @Author: user
# @Date:   2018-06-21 17:04:32
# @Last Modified by:   user
# @Last Modified time: 2018-06-21 18:30:22

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import werkzeug
import json
from app_main import SizeChange
import os


ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
FILE_CONTENT_TYPES = { 
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}
UPLOAD_FOLDER = './files'


app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
app.config.from_object(__name__)

class mainpage(Resource):
	def get(self):
		return {'Welcome': 'world'}
		

class UploadFiles(Resource):
      def post(self):
        images_array=[]
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.FileStorage, location='files',required=True, action='append')
        args = parse.parse_args()
        imageFile = args['file']
        for val in imageFile:
        	extension = val.filename.rsplit('.', 1)[1].lower()
        	if '.' in val.filename and not extension in app.config['ALLOWED_EXTENSIONS']:
        		return {'message': 'upload a image file ... we cannot read codes'}
        	print(val.filename)
        	val.save(os.path.join(app.config['UPLOAD_FOLDER'],val.filename))
        	images_array.append(os.path.join(app.config['UPLOAD_FOLDER'],val.filename))
        change= SizeChange()
        inc_width=change.imagedimenstion(images_array)
        os.remove(images_array[0])
        os.remove(images_array[1])
        return {'width increase(%)': inc_width}

api.add_resource(UploadFiles, '/files')
api.add_resource(mainpage, '/')

if __name__ == '__main__':
    app.run(debug=True)