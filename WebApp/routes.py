from flask import render_template, flash, redirect, url_for, session, current_app, request
from WebApp.extensions import db
from WebApp.models import User, Hotel, Role, Availability, Amenity, hotel_amenities, Room, Booking
from WebApp.forms.loginForm import LoginForm
from WebApp.forms.registerform import RegisterForm
from WebApp.blueprints.user.service import UserService
from authlib.jose import jwt
from datetime import datetime, timedelta
from sqlalchemy import desc, asc
from math import ceil

def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        # If user is already logged in, redirect to homepage
        if 'user_id' in session:
            return redirect(url_for('index'))
            
        form = LoginForm()
        if form.validate_on_submit():
            try:
                login_data = {
                    "email": form.username.data,  # Using username field for email
                    "password": form.password.data
                }
                
                success, response = UserService.user_login(login_data)
                
                if success:
                    # Store token in session
                    session['token'] = response.get('token', '')
                    
                    # Decode token to get user info
                    try:
                        token_data = jwt.decode(
                            response.get('token', ''),
                            current_app.config['SECRET_KEY'])
                        
                        # Store user info from token
                        session['user_id'] = token_data.get('user_id')
                        session['user_roles'] = [role['name'] for role in token_data.get('roles', [])]
                        session['token_exp'] = token_data.get('exp')
                    except Exception as e:
                        flash(f"Token error: {str(e)}")
                        return render_template("login.html", title="Login", form=form)
                    
                    # Store user info in session
                    session['user_name'] = response['name']
                    
                    if form.remember_me.data:
                        # Make session permanent (lasts for 31 days by default)
                        session.permanent = True
                    
                    flash(f"Welcome back, {response['name']}!")
                    
                    # Check if we need to redirect to a specific page after login
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
        # If user is already logged in, redirect to homepage
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
        # Clear all session data
        session.clear()
        flash("You have been logged out successfully.")
        return redirect(url_for('index'))

    # Helper function to get the current user
    def get_current_user():
        if 'user_id' in session:
            return {
                'id': session['user_id'],
                'username': session['user_name'],
                'roles': session.get('user_roles', ['User'])
            }
        return None

    @app.route("/")
    @app.route("/index")
    def index():
        # Fetch hotels from the database
        hotels_data = db.session.query(Hotel).order_by(Hotel.rating.desc()).limit(6).all()
        
        # Format hotel data for the template
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
    
    # Helper function to get the lowest room price for a hotel
    def get_lowest_room_price(hotel):
        if hotel.rooms:
            return min(room.price_per_night for room in hotel.rooms)
        return 0

    @app.route("/hotel/<int:hotel_id>")
    def hotel_detail(hotel_id):
        
        # Get date parameters from query string
        check_in_str = request.args.get('check_in', '')
        check_out_str = request.args.get('check_out', '')
        
        # Convert dates if provided
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
        
        # Fetch the specific hotel from the database
        hotel = db.session.get(Hotel, hotel_id)
        
        if not hotel:
            flash("Hotel not found.")
            return redirect("/index")
        
        # Format hotel data for the template
        hotel_data = {
            'id': hotel.id,
            'name': hotel.name,
            'location': f"{hotel.city}, {hotel.country}",
            'address': hotel.address,
            'description': hotel.description,
            'rating': hotel.rating,
            'image_url': hotel.main_photo_url,
            'photo_urls': hotel.photo_urls,
            'amenities': hotel.amenities  # Add this line
        }
        
        # Get all rooms for this hotel with their additional services
        rooms = []
        for room in hotel.rooms:
            # Check if room is generally available
            if not room.available:
                continue
                
            # Check date-specific availability if dates were provided
            room_available = True
            if check_in and check_out:
                # Get all unavailable dates for this room in the requested period
                unavailable_dates = db.session.query(Availability).filter(
                    Availability.room_id == room.id,
                    Availability.availability_date.between(check_in, check_out),
                    Availability.is_available == False
                ).count()
                
                # If any date in the range is unavailable, the room is not available
                if unavailable_dates > 0:
                    room_available = False
                    continue  # Skip this room
            
            # Room is available - add it to the list
            room_data = {
                'id': room.id,
                'room_number': room.room_number,
                'price_per_night': room.price_per_night,
                'description': room.description,
                'available': True,  # We know it's available since we filtered
                'image_url': room.main_photo_url,
                'additional_services': []
            }
            
            # Add additional services
            for service in room.additional_services:
                room_data['additional_services'].append({
                    'name': service.name,
                    'description': service.description,
                    'price': service.price
                })
                
            rooms.append(room_data)
        
        # Pass the dates to the template for booking form
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
        if 'token' not in session or 'token_exp' not in session:
            return False
        
        # Check if token is expired
        current_time = int(datetime.now().timestamp())
        if session['token_exp'] < current_time:
            # Token expired, clear session
            session.clear()
            return False
        
        return True

    @app.route("/admin/hotels")
    def admin_hotels():
        if not validate_token():
            flash("Your session has expired. Please log in again.")
            return redirect(url_for('login'))
        
        # Check role
        if 'user_roles' not in session or 'Administrator' not in session['user_roles']:
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for('index'))
        
        # Admin-only code here
        # ...
        return render_template("admin/hotels.html", user=get_current_user())

    @app.route("/hotels")
    def hotels_list():
        # Get search parameters
        check_in_str = request.args.get('check_in', '')
        check_out_str = request.args.get('check_out', '')
        location = request.args.get('location', '')
        page = request.args.get('page', 1, type=int)  # Get current page
        per_page = 5  # Number of hotels per page
        
        # Convert dates if provided
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
        
        # Build base query
        query = db.session.query(Hotel)
        
        # Apply location filter if provided
        if location:
            query = query.filter(
                db.or_(
                    Hotel.city.ilike(f'%{location}%'),
                    Hotel.country.ilike(f'%{location}%')
                )
            )
        
        # Get hotels matching location criteria
        hotels_data = query.all()
        available_hotels = []
        
        # Filter hotels based on room availability
        for hotel in hotels_data:
            available_rooms = []
            
            for room in hotel.rooms:
                # Default: room is available
                room_available = True
                
                # Check date-specific availability if dates were provided
                if check_in and check_out:
                    # Get all unavailable dates for this room in the requested period
                    unavailable_dates = db.session.query(Availability).filter(
                        Availability.room_id == room.id,
                        Availability.availability_date.between(check_in, check_out),
                        Availability.is_available == False
                    ).count()
                    
                    # If any date in the range is unavailable, the room is not available
                    if unavailable_dates > 0:
                        room_available = False
                
                # Only include available rooms
                if room_available and room.available:  # Check both date availability and general room availability
                    available_rooms.append(room)
            
            # Include hotel if it has at least one available room
            if available_rooms:
                # Find lowest price among available rooms
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
        
        # Calculate pagination
        total_hotels = len(available_hotels)
        total_pages = ceil(total_hotels / per_page)
        
        # Get the slice of hotels for current page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_hotels = available_hotels[start:min(end, total_hotels)]
        
        # Create pagination object
        pagination = {
            'page': page,
            'pages': total_pages,
            'total': total_hotels,
            'per_page': per_page
        }
        
        # Get amenity filters
        amenity_ids = request.args.getlist('amenities')
        
        # Fetch all amenities for the filter form
        all_amenities = db.session.query(Amenity).all()
        
        # Filter by amenities if selected
        if amenity_ids:
            query = query.join(hotel_amenities).filter(
                hotel_amenities.c.amenity_id.in_([int(a) for a in amenity_ids])
            )
        
        return render_template(
            "hotels.html",
            title="Available Hotels",
            hotels=paginated_hotels,  # Send only the hotels for current page
            pagination=pagination,    # Add pagination data
            request=request,          # Pass request for maintaining filters in pagination links
            user=get_current_user(),
            all_amenities=all_amenities  # Pass all amenities to the template
        )

    @app.route("/book", methods=["GET", "POST"])
    def book_room():
        # Get the room ID and dates from the query parameters
        room_id = request.args.get('room_id')
        check_in_str = request.args.get('check_in', '')
        check_out_str = request.args.get('check_out', '')
        
        # Add this variable to track date availability
        dates_unavailable = False
        
        # Initialize these variables at the start of the function
        nights = 0
        total_price = 0
        
        if not room_id:
            flash("No room selected for booking.")
            return redirect(url_for('index'))
        
        # Check if user is logged in
        if 'user_id' not in session:
            # Store the booking URL so we can redirect back after login
            session['redirect_after_login'] = request.url
            flash("Please log in to book a room.")
            return redirect(url_for('login'))
        
        # Fetch the room details
        room = db.session.get(Room, room_id)
        if not room:
            flash("Room not found.")
            return redirect(url_for('index'))
        
        # Fetch the hotel details
        hotel = room.hotel
        
        # Convert dates if provided
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
        
        # Handle form submission
        if request.method == "POST":
            # Get form data - always use the form values for POST requests
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')
            
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
                
                # Calculate nights and price right after parsing dates successfully
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
                    nights=nights,               # Add these
                    total_price=total_price,     # Add these
                    user=get_current_user()
                )
            
            # Validate dates
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
                    nights=nights,               # Add these
                    total_price=total_price,     # Add these
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
                    nights=nights,               # Add these
                    total_price=total_price,     # Add these
                    user=get_current_user()
                )
            
            # Check if the room is available for the selected dates
            unavailable_dates = db.session.query(Availability).filter(
                Availability.room_id == room_id,
                Availability.availability_date.between(check_in, check_out),
                Availability.is_available == False
            ).count()
            
            if unavailable_dates > 0:
                flash("Sorry, the room is not available for the selected dates. Please choose different dates.")
                dates_unavailable = True
                
                # Calculate which dates are unavailable to show more detailed info
                unavailable_date_records = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date.between(check_in, check_out),
                    Availability.is_available == False
                ).all()
                
                unavailable_date_list = [u.availability_date.strftime("%Y-%m-%d") for u in unavailable_date_records]
                
                # Instead of redirecting, stay on the booking page
                return render_template(
                    "booking.html",
                    title="Book Your Stay",
                    room=room,
                    hotel=hotel,
                    check_in=check_in_str,
                    check_out=check_out_str,
                    dates_unavailable=dates_unavailable,
                    unavailable_date_list=unavailable_date_list,
                    nights=nights,               # Add these
                    total_price=total_price,     # Add these
                    user=get_current_user()
                )
            
            # If everything is fine, continue with booking creation
            # Create the booking
            booking = Booking(
                user_id=session['user_id'],
                room_id=room_id,
                start_date=check_in,
                end_date=check_out,
                status="confirmed",
                created_on=datetime.utcnow()
            )

            db.session.add(booking)

            # Mark the dates as unavailable
            for day in range(nights):
                current_date = check_in + timedelta(days=day)
                
                # Check if record already exists
                availability = db.session.query(Availability).filter(
                    Availability.room_id == room_id,
                    Availability.availability_date == current_date
                ).first()
                
                if availability:
                    availability.is_available = False
                else:
                    availability = Availability(
                        room_id=room_id,
                        availability_date=current_date,
                        is_available=False
                    )
                    db.session.add(availability)

            db.session.commit()

            flash("Your booking has been confirmed!")
            return redirect(url_for('booking_confirmation', booking_id=booking.id))
        
        # For GET request, show the booking form
        # Calculate number of nights and total price (if dates are provided)
        nights = 0
        total_price = 0
        
        if check_in and check_out:
            nights = (check_out - check_in).days
            total_price = nights * room.price_per_night
        
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

    @app.route("/booking/confirmation/<int:booking_id>")
    def booking_confirmation(booking_id):
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Fetch the booking details
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.user_id != session['user_id']:
            flash("Booking not found.")
            return redirect(url_for('index'))
        
        # Fetch room and hotel details
        room = booking.room
        hotel = room.hotel
        
        # Calculate number of nights and total price
        nights = (booking.end_date - booking.start_date).days
        total_price = nights * room.price_per_night
        
        return render_template(
            "booking_confirmation.html",
            title="Booking Confirmation",
            booking=booking,
            room=room,
            hotel=hotel,
            nights=nights,
            total_price=total_price,
            user=get_current_user()
        )

    @app.route("/profile", methods=["GET", "POST"])
    def user_profile():
        # Check if user is logged in
        if 'user_id' not in session:
            flash("Please log in to view your profile.")
            return redirect(url_for('login'))
        
        # Get the user data
        user = db.session.get(User, session['user_id'])
        if not user:
            flash("User not found.")
            return redirect(url_for('index'))
        
        # Handle form submission for profile update
        if request.method == "POST":
            # Update user information
            user.name = request.form.get('name', user.name)
            user.email = request.form.get('email', user.email)
            user.phone = request.form.get('phone', user.phone)
            
            # Check if password update is requested
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if current_password and new_password and confirm_password:
                # Verify current password
                if user.verify_password(current_password):
                    if new_password == confirm_password:
                        user.password = user.hash_password(new_password)
                        flash("Password updated successfully!", "success")
                    else:
                        flash("New passwords don't match.", "danger")
                else:
                    flash("Current password is incorrect.", "danger")
            
            # Save changes
            db.session.commit()
            flash("Profile updated successfully!", "success")
            
            # Update session
            session['user_name'] = user.name
            
            return redirect(url_for('user_profile'))
        
        # Prepare user data for the template
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

    @app.route("/bookings")
    def user_bookings():
        # Check if user is logged in
        if 'user_id' not in session:
            flash("Please log in to view your bookings.")
            return redirect(url_for('login'))
        
        # Get the user's bookings
        bookings = db.session.query(Booking).filter(
            Booking.user_id == session['user_id']
        ).order_by(Booking.created_on.desc()).all()
        
        # Format bookings data
        bookings_data = []
        for booking in bookings:
            # Get the room and hotel info
            room = booking.room
            hotel = room.hotel
            
            # Calculate number of nights and total price
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

    @app.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
    def cancel_booking(booking_id):
        # Check if user is logged in
        if 'user_id' not in session:
            flash("Please log in to cancel your booking.")
            return redirect(url_for('login'))
        
        # Get the booking
        booking = db.session.get(Booking, booking_id)
        
        # Check if booking exists and belongs to user
        if not booking or booking.user_id != session['user_id']:
            flash("Booking not found or not authorized.")
            return redirect(url_for('user_bookings'))
        
        # Check if booking is upcoming (can't cancel past or active bookings)
        if booking.start_date <= datetime.now().date():
            flash("Cannot cancel a booking that has already started or completed.")
            return redirect(url_for('user_bookings'))
        
        # Update booking status
        booking.status = "cancelled"
        
        # Restore availability for these dates
        start_date = booking.start_date
        end_date = booking.end_date
        room_id = booking.room_id
        
        # Mark the dates as available again
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