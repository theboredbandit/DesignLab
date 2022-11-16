import os
import secrets
import razorpay
#from PIL import Image

from flask import render_template, url_for, flash, redirect, request, abort
from flaskapp import App,db,bcrypt
from flaskapp.forms import RegistrationForm,LoginForm, UpdateAccountForm, ProductForm, BookingForm, BankAccountForm
from flaskapp.models import User, Product, Booking
from flask_login import login_user, current_user, logout_user, login_required


@App.route("/")
@App.route("/about")
def about():
    return render_template('about.html', title='About')


@App.route("/home")
@login_required
def home():
    bookings = Booking.query.filter_by(buyer_id=current_user.id).all()
    bookings.sort(key=lambda x: x.date_of_booking,reverse=True)
    products = []
    for booking in bookings:
        products.append((booking, Product.query.filter_by(id=booking.product_id).first()))
    return render_template('home.html', products=products)



@App.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, contact_number = form.contact_number.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@App.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@App.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# def save_picture(form_picture):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex + f_ext
#     picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

#     output_size = (125, 125)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)

#     return picture_fn


@App.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # if form.picture.data:
        #     picture_file = save_picture(form.picture.data)
        #     current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.contact_number = form.contact_number.data        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.contact_number.data = current_user.contact_number        
    #image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', form=form)


###### route for adding new product ###### 
@App.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        if (form.quantity_kg.data>0 or form.quantity_grams.data>0):           
            product = Product(title=form.title.data, quantity_kg=form.quantity_kg.data, quantity_grams=form.quantity_grams.data, rate=form.rate.data,
                additional_info=form.additional_info.data, seller=current_user)
            db.session.add(product)
            db.session.commit()
            flash('Your product has been listed!', 'success')
            return redirect(url_for('sell'))
        else:
            flash("Quantity cannot be zero!", 'danger') 
    return render_template('add_product.html', title='New Product',
                           form=form, legend='New Product')
##########################################

@App.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', title=product.title, product=product)


@App.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.title = form.title.data
        product.quantity_kg = form.quantity_kg.data
        product.quantity_grams = form.quantity_grams.data        
        product.rate = form.rate.data
        product.additional_info = form.additional_info.data
        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.quantity_kg.data = product.quantity_kg
        form.quantity_grams.data = product.quantity_grams       
        form.rate.data = product.rate
        form.additional_info.data = product.additional_info
    return render_template('add_product.html', title='Update Product',
                           form=form, legend='Update Product')


@App.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('home'))


@App.route("/buy")
@login_required
def buy():
    products = Product.query.all()
    return render_template('buy.html', products=products)    

@App.route("/buy_product/<int:product_id>",methods=['GET', 'POST'])
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    seller = User.query.filter_by(id=product.seller_id).first()
    payment_flag = True
    if seller.account_number=='' or seller.ifsc_code=='' :
        payment_flag = False
    form = BookingForm()
    available = product.quantity_kg*1000+product.quantity_grams
    if form.validate_on_submit():
        ask = form.quantity_kg.data*1000+form.quantity_grams.data        
        if ask <= available and ask>0:
            cost = (ask*product.rate)/1000
            booking = Booking(quantity_booked_kg=form.quantity_kg.data, quantity_booked_grams=form.quantity_grams.data, 
                payment_type=form.payment_type.data,
                cost=cost, product_id=product.id, 
                buyer_id=current_user.id)
            new_quantity = available-ask
            product.quantity_kg = new_quantity//1000
            product.quantity_grams = new_quantity%1000
            # if product.quantity==0: #product should not be deleted even if its quantity is 0 cuz it has to appear in bookings
            #     db.session.delete(product)
            if form.payment_type.data=='2':
                db.session.add(booking)
                db.session.commit()
                flash('Booking successful! Total cost = INR {:.2f}'.format(cost), 'success')
                return redirect(url_for('home'))
            else:
                client = razorpay.Client(auth=("rzp_test_3qAwJFpH31deY0", "TveSwn663Nvo2GL2U7xCImP9"))
                DATA = {
                    "amount": int(booking.cost*100),
                    "currency": "INR",
                    # "receipt": "receipt#1",
                    # "notes": {
                    #     "key1": "value3",
                    #     "key2": "value2"
                    # }
                    "payment_capture": "1"
                }
                payment = client.order.create(data=DATA)       
                return render_template('pay.html',payment=payment, user=current_user,quantity_booked_kg=form.quantity_kg.data, quantity_booked_grams=form.quantity_grams.data, 
                payment_type=form.payment_type.data,
                cost=cost, product_id=product.id, 
                buyer_id=current_user.id)
        elif ask==0:
            flash("Quantity cannot be 0!",'danger')
        else:
            message = "The quantity you have entered exceeds availability. Please enter a quantity below {:.1f} kg".format(available/1000)
            flash(message, 'danger')
    return render_template('buy_product.html', title='Buy Product',
                           form=form, product=product, legend='Buy Product', flag=payment_flag)


@App.route("/booking/<int:booking_id>")
def booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    product_id = booking.product_id
    product = Product.query.filter_by(id=product_id).first()
    return render_template('booking.html', title=product.title, product=product, booking=booking)

# @App.route("/booking/<int:booking_id>/update", methods=['GET', 'POST'])
# @login_required
# def update_booking(booking_id):
#     booking = Booking.query.get_or_404(booking_id)
#     original_quantity_booked_kg = booking.quantity_booked_kg
#     original_quantity_booked_grams = booking.quantity_booked_grams    
#     product=Product.query.filter_by(id=booking.product_id).first()
#     form = BookingForm()
#     available = (product.quantity_kg+original_quantity_booked_kg)*1000+product.quantity_grams+original_quantity_booked_grams
#     if form.validate_on_submit():
#         ask = form.quantity_kg.data*1000+form.quantity_grams.data     
#         if ask<=available and ask>0:    
#             booking.quantity_booked_kg = form.quantity_kg.data
#             booking.quantity_booked_grams = form.quantity_grams.data
#             booking.cost = (ask*product.rate)/1000
#             new_quantity = available-ask
#             product.quantity_kg = new_quantity//1000
#             product.quantity_grams = new_quantity%1000
#             db.session.commit()
#             flash('Your booking has been updated!', 'success')
#             return redirect(url_for('booking', booking_id=booking.id))
#         elif ask==0:
#             flash("Quantity cannot be 0!",'danger')            
#         else:
#             message = "The quantity you have entered exceeds availability. Please enter a quantity below {:0.1f} kg".format(available/1000)
#             flash(message, 'danger')
#     elif request.method == 'GET':
#         form.quantity_kg.data = booking.quantity_booked_kg
#         form.quantity_grams.data = booking.quantity_booked_grams        
#     return render_template('buy_product.html', title='Update Booking',
#                            form=form, legend='Update Booking', product=product)    


@App.route("/booking/<int:booking_id>/delete", methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    product=Product.query.filter_by(id=booking.product_id).first()
    if booking.buyer_id != current_user.id:
        abort(403)
    new_quantity=(product.quantity_kg+booking.quantity_booked_kg)*1000 + product.quantity_grams+booking.quantity_booked_grams    
    product.quantity_kg = new_quantity//1000
    product.quantity_grams = new_quantity%1000 
    if booking.payment_type=='1': #online payment
        seller=User.query.filter_by(id=product.seller_id).first()
        seller.amount_owed=seller.amount_owed-booking.cost
    db.session.delete(booking)
    db.session.commit()
    flash('Your booking has been deleted!', 'success')
    return redirect(url_for('home'))    


@App.route("/sell")
@login_required
def sell():
    products = Product.query.filter_by(seller_id=current_user.id).all()
    products.sort(key=lambda x: x.date_listed,reverse=True)    
    return render_template('sell.html', products=products)      

@App.route("/orders_received")
@login_required
def orders_received():
    bookings=Booking.query.all()
    bookings.sort(key=lambda x: x.date_of_booking,reverse=True)    
    orders_received=[]
    for booking in bookings:
        product=Product.query.filter_by(id=booking.product_id).first()
        if(product.seller_id==current_user.id):
            orders_received.append((product.title,booking))
    return render_template('orders_received.html', orders_received=orders_received)       

@App.route("/bank_account_details", methods=['GET', 'POST'])
@login_required
def bank_account_details():
    form = BankAccountForm()
    if form.validate_on_submit():
        current_user.account_number = form.account_number.data
        current_user.ifsc_code = form.ifsc_code.data
        db.session.commit()
        flash('Your bank account details have been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.account_number.data = current_user.account_number
        form.ifsc_code.data = current_user.ifsc_code
    return render_template('bank_account_details.html', title='Bank Account details', legend= 'Bank Account details',form=form)    

@App.route("/payment_failure/<int:product_id>", methods=['GET', 'POST'])
@login_required
def payment_failure(product_id):
    flash('Your payment failed! Please re-try.', 'danger')    
    return redirect(url_for('buy_product',product_id=product_id))  

@App.route("/payment_success/<quantity_booked_kg>/<quantity_booked_grams>/<payment_type>/<cost>/<product_id>/<buyer_id>", methods=['GET', 'POST'])
@login_required
def payment_success(quantity_booked_kg,quantity_booked_grams,payment_type,cost,product_id,buyer_id):
    booking = Booking(quantity_booked_kg=quantity_booked_kg, quantity_booked_grams=quantity_booked_grams, 
                payment_type=payment_type,
                cost=cost, product_id=product_id, 
                buyer_id=buyer_id)

    product = Product.query.get_or_404(product_id)
    seller = User.query.filter_by(id=product.seller_id).first()
    seller.amount_owed=seller.amount_owed+float(booking.cost)
    db.session.add(booking)
    db.session.commit()    
    flash('Booking successful! Total cost = INR {:.2f}'.format(booking.cost), 'success')
    return redirect(url_for('home')) 
