from flask import Flask, render_template, url_for, request, Blueprint
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import config
import os

URL_PREFIX = ''

if config.app['blueprint']:
	admin = Blueprint(config.root_route, __name__, template_folder='./templates', static_folder='./static')
	URL_PREFIX = 'admin.'
else:
	admin = Flask(__name__, static_url_path='')

if config.mongodb['url'] is None:
	client = MongoClient(config.mongodb['host'], config.mongodb['port'])
else:
	client = MongoClient(config.mongodb['url'])


def generate_breadcrumbs():
	breadcrumbs = []
	p = request.path.replace(url_for(URL_PREFIX+'databases'),"", 1)
	parts = p.split('/')
	for part in parts:
		breadcrumbs.append({
			"url": shorten(request.path, part),
			"name": part,
			"is_current": False
		})
	breadcrumbs[len(breadcrumbs)-1]['is_current'] = True
	return breadcrumbs


def build_collections_url(database):
	return url_for(URL_PREFIX+'collections', database=database)


def build_documents_url(collection):
	return url_for(URL_PREFIX+'documents', database=request.path.replace(url_for(URL_PREFIX+'databases')+'/',"", 1),
		collection=collection)


def build_document_url(document):
	parts = request.path.replace(url_for(URL_PREFIX+'databases')+'/',"", 1).split('/')
	return url_for(URL_PREFIX+'document', database=parts[0],
		collection=parts[1], document=document)


def shorten(s, subs):
    i = s.index(subs)
    return s[:i+len(subs)]



def msg(status, response):
	return '{ "status": "'+status+'", "response": "'+response+'" }'

def response_msg(status, response):
	return '{ "status": "'+status+'", "response": '+response+' }'








@admin.route('/'+config.root_route+'/api/update/<database>/<collection>/<document>', methods=['POST'])
def update(database, collection, document):
	if request.method == 'POST':
		try:
			content = json.loads(request.form['content'])
			if content is not None:
				client[database][collection].update({'_id': ObjectId(document)}, {'$set': content}, upsert=False)
				return msg('success', 'Success! Document has been updated.')
		except:
			return msg('error', 'Failed to update document. Is this JSON valid?')



@admin.route('/'+config.root_route+'/api/delete/<database>/<collection>/<document>', methods=['POST'])
def delete(database, collection, document):
	if request.method == 'POST':
		try:
			client[database][collection].remove({'_id': ObjectId(document)})
			return msg('success', 'Success! Document has been deleted.')
		except:
			return msg('error', 'Failed to delete document.')


@admin.route('/'+config.root_route+'/api/insert', methods=['POST'])
def insert():
	if request.method == 'POST':
		try:
			database = request.form['database']
			collection = request.form['collection']
			document = json.loads(request.form['document'])

			id = str(client[database][collection].insert_one(document).inserted_id)

			if id is not None:
				return response_msg('success', json.dumps({'msg': 'Success! Document inserted successfully.', 'id': id}))
			return msg('error', 'A strange error occured.')
		except:
			return msg('error', 'Failed to insert document. Is this JSON valid?')


@admin.route('/'+config.root_route+'/api/get_collections/<database>', methods=['POST'])
def get_collections(database):
	if request.method == 'POST':
		return response_msg('success', json.dumps(client[database].collection_names()))







@admin.route('/'+config.root_route)
def databases():
	return render_template('template.html', page='select.html', objects=client.database_names(),
	 breadcrumbs=generate_breadcrumbs(), title='Databases', build_url=build_collections_url, databases=client.database_names())


@admin.route('/'+config.root_route+'/<database>')
def collections(database):
	db = client[database]
	return render_template('template.html', page='select.html', objects=db.collection_names(),
	 breadcrumbs=generate_breadcrumbs(), title='Collections',  build_url=build_documents_url, databases=client.database_names())


@admin.route('/'+config.root_route+'/<database>/<collection>')
def documents(database, collection):
	raw_documents = client[database][collection].find({})
	documents = []
	for document in raw_documents:
		documents.append(document['_id'])
	return render_template('template.html', page='select.html', objects=documents,
	 breadcrumbs=generate_breadcrumbs(), title='Documents',  build_url=build_document_url, databases=client.database_names())


@admin.route('/'+config.root_route+'/<database>/<collection>/<document>')
def document(database, collection, document):
	document = client[database][collection].find_one({'_id': ObjectId(document)})
	doc_id = str(document['_id'])
	del document['_id']
	return render_template('template.html', page='edit.html', document=json.dumps(document, sort_keys=True, indent=4, ensure_ascii=False), 
		breadcrumbs=generate_breadcrumbs(), doc_id=doc_id, database=database, collection=collection, databases=client.database_names())


@admin.context_processor
def inject_context():
    return dict(url_prefix=URL_PREFIX)


if config.app['blueprint'] is False:
	if __name__ == '__main__':
		admin.run(host=config.app['host'], port=config.app['port'], debug=config.app['debug'])
