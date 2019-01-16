from flask import Flask, jsonify, abort, make_response, request,render_template, url_for, flash, redirect
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
from flask_jwt_extended import JWTManager
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/tododb'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'apple'

db = SQLAlchemy(app)

class Tasks(db.Model):
    __tablename__ ='tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, primary_key=True)
    status = db.Column(db.Boolean, primary_key=True)
    user_id = db.Column(db.Integer)

    def __repr__(self):
        return "Users(title: %r,status: %r)" %(self.title,self.status)
    
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(500))

    def __repr__(self):
        return "Users(email: %r,password: %r)" %(self.email,self.password)


@app.route("/")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    user = Users.query.filter_by(email=form.email.data)
    

    if user.count() == 0 :
        
        new_user = Users(email=form.email.data,password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        if form.validate_on_submit():
            flash('Account created for ' + form.email.data, 'success')
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == form.email.data and form.password.data == form.password.data:
            flash('You have been logged in!', 'success')
            return redirect(url_for('alltasks'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/alltasks', methods=['GET', 'POST'])
def alltasks():

    tasks = Tasks.query.all()

    output = []
    print(tasks)
    
    for task in tasks:

        tasks_data = {}
        tasks_data['id'] = task.id
        tasks_data['title'] = task.title
        tasks_data['status'] = task.status
        output.append(tasks_data)
    return render_template('alltasks.html', title='Login')

@app.route('/get_tasks', methods=['GET'])

def get_tasks(user):
    tasks = Tasks.query.filter_by(user_id=user.id)
    
    if tasks.count() == 0:
        return jsonify({'message': 'No tasks found the current user'})
    output = []
    for task in tasks:

        tasks_data = {}
        tasks_data['id'] = task.id
        tasks_data['title'] = task.title
        tasks_data['description'] = task.description
        tasks_data['done'] = task.done
        output.append(tasks_data)
    return jsonify({'tasks': output})


@app.route('/todo/api/create_tasks', methods=['POST'])
# @token_required
def create_task(user):

    data = request.get_json()
   
    new_task = Tasks(title=data['title'],description=data['description'],done=data['done'],user_id=user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'The New Task has been created'})

@app.route('/todo/api/tasks/<int:id>', methods=['PUT'])
# @token_required
def update_task(user,id):

    task = Tasks.query.filter_by(user_id=user.id).first()

    if not task:
        return jsonify({'Message': 'No task to update'})
 
    data = request.get_json()
    d =  bool(data['done'])
    task.done = d
    db.session.commit()
    return jsonify({'Message': 'The task has been updated'})

@app.route('/todo/api/tasks/<int:id>', methods=['DELETE'])
# @token_required
def delete_task(user,id):
    task = Tasks.query.filter_by(id=userid).first()

    if not task:
        return jsonify({'Message': 'No task to delete'})

    db.session.delete(task)
    db.session.commit()

    return jsonify({'Message': 'Task has been deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)