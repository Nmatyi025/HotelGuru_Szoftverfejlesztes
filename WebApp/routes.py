from flask import render_template, flash, redirect, url_for, session, current_app, request
from WebApp.extensions import db
from WebApp.models import User, Hotel, Role, Availability, Amenity, hotel_amenities, Room, Booking, AdditionalService
from WebApp.forms.loginForm import LoginForm
from WebApp.forms.registerform import RegisterForm
from WebApp.blueprints.user.service import UserService
from authlib.jose import jwt
from datetime import datetime, timedelta
from sqlalchemy import desc, asc
from math import ceil

def validate_token():
    if 'token' not in session:
        return False
    
    try:
        token_data = jwt.decode(
            session['token'],
            current_app.config['SECRET_KEY']
        )
        
        expiration = token_data.get('exp', 0)
        if expiration < datetime.now().timestamp():
            return False
            
        return True
    except Exception as e:
        return False

def register_routes(app):
    # Authentication routes
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if 'user_id' in session:
            return redirect(url_for('index'))
            
        form = LoginForm()
        if form.validate_on_submit():
            try:
                login_data = {
                    "email": form.username.data,
                    "password": form.password.data
                }
                
                success, response = UserService.user_login(login_data)
                
                if success:
                    session['token'] = response.get('token', '')
                    
                    try:
                        token_data = jwt.decode(
                            response.get('token', ''),
                            current_app.config['SECRET_KEY'])
                        
                        session['user_id'] = token_data.get('user_id')
                        session['user_roles'] = [role['name'] for role in token_data.get('roles', [])]
                        session['token_exp'] = token_data.get('exp')
                    except Exception as e:
                        flash(f"Token error: {str(e)}")
                        return render_template("login.html", title="Login", form=form)
                    
                    session['user_name'] = response['name']
                    
                    if form.remember_me.data:
                        session.permanent = True
                    
                    flash(f"Welcome back, {response['name']}!")
                    
                    if 'redirect_after_login' in session:
                        redirect_url = session.pop('redirect_after_login')
                        return redirect(redirect_url)
                    
                    return redirect(url_for('index'))
                else:
                    flash("Invalid email or password. Please try again.")
            except Exception as e:
                flash(f"Login error: {str(e)}")
                
        return render_template("login.html", title="Login", form=form)
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if 'user_id' in session:
            return redirect(url_for('index'))
            
        form = RegisterForm()
        if form.validate_on_submit():
            try:
                user_data = {
                    "name": form.name.data,
                    "email": form.email.data,
                    "password": form.password.data,
                    "phone": form.phone.data
                }
                
                success, response = UserService.user_registrate(user_data)
                
                if success:
                    flash("Registration successful! Please log in.")
                    return redirect(url_for('login'))
                else:
                    flash(f"Registration failed: {response}")
            except Exception as e:
                flash(f"Registration error: {str(e)}")
                
        return render_template("register.html", title="Register", form=form)

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out successfully.")
        return redirect(url_for('index'))

    def get_current_user():
        if 'user_id' in session:
            return {
                'id': session['user_id'],
                'username': session['user_name'],
                'roles': session.get('user_roles', ['User'])
            }
        return None

    # Homepage route
    @app.route("/")
    @app.route("/index")
    def index():
        hotels_data = db.session.query(Hotel).order_by(Hotel.rating.desc()).limit(6).all()
        
        hotels = []
        for hotel in hotels_data:
            hotels.append({
                'id': hotel.id,
                'name': hotel.name,
                'location': f"{hotel.city}, {hotel.country}",
                'price_per_night': get_lowest_room_price(hotel),
                'rating': hotel.rating,
                'image_url': hotel.main_photo_url
            })
        
        return render_template("index.html", 
                    title="Hotel Guru",
                    user=get_current_user(),
                    hotels=hotels)
    
    def get_lowest_room_price(hotel):
        if hotel.rooms:
            return min(room.price_per_night for room in hotel.rooms)
        return 0

    # Hotel details page
    @app.route("/hotel/<int:hotel_id>")
    def hotel_detail(hotel_id):
        check_in_str = request.args.get('check_in', '')
        check_out_str = request.args.get('check_out', '')
        
        check_in = None
        check_out = None
        
        if check_in_str:
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid check-in date format.")
        
        if check_out_str:
            try:
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid check-out date format.")
        
        hotel = db.session.get(Hotel, hotel_id)
        
        if not hotel:
            flash("Hotel not found.")
            return redirect("/index")
        
        hotel_data = {
            'id': hotel.id,
            'name': hotel.name,
            'location': f"{hotel.city}, {hotel.country}",
            'address': hotel.address,
            'description': hotel.description,
            'rating': hotel.rating,
            'image_url': hotel.main_photo_url,
            'photo_urls': hotel.photo_urls,
            'amenities': hotel.amenities
        }
        
        rooms = []
        for room in hotel.rooms:
            if not room.available:
                continue
                
            room_available = True
            if check_in and check_out:
                unavailable_dates = db.session.query(Availability).filter(
                    Availability.room_id == room.id,
                    Availability.availability_date.between(check_in, check_out),
                    Availability.is_available == False
                ).count()
                
                if unavailable_dates > 0:
                    room_available = False
                    continue
            
            room_data = {
                'id': room.id,
                'room_number': room.room_number,
                'price_per_night': room.price_per_night,
                'description': room.description,
                'available': True,
                'image_url': room.main_photo_url,
                'additional_services': []
            }
            
            for service in room.additional_services:
                room_data['additional_services'].append({
                    'name': service.name,
                    'description': service.description,
                    'price': service.price
                })
                
            rooms.append(room_data)
        
        selected_dates = {
            'check_in': check_in_str,
            'check_out': check_out_str
        }
        
        return render_template("hotel_detail.html", 
                    title=f"{hotel.name} - Hotel Guru",
                    user=get_current_user(),
                    hotel=hotel_data,
                    rooms=rooms,
                    selected_dates=selected_dates)

    def validate_token():
        if 'token' not in session:
            return False
        
        try:
            token_data = jwt.decode(session['token'], current_app.config['SECRET_KEY'])
            
            if token_data.get('exp', 0) < datetime.now().timestamp():
                return False
                
            return True
        except Exception:
            return False

    def has_role(user, role_name):
        if not user or 'roles' not in user:
            return False
        return role_name in user['roles']

    @app.template_filter('has_role')
    def has_role_filter(user, role_name):
        return has_role(user, role_name)

    # Hotels list page with search
    @app.route("/hotels")
    def hotels_list():
        check_in_str = request.args.get('check_in', '')
        check_out_str = request.args.get('check_out', '')
        location = request.args.get('location', '')
        page = request.args.get('page', 1, type=int)
        per_page = 5
        
        check_in = None
        check_out = None
        
        if check_in_str:
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid check-in date format.")
        
        if check_out_str:
            try:
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid check-out date format.")
        
        query = db.session.query(Hotel)
        
        if location:
            query = query.filter(
                db.or_(
                    Hotel.city.ilike(f'%{location}%'),
                    Hotel.country.ilike(f'%{location}%')
                )
            )
        
        hotels_data = query.all()
        available_hotels = []
        
        for hotel in hotels_data:
            available_rooms = []
            
            for room in hotel.rooms:
                room_available = True
                
                if check_in and check_out:
                    unavailable_dates = db.session.query(Availability).filter(
                        Availability.room_id == room.id,
                        Availability.availability_date.between(check_in, check_out),
                        Availability.is_available == False
                    ).count()
                    
                    if unavailable_dates > 0:
                        room_available = False
                
                if room_available and room.available:
                    available_rooms.append(room)
            
            if available_rooms:
                min_price = min(room.price_per_night for room in available_rooms) if available_rooms else 0
                
                hotel_data = {
                    'id': hotel.id,
                    'name': hotel.name,
                    'location': f"{hotel.city}, {hotel.country}",
                    'description': hotel.description,
                    'price_per_night': min_price,
                    'rating': hotel.rating,
                    'image_url': hotel.main_photo_url,
                    'available_rooms': len(available_rooms)
                }
                available_hotels.append(hotel_data)
        
        total_hotels = len(available_hotels)
        total_pages = ceil(total_hotels / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_hotels = available_hotels[start:min(end, total_hotels)]
        
        pagination = {
            'page': page,
            'pages': total_pages,
            'total': total_hotels,
            'per_page': per_page
        }
        
        amenity_ids = request.args.getlist('amenities')
        
        all_amenities = db.session.query(Amenity).all()
        
        if amenity_ids:
            query = query.join(hotel_amenities).filter(
                hotel_amenities.c.amenity_id.in_([int(a) for a in amenity_ids])
            )
        
        return render_template(
            "hotels.html",
            title="Available Hotels",
            hotels=paginated_hotels,
            pagination=pagination,
            request=request,
            user=get_current_user(),
            all_amenities=all_amenities
        )

    # Room booking process
    @app.route("/book", methods=["GET", "POST"])
    def book_room():
        room_id = request.args.get('room_id')
        check_in_str = request.args.get('check_in', '')
        check_out_str = request.args.get('check_out', '')
        
        dates_unavailable = False
        
        nights = 0
        total_price = 0
        
        if not room_id:
            flash("No room selected for booking.")
            return redirect(url_for('index'))
        
        if 'user_id' not in session:
            session['redirect_after_login'] = request.url
            flash("Please log in to book a room.")
            return redirect(url_for('login'))
        
        room = db.session.get(Room, room_id)
        if not room:
            flash("Room not found.")
            return redirect(url_for('index'))
        
        hotel = room.hotel
        
        check_in = None
        check_out = None
        
        if check_in_str:
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid check-in date format.")
        
        if check_out_str:
            try:
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid check-out date format.")
        
        if request.method == "POST":
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')
            
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
                
                nights = (check_out - check_in).days
                total_price = nights * room.price_per_night
                
            except ValueError:
                flash("Invalid date format.")
                dates_unavailable = True
                return render_template(
                    "booking.html",
                    title="Book Your Stay",
                    room=room,
                    hotel=hotel,
                    check_in=check_in_str,
                    check_out=check_out_str,
                    dates_unavailable=dates_unavailable,
                    nights=nights,
                    total_price=total_price,
                    user=get_current_user()
                )
            
            today = datetime.now().date()
            if check_in < today:
                flash("Check-in date cannot be in the past.")
                dates_unavailable = True
                return render_template(
                    "booking.html",
                    title="Book Your Stay",
                    room=room,
                    hotel=hotel,
                    check_in=check_in_str,
                    check_out=check_out_str,
                    dates_unavailable=dates_unavailable,
                    nights=nights,
                    total_price=total_price,
                    user=get_current_user()
                )
            
            if check_out <= check_in:
                flash("Check-out date must be after check-in date.")
                dates_unavailable = True
                return render_template(
                    "booking.html",
                    title="Book Your Stay",
                    room=room,
                    hotel=hotel,
                    check_in=check_in_str,
                    check_out=check_out_str,
                    dates_unavailable=dates_unavailable,
                    nights=nights,
                    total_price=total_price,
                    user=get_current_user()
                )
            
            unavailable_dates = db.session.query(Availability).filter(
                Availability.room_id == room_id,
                Availability.availability_date.between(check_in, check_out),
                Availability.is_available == False
            ).count()
            
            if unavailable_dates > 0:
                flash("Sorry, the room is not available for the selected dates. Please choose different dates.")
                dates_unavailable = True
                
                unavailable_date_records = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date.between(check_in, check_out),
                    Availability.is_available == False
                ).all()
                
                unavailable_date_list = [u.availability_date.strftime("%Y-%m-%d") for u in unavailable_date_records]
                
                return render_template(
                    "booking.html",
                    title="Book Your Stay",
                    room=room,
                    hotel=hotel,
                    check_in=check_in_str,
                    check_out=check_out_str,
                    dates_unavailable=dates_unavailable,
                    unavailable_date_list=unavailable_date_list,
                    nights=nights,
                    total_price=total_price,
                    user=get_current_user()
                )
            
            selected_service_ids = request.form.getlist('selected_services')
            selected_services = []
            service_total = 0

            if selected_service_ids:
                for service_id in selected_service_ids:
                    for service in room.additional_services:
                        if str(service.id) == service_id:
                            selected_services.append(service)
                            service_total += service.price
                            break

            nights = (check_out - check_in).days
            base_price = nights * room.price_per_night
            total_price = base_price + service_total

            booking = Booking(
                user_id=session['user_id'],
                room_id=room_id,
                start_date=check_in,
                end_date=check_out,
                status="confirmed",
                created_on=datetime.utcnow(),
                selected_services=[s.id for s in selected_services],
                service_total=service_total,
                total_price=total_price
            )

            db.session.add(booking)

            nights = (check_out - check_in).days

            for i in range(nights):
                current_date = check_in + timedelta(days=i)
                
                availability = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date == current_date
                ).first()
                
                if availability:
                    availability.is_available = False
                else:
                    new_availability = Availability(
                        room_id=room_id,
                        availability_date=current_date,
                        is_available=False
                    )
                    db.session.add(new_availability)

            db.session.commit()

            verification = db.session.query(Availability).filter(
                Availability.room_id == room_id,
                Availability.availability_date.between(check_in, check_out - timedelta(days=1)),
                Availability.is_available == False
            ).all()

            flash("Your booking has been confirmed!")
            return redirect(url_for('booking_confirmation', booking_id=booking.id))
        
        nights = 0
        total_price = 0
        
        if check_in and check_out:
            nights = (check_out - check_in).days
            total_price = nights * room.price_per_night
        
        if check_in and check_out:
            unavailable_dates = []
            date_range = (check_out - check_in).days

            for i in range(date_range):
                current_date = check_in + timedelta(days=i)
                availability = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date == current_date,
                    Availability.is_available == False
                ).first()

                if availability:
                    unavailable_dates.append(current_date.strftime("%Y-%m-%d"))

            if unavailable_dates:
                flash(f"Room is not available on the following dates: {', '.join(unavailable_dates)}")
                dates_unavailable = True

        return render_template(
            "booking.html",
            title="Book Your Stay",
            room=room,
            hotel=hotel,
            check_in=check_in_str,
            check_out=check_out_str,
            nights=nights,
            total_price=total_price,
            dates_unavailable=dates_unavailable,
            user=get_current_user()
        )

    # Booking confirmation page
    @app.route("/booking/confirmation/<int:booking_id>")
    def booking_confirmation(booking_id):
        booking = db.session.get(Booking, booking_id)
        if not booking:
            flash("Booking not found.")
            return redirect(url_for('index'))
        
        room = booking.room
        hotel = room.hotel
        
        nights = (booking.end_date - booking.start_date).days
        
        selected_services = []
        if booking.selected_services:
            for service_id in booking.selected_services:
                service_id = int(service_id) if isinstance(service_id, str) else service_id
                for service in room.additional_services:
                    if service.id == service_id:
                        selected_services.append(service)
                        break
        
        base_price = nights * room.price_per_night
        service_total = booking.service_total if booking.service_total is not None else sum(s.price for s in selected_services)
        total_price = booking.total_price if booking.total_price is not None else (base_price + service_total)
        
        return render_template(
            "booking_confirmation.html",
            title="Booking Confirmation",
            booking=booking,
            room=room,
            hotel=hotel,
            nights=nights,
            base_price=base_price,
            service_total=service_total,
            total_price=total_price,
            selected_services=selected_services,
            user=get_current_user()
        )

    # User profile page
    @app.route("/profile", methods=["GET", "POST"])
    def user_profile():
        if 'user_id' not in session:
            flash("Please log in to view your profile.")
            return redirect(url_for('login'))
        
        user = db.session.get(User, session['user_id'])
        if not user:
            flash("User not found.")
            return redirect(url_for('index'))
        
        if request.method == "POST":
            user.name = request.form.get('name', user.name)
            user.email = request.form.get('email', user.email)
            user.phone = request.form.get('phone', user.phone)
            
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if current_password and new_password and confirm_password:
                if user.verify_password(current_password):
                    if new_password == confirm_password:
                        user.password = user.hash_password(new_password)
                        flash("Password updated successfully!", "success")
                    else:
                        flash("New passwords don't match.", "danger")
                else:
                    flash("Current password is incorrect.", "danger")
            
            db.session.commit()
            flash("Profile updated successfully!", "success")
            
            session['user_name'] = user.name
            
            return redirect(url_for('user_profile'))
        
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'roles': [role.name for role in user.roles]
        }
        
        return render_template(
            "profile.html",
            title="My Profile",
            user=get_current_user(),
            user_data=user_data
        )

    # User bookings page
    @app.route("/bookings")
    def user_bookings():
        if 'user_id' not in session:
            flash("Please log in to view your bookings.")
            return redirect(url_for('login'))
        
        bookings = db.session.query(Booking).filter(
            Booking.user_id == session['user_id']
        ).order_by(Booking.created_on.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            room = booking.room
            hotel = room.hotel
            
            nights = (booking.end_date - booking.start_date).days
            total_price = nights * room.price_per_night
            
            bookings_data.append({
                'id': booking.id,
                'hotel': {
                    'id': hotel.id,
                    'name': hotel.name,
                    'image_url': hotel.main_photo_url,
                    'location': f"{hotel.city}, {hotel.country}"
                },
                'room': {
                    'id': room.id,
                    'room_number': room.room_number,
                    'price_per_night': room.price_per_night
                },
                'start_date': booking.start_date,
                'end_date': booking.end_date,
                'nights': nights,
                'total_price': total_price,
                'status': booking.status,
                'created_on': booking.created_on,
                'is_upcoming': booking.start_date >= datetime.now().date(),
                'is_active': booking.start_date <= datetime.now().date() <= booking.end_date,
                'is_past': booking.end_date < datetime.now().date()
            })
        
        return render_template(
            "bookings.html",
            title="My Bookings",
            user=get_current_user(),
            bookings=bookings_data
        )

    # Cancel booking route
    @app.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
    def cancel_booking(booking_id):
        if 'user_id' not in session:
            flash("Please log in to cancel your booking.")
            return redirect(url_for('login'))
        
        booking = db.session.get(Booking, booking_id)
        
        if not booking or booking.user_id != session['user_id']:
            flash("Booking not found or not authorized.")
            return redirect(url_for('user_bookings'))
        
        if booking.start_date <= datetime.now().date():
            flash("Cannot cancel a booking that has already started or completed.")
            return redirect(url_for('user_bookings'))
        
        booking.status = "cancelled"
        
        start_date = booking.start_date
        end_date = booking.end_date
        room_id = booking.room_id
        
        for i in range((end_date - start_date).days):
            current_date = start_date + timedelta(days=i)
            availability = db.session.query(Availability).filter(
                Availability.room_id == room_id,
                Availability.availability_date == current_date
            ).first()
            
            if availability:
                availability.is_available = True
        
        db.session.commit()
        flash("Booking cancelled successfully!")
        return redirect(url_for('user_bookings'))

    # Admin routes
    @app.route("/admin/dashboard")
    def admin_dashboard():
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        return render_template("admin/dashboard.html", user=get_current_user())

    @app.route("/admin/hotels")
    def admin_hotels():
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        hotels = db.session.query(Hotel).all()
        
        return render_template(
            "admin/hotels.html",
            title="Manage Hotels",
            user=get_current_user(),
            hotels=hotels
        )

    @app.route("/admin/users")
    def admin_users():
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        users = db.session.query(User).all()
        
        return render_template(
            "admin/users.html",
            title="Manage Users",
            user=get_current_user(),
            users=users
        )

    @app.route("/admin/bookings")
    def admin_bookings():
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        bookings = db.session.query(Booking).all()
        
        return render_template(
            "admin/bookings.html",
            title="All Bookings",
            user=get_current_user(),
            bookings=bookings
        )

    # Admin booking management
    @app.route("/admin/bookings/<int:booking_id>/edit", methods=["GET", "POST"])
    def admin_edit_booking(booking_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        booking = db.session.get(Booking, booking_id)
        if not booking:
            flash("Booking not found.")
            return redirect(url_for('admin_bookings'))
        
        room = booking.room
        hotel = room.hotel
        user = booking.user
        
        if request.method == "POST":
            new_status = request.form.get('status')
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                
                if end_date <= start_date:
                    flash("Check-out date must be after check-in date.")
                    return redirect(url_for('admin_edit_booking', booking_id=booking_id))
                
                old_nights = (booking.end_date - booking.start_date).days
                new_nights = (end_date - start_date).days
                
                if start_date != booking.start_date or end_date != booking.end_date:
                    unavailable_dates = db.session.query(Availability).filter(
                        Availability.room_id == room.id,
                        Availability.availability_date.between(start_date, end_date),
                        Availability.is_available == False
                    ).all()
                    
                    dates_from_other_bookings = []
                    for unavail in unavailable_dates:
                        is_from_current = (unavail.availability_date >= booking.start_date and 
                                           unavail.availability_date < booking.end_date)
                        if not is_from_current:
                            dates_from_other_bookings.append(unavail.availability_date)
                    
                    if dates_from_other_bookings:
                        unavailable_dates_str = [d.strftime("%Y-%m-%d") for d in dates_from_other_bookings]
                        flash(f"Cannot update booking: Room is already booked on: {', '.join(unavailable_dates_str)}")
                        return redirect(url_for('admin_edit_booking', booking_id=booking_id))
                    
                    old_availabilities = db.session.query(Availability).filter(
                        Availability.room_id == room.id,
                        Availability.availability_date.between(booking.start_date, booking.end_date - timedelta(days=1))
                    ).all()
                    
                    for avail in old_availabilities:
                        avail.is_available = True
                    
                    for i in range(new_nights):
                        current_date = start_date + timedelta(days=i)
                        avail = db.session.query(Availability).filter(
                            Availability.room_id == room.id,
                            Availability.availability_date == current_date
                        ).first()
                        
                        if avail:
                            avail.is_available = False
                        else:
                            new_avail = Availability(
                                room_id=room.id,
                                availability_date=current_date,
                                is_available=False
                            )
                            db.session.add(new_avail)
                
                booking.start_date = start_date
                booking.end_date = end_date
                booking.status = new_status
                db.session.commit()
                
                flash(f"Booking #{booking_id} has been updated successfully!")
                return redirect(url_for('admin_bookings'))
                
            except ValueError:
                flash("Invalid date format.")
                return redirect(url_for('admin_edit_booking', booking_id=booking_id))
        
        nights = (booking.end_date - booking.start_date).days
        
        return render_template(
            "admin/booking_edit.html",
            title="Edit Booking",
            user=get_current_user(),
            booking=booking,
            room=room,
            hotel=hotel,
            guest=user,
            nights=nights
        )

    @app.route("/admin/bookings/<int:booking_id>/cancel", methods=["POST"])
    def admin_cancel_booking(booking_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        booking = db.session.get(Booking, booking_id)
        if not booking:
            flash("Booking not found.")
            return redirect(url_for('admin_bookings'))
        
        booking.status = "cancelled"
        
        if booking.start_date > datetime.now().date():
            start_date = booking.start_date
            end_date = booking.end_date
            room_id = booking.room_id
            
            for i in range((end_date - start_date).days):
                current_date = start_date + timedelta(days=i)
                availability = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date == current_date
                ).first()
                
                if availability:
                    availability.is_available = True
        
        db.session.commit()
        flash(f"Booking #{booking_id} has been cancelled successfully.")
        return redirect(url_for('admin_bookings'))

    # Hotel management for admins
    @app.route("/admin/hotels/add", methods=["GET", "POST"])
    def admin_add_hotel():
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        if request.method == "POST":
            name = request.form.get('name')
            address = request.form.get('address')
            city = request.form.get('city')
            country = request.form.get('country')
            description = request.form.get('description')
            rating = float(request.form.get('rating', 0.0))
            photo_url = request.form.get('photo_url')
            
            new_hotel = Hotel(
                name=name,
                address=address,
                city=city,
                country=country,
                description=description,
                rating=rating,
                photo_urls=[photo_url] if photo_url else []
            )
            
            amenity_ids = request.form.getlist('amenities')
            if amenity_ids:
                for amenity_id in amenity_ids:
                    amenity = db.session.get(Amenity, int(amenity_id))
                    if amenity:
                        new_hotel.amenities.append(amenity)
            
            db.session.add(new_hotel)
            db.session.commit()
            
            flash(f"Hotel '{name}' has been added successfully!")
            return redirect(url_for('admin_hotels'))
        
        amenities = db.session.query(Amenity).all()
        
        return render_template(
            "admin/hotel_form.html", 
            title="Add New Hotel",
            user=get_current_user(),
            amenities=amenities,
            hotel=None,
            is_edit=False
        )

    @app.route("/admin/hotels/edit/<int:hotel_id>", methods=["GET", "POST"])
    def admin_edit_hotel(hotel_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        hotel = db.session.get(Hotel, hotel_id)
        if not hotel:
            flash("Hotel not found.")
            return redirect(url_for('admin_hotels'))
        
        if request.method == "POST":
            hotel.name = request.form.get('name')
            hotel.address = request.form.get('address')
            hotel.city = request.form.get('city')
            hotel.country = request.form.get('country')
            hotel.description = request.form.get('description')
            hotel.rating = float(request.form.get('rating', 0.0))
            
            photo_url = request.form.get('photo_url')
            if photo_url:
                if not hotel.photo_urls:
                    hotel.photo_urls = [photo_url]
                elif photo_url not in hotel.photo_urls:
                    hotel.photo_urls.append(photo_url)
            
            hotel.amenities = []
            amenity_ids = request.form.getlist('amenities')
            if amenity_ids:
                for amenity_id in amenity_ids:
                    amenity = db.session.get(Amenity, int(amenity_id))
                    if amenity:
                        hotel.amenities.append(amenity)
            
            db.session.commit()
            flash(f"Hotel '{hotel.name}' has been updated successfully!")
            return redirect(url_for('admin_hotels'))
        
        amenities = db.session.query(Amenity).all()
        
        return render_template(
            "admin/hotel_form.html", 
            title="Edit Hotel",
            user=get_current_user(),
            hotel=hotel,
            amenities=amenities,
            is_edit=True
        )

    @app.route("/admin/hotels/delete/<int:hotel_id>", methods=["POST"])
    def admin_delete_hotel(hotel_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        hotel = db.session.get(Hotel, hotel_id)
        if not hotel:
            flash("Hotel not found.")
            return redirect(url_for('admin_hotels'))
        
        has_bookings = False
        for room in hotel.rooms:
            if room.bookings and len(room.bookings) > 0:
                has_bookings = True
                break
        
        if has_bookings:
            flash(f"Cannot delete hotel '{hotel.name}' as it has existing bookings.")
            return redirect(url_for('admin_hotels'))
        
        db.session.delete(hotel)
        db.session.commit()
        flash(f"Hotel '{hotel.name}' has been deleted successfully!")
        return redirect(url_for('admin_hotels'))

    # Room management for admins
    @app.route("/admin/hotels/<int:hotel_id>/rooms", methods=["GET"])
    def admin_hotel_rooms(hotel_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        hotel = db.session.get(Hotel, hotel_id)
        if not hotel:
            flash("Hotel not found.")
            return redirect(url_for('admin_hotels'))
        
        return render_template(
            "admin/rooms.html", 
            title=f"Manage Rooms - {hotel.name}",
            user=get_current_user(),
            hotel=hotel,
            rooms=hotel.rooms
        )

    @app.route("/admin/hotels/<int:hotel_id>/rooms/add", methods=["GET", "POST"])
    def admin_add_room(hotel_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        hotel = db.session.get(Hotel, hotel_id)
        if not hotel:
            flash("Hotel not found.")
            return redirect(url_for('admin_hotels'))
        
        if request.method == "POST":
            room_number = request.form.get('room_number')
            price_per_night = float(request.form.get('price_per_night', 0))
            description = request.form.get('description')
            photo_url = request.form.get('photo_url')
            
            new_room = Room(
                room_number=room_number,
                hotel_id=hotel_id,
                price_per_night=price_per_night,
                description=description,
                available=True,
                photo_urls=[photo_url] if photo_url else []
            )
            
            service_names = request.form.getlist('service_name[]')
            service_descriptions = request.form.getlist('service_description[]')
            service_prices = request.form.getlist('service_price[]')
            
            for i in range(len(service_names)):
                if service_names[i]:
                    service = AdditionalService(
                        name=service_names[i],
                        description=service_descriptions[i] if i < len(service_descriptions) else "",
                        price=float(service_prices[i]) if i < len(service_prices) and service_prices[i] else 0
                    )
                    new_room.additional_services.append(service)
            
            db.session.add(new_room)
            db.session.commit()
            
            flash(f"Room {room_number} has been added successfully!")
            return redirect(url_for('admin_hotel_rooms', hotel_id=hotel_id))
        
        return render_template(
            "admin/room_form.html", 
            title=f"Add New Room - {hotel.name}",
            user=get_current_user(),
            hotel=hotel,
            room=None,
            is_edit=False
        )

    @app.route("/admin/rooms/<int:room_id>/edit", methods=["GET", "POST"])
    def admin_edit_room(room_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        room = db.session.get(Room, room_id)
        if not room:
            flash("Room not found.")
            return redirect(url_for('admin_hotels'))
        
        hotel = room.hotel
        
        if request.method == "POST":
            room.room_number = request.form.get('room_number')
            room.price_per_night = float(request.form.get('price_per_night', 0))
            room.description = request.form.get('description')
            room.available = 'available' in request.form
            
            photo_url = request.form.get('photo_url')
            if photo_url:
                if not room.photo_urls:
                    room.photo_urls = [photo_url]
                elif photo_url not in room.photo_urls:
                    room.photo_urls.append(photo_url)
            
            for service in room.additional_services:
                db.session.delete(service)
            
            service_names = request.form.getlist('service_name[]')
            service_descriptions = request.form.getlist('service_description[]')
            service_prices = request.form.getlist('service_price[]')
            
            room.additional_services = []
            
            for i in range(len(service_names)):
                if service_names[i]:
                    service = AdditionalService(
                        name=service_names[i],
                        description=service_descriptions[i] if i < len(service_descriptions) else "",
                        price=float(service_prices[i]) if i < len(service_prices) and service_prices[i] else 0
                    )
                    room.additional_services.append(service)
            
            db.session.commit()
            
            flash(f"Room {room.room_number} has been updated successfully!")
            return redirect(url_for('admin_hotel_rooms', hotel_id=hotel.id))
        
        return render_template(
            "admin/room_form.html", 
            title=f"Edit Room {room.room_number} - {hotel.name}",
            user=get_current_user(),
            hotel=hotel,
            room=room,
            is_edit=True
        )

    @app.route("/admin/rooms/<int:room_id>/delete", methods=["POST"])
    def admin_delete_room(room_id):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        room = db.session.get(Room, room_id)
        if not room:
            flash("Room not found.")
            return redirect(url_for('admin_hotels'))
        
        hotel_id = room.hotel_id
        
        if room.bookings and len(room.bookings) > 0:
            active_bookings = [b for b in room.bookings if b.status != 'cancelled' and b.end_date >= datetime.now().date()]
            if active_bookings:
                flash(f"Cannot delete room {room.room_number} as it has active or upcoming bookings.")
                return redirect(url_for('admin_hotel_rooms', hotel_id=hotel_id))
        
        db.session.delete(room)
        db.session.commit()
        
        flash(f"Room {room.room_number} has been deleted successfully!")
        return redirect(url_for('admin_hotel_rooms', hotel_id=hotel_id))

    # Process room booking request
    @app.route("/book_room/<int:room_id>", methods=["POST"])
    def process_room_booking(room_id):
        if 'user_id' not in session:
            flash("Please log in to book a room.")
            return redirect(url_for('login'))
        
        room = db.session.get(Room, room_id)
        if not room:
            flash("Room not found.")
            return redirect(url_for('hotels_list'))
        
        check_in_str = request.form.get('check_in')
        check_out_str = request.form.get('check_out')
        
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            
            if check_out <= check_in:
                flash("Check-out date must be after check-in date.")
                return redirect(url_for('book', room_id=room_id, check_in=check_in_str, check_out=check_out_str))
            
            unavailable_dates = []
            for i in range((check_out - check_in).days):
                current_date = check_in + timedelta(days=i)
                availability = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date == current_date
                ).first()
                
                if availability and not availability.is_available:
                    unavailable_dates.append(current_date.strftime("%Y-%m-%d"))
            
            if unavailable_dates:
                flash(f"Room is not available on the following dates: {', '.join(unavailable_dates)}")
                return redirect(url_for('book', room_id=room_id, 
                                       check_in=check_in_str, 
                                       check_out=check_out_str, 
                                       dates_unavailable=True))
            
            selected_service_ids = request.form.getlist('selected_services')
            selected_services = []
            service_total = 0
            
            if selected_service_ids:
                for service_id in selected_service_ids:
                    for service in room.additional_services:
                        if str(service.id) == service_id:
                            selected_services.append(service)
                            service_total += service.price
                            break
            
            nights = (check_out - check_in).days
            base_price = nights * room.price_per_night
            total_price = base_price + service_total
            
            booking = Booking(
                user_id=session['user_id'],
                room_id=room_id,
                start_date=check_in,
                end_date=check_out,
                status="confirmed",
                created_on=datetime.utcnow(),
                selected_services=[s.id for s in selected_services],
                service_total=service_total,
                total_price=total_price
            )
            
            db.session.add(booking)

            nights = (check_out - check_in).days

            for i in range(nights):
                current_date = check_in + timedelta(days=i)
                
                availability = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date == current_date
                ).first()
                
                if availability:
                    availability.is_available = False
                else:
                    new_availability = Availability(
                        room_id=room_id,
                        availability_date=current_date,
                        is_available=False
                    )
                    db.session.add(new_availability)

            db.session.commit()

            verification = db.session.query(Availability).filter(
                Availability.room_id == room_id,
                Availability.availability_date.between(check_in, check_out - timedelta(days=1)),
                Availability.is_available == False
            ).all()
            
            return redirect(url_for('booking_confirmation', booking_id=booking.id))
        
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('book', room_id=room_id))

    # User role management for admins
    @app.route("/admin/users/<int:user_id>/toggle_role/<role_name>", methods=["POST"])
    def admin_toggle_user_role(user_id, role_name):
        if not validate_token() or 'Administrator' not in session.get('user_roles', []):
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        if user_id == session.get('user_id') and role_name == 'Administrator':
            flash("You cannot modify your own Administrator role.")
            return redirect(url_for('admin_users'))
        
        user = db.session.get(User, user_id)
        if not user:
            flash("User not found.")
            return redirect(url_for('admin_users'))
        
        has_role = False
        for role in user.roles:
            if role.name == role_name:
                has_role = True
                break
        
        if has_role:
            success, message = UserService.remove_role_from_user(user_id, role_name)
        else:
            success, message = UserService.add_role_to_user(user_id, role_name)
        
        flash(message)
        return redirect(url_for('admin_users'))