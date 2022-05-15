from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

conn = 'mysql://{}:{}@{}/{}'.format("root", "password", "host.docker.internal", "flask_tutorial")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conn
api = Api(app)
db = SQLAlchemy(app)

contactlist = db.Table('contactlist',
    db.Column('contactee_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('contact_id', db.Integer, db.ForeignKey('users.id'))
)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User(first_name = {self.first_name}, last_name = {self.last_name}, email = {self.email}, phone={self.phone})"

    contacts = db.relationship(
        'Users', secondary=contactlist,
        primaryjoin=(contactlist.c.contactee_id == id),
        secondaryjoin=(contactlist.c.contact_id == id),
        backref=db.backref('contactlist', lazy='dynamic'), lazy='dynamic')



user_post_args = reqparse.RequestParser()
user_post_args.add_argument("first_name", type=str, help="First name of user is required", required=True)
user_post_args.add_argument("last_name", type=str, help="Last Name of user is required", required=True)
user_post_args.add_argument("email", type=str, help="Email of user is required", required=True)
user_post_args.add_argument("phone", type=str, help="Phone number of user is required", required=True)

user_put_args = reqparse.RequestParser()
user_put_args.add_argument("first_name", type=str, help="First name of the user")
user_put_args.add_argument("last_name", type=str, help="Last name of the user")
user_put_args.add_argument("email", type=str, help="Email of ther user")
user_put_args.add_argument("phone", type=str, help="Phone of the user")

resource_fields = {
	'id': fields.Integer,
	'first_name': fields.String,
	'last_name': fields.String,
	'email': fields.String,
    'phone': fields.String
}

class UserContacts(Resource):
    @marshal_with(resource_fields)
    def get(self, phone):
        result = db.session.query(Users).filter(Users.phone == phone).first()
        return result.contacts.all()

    def put(self, phone):
        args = user_put_args.parse_args()
        result = db.session.query(Users).filter(Users.phone == phone).first()
        if not result:
            abort(404, message="Could not find user with this number")
        contact = db.session.query(Users).filter(Users.phone == args['phone']).first()
        if contact in result.contacts:
            return "Contact already present"
        result.contacts.append(contact)
        db.session.add(result)
        db.session.commit()

        return "Contact added"

class User(Resource):
    @marshal_with(resource_fields)
    def get(self, phone):
        result = db.session.query(Users).filter(Users.phone == phone).first()
        if not result:
            abort(404, message="Could not find user with this number")
        return result

    @marshal_with(resource_fields)
    def post(self):
        args = user_post_args.parse_args()
        result = db.session.query(Users).filter(Users.email==args['email'], Users.phone==args['phone']).first()
        if result:
            abort(409, message="email and phone should be unique")
        user = Users(first_name=args['first_name'], last_name=args['last_name'], email=args['email'], phone=args['phone'])
        db.session.add(user)
        db.session.commit()
        return user, 201

    @marshal_with(resource_fields)
    def put(self, phone):
        args = user_put_args.parse_args()
        result = db.session.query(Users).filter(Users.phone==phone).first()
        if not result:
            abort(404, message="User dosen't exist")

        if args['first_name']:
            result.first_name = args['first_name']
        if args['last_name']:
            result.last_name = args['last_name']
        if args['email']:
            result.email = args['email']
        if args['phone']:
            result.phone = args['phone']

        db.session.commit()

        return result

api.add_resource(User, "/user/<string:phone>", endpoint='/user/<string:phone>')
api.add_resource(User, "/user", endpoint='/user')
api.add_resource(UserContacts, "/contacts/<string:phone>", endpoint='/contacts/<string:phone>')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)