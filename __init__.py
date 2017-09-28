from flask import Flask, render_template, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

app = Flask(__name__, static_url_path='')
client = MongoClient()


def generate_breadcrumbs():
	breadcrumbs = []
	p = request.path.replace(url_for('databases'),"", 1)
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
	return url_for('collections', database=database)


def build_documents_url(collection):
	return url_for('documents', database=request.path.replace(url_for('databases')+'/',"", 1),
		collection=collection)


def build_document_url(document):
	parts = request.path.replace(url_for('databases')+'/',"", 1).split('/')
	return url_for('document', database=parts[0],
		collection=parts[1], document=document)


def shorten(s, subs):
    i = s.index(subs)
    return s[:i+len(subs)]



def msg(status, response):
	return '{ "status": "'+status+'", "response": "'+response+'" }'








@app.route('/admin/api/update/<database>/<collection>/<document>', methods=['POST'])
def update(database, collection, document):
	if request.method == 'POST':
		content = json.loads(request.form['content'])
		if content is not None:
			client[database][collection].update({'_id': ObjectId(document)}, {'$set': content}, upsert=False)
			return msg('success', 'Success! Document has been updated.')
		return msg('error', 'A strange error occured. Is this JSON valid?')



@app.route('/admin/api/delete/<database>/<collection>/<document>', methods=['POST'])
def delete(database, collection, document):
	if request.method == 'POST':
		client[database][collection].remove({'_id': ObjectId(document)})
		return msg('success', 'delete successful')











@app.route('/admin')
def databases():
	return render_template('template.html', page='select.html', objects=client.database_names(),
	 breadcrumbs=generate_breadcrumbs(), title='Databases', build_url=build_collections_url)


@app.route('/admin/<database>')
def collections(database):
	db = client[database]
	return render_template('template.html', page='select.html', objects=db.collection_names(),
	 breadcrumbs=generate_breadcrumbs(), title='Collections',  build_url=build_documents_url)


@app.route('/admin/<database>/<collection>')
def documents(database, collection):
	raw_documents = client[database][collection].find({})
	documents = []
	for document in raw_documents:
		documents.append(document['_id'])
	return render_template('template.html', page='select.html', objects=documents,
	 breadcrumbs=generate_breadcrumbs(), title='Documents',  build_url=build_document_url)


@app.route('/admin/<database>/<collection>/<document>')
def document(database, collection, document):
	document = client[database][collection].find_one({'_id': ObjectId(document)})
	doc_id = str(document['_id'])
	del document['_id']
	return render_template('template.html', page='edit.html', document=json.dumps(document, sort_keys=True, indent=4, ensure_ascii=False), 
		breadcrumbs=generate_breadcrumbs(), doc_id=doc_id, database=database, collection=collection)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)