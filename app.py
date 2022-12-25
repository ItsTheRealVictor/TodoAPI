from flask import Flask, request, jsonify, render_template
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)

app.config['SECRET_KEY'] = "farts"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_BINDS'] = {'testDB' : 'sqlite:///test_todo.db'}


app.debug = True
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = SQLAlchemy(app)
app.app_context().push()

migrate = Migrate(app, db)

class Todo(db.Model):
    """Todo Model"""

    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done
        }

    def __repr__(self):
        return f"<Todo {self.id} title={self.title} done={self.done} >"


@app.route('/api/todos')
def list_all_todos():
    all_todos = [todo.serialize() for todo in Todo.query.all()]
    return jsonify(todos=all_todos)


@app.route('/api/todos/<int:id>')
def show_todo(id):
    todo = Todo.query.get_or_404(id)
    return jsonify(todo=todo.serialize())

@app.route('/api/todos', methods=['POST'])
def create_todo():
    new_todo = Todo(title=request.json["title"])
    
    db.session.add(new_todo)
    db.session.commit()
    
    return (jsonify(todo=new_todo.serialize()), 201)

@app.route('/api/todos/<int:id>', methods=['PATCH'])
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.title = request.json.get('title', todo.title) # todo.title is the default value incase 'title' isn't found or provided
    todo.done = request.json.get('done', todo.done) # same as above
    
    db.session.commit()
    return jsonify(todo=todo.serialize())


@app.route('/api/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify(msg='deleted')