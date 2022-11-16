from datetime import datetime
from flaskapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_number =  db.Column(db.String(10), unique=True, nullable=False) 
    account_number =  db.Column(db.String(30), nullable=True, default='')  
    ifsc_code = db.Column(db.String(30), nullable=True, default='')
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    amount_owed = db.Column(db.Float, nullable=False, default=0)
    products = db.relationship('Product', backref='seller', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_listed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ####### units of the product #######  
    quantity_kg = db.Column(db.Integer, nullable=False, default=0)
    quantity_grams = db.Column(db.Integer, nullable=False, default=0) 
    ####################################   
    rate = db.Column(db.Float, nullable=False)
    additional_info = db.Column(db.Text, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Product('{self.title}', '{self.date_listed}')"


class Booking(db.Model): #made by buyer
    id=db.Column(db.Integer, primary_key=True)
    quantity_booked_kg = db.Column(db.Integer, nullable=False)
    quantity_booked_grams = db.Column(db.Integer, nullable=False, default=0)    
    date_of_booking = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_type = db.Column(db.String(), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Booking('{self.id}', '{self.quantity_booked}', '{self.date_of_booking}')"

