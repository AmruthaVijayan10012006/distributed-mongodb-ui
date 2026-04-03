from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
from config import MONGO_URIS

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# Connect to MongoDB
clients = {node: MongoClient(uri) for node, uri in MONGO_URIS.items()}
dbs = {node: clients[node].get_database() for node in clients}

def get_primary_node(user_id):
    return f"node{user_id % 3 + 1}"

def get_replica_node(primary):
    nodes = ["node1","node2","node3"]
    nodes.remove(primary)
    return nodes[0]

# ----------- Routes -----------

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Enter valid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ----------- API -----------

@app.route('/insert', methods=['POST'])
def insert():
    data = request.json
    user_id = data['id']
    primary = get_primary_node(user_id)
    replica = get_replica_node(primary)
    dbs[primary].users.insert_one(data)
    dbs[replica].users.insert_one(data)
    return jsonify({"id": user_id,"name":data['name'],"message":f"Stored in {primary} and replicated to {replica}"})

@app.route('/get/<int:user_id>', methods=['GET'])
def get(user_id):
    primary = get_primary_node(user_id)
    result = dbs[primary].users.find_one({"id": user_id},{"_id":0})
    if not result:
        replica = get_replica_node(primary)
        result = dbs[replica].users.find_one({"id": user_id},{"_id":0})
    if result:
        return jsonify(result)
    return jsonify({"message":"User not found"})

@app.route('/update/<int:user_id>', methods=['PUT'])
def update(user_id):
    data = request.json
    primary = get_primary_node(user_id)
    replica = get_replica_node(primary)
    dbs[primary].users.update_one({"id":user_id},{"$set":data})
    dbs[replica].users.update_one({"id":user_id},{"$set":data})
    return jsonify({"id":user_id,"name":data.get("name",""),"message":"Updated successfully"})

@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete(user_id):
    primary = get_primary_node(user_id)
    replica = get_replica_node(primary)
    dbs[primary].users.delete_one({"id":user_id})
    dbs[replica].users.delete_one({"id":user_id})
    return jsonify({"id":user_id,"message":"Deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
    