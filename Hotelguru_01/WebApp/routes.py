from WebApp import app, db
from flask import render_template, flash, redirect
from WebApp.hotelmanager import HotelManager
from WebApp.models import Hotel
from WebApp.forms.hotelform import HotelForm
from WebApp.forms.searchform import SearchForm

hm = HotelManager(db)

@app.route("/index")
@app.route("/")
def index():
    page = "Hotel Manager - Welcome"
    return render_template('index.html', page_title=page)

@app.route("/hotels", methods=["GET", "POST"])
def hotels():
    page = "Hotel Manager - Hotels"
    
    search_form = SearchForm()
    hotels = []
    
    if search_form.validate_on_submit():
        hotels = hm.search_hotels(search_form.search_text.data)
        flash("Search results for '{}'!".format(search_form.search_text.data))
    else:
        hotels = hm.hotels
    
    return render_template(
        'hotels.html',
        page_title=page,
        search_form=search_form,
        hotels=hotels
    )

@app.route("/hotel/<id>")
def hotel(id: int):
    page = "Hotel Manager - Hotel Details"
    
    hotel = hm.get_hotel(id)
    return render_template(
        'hotel.html',
        page_title=page,
        hotel=hotel
    )

@app.route("/hotel/add", methods=["GET", "POST"])
def new_hotel():
    page = "Hotel Manager - New Hotel"
    form = HotelForm()

    if form.validate_on_submit():
        hm.add_hotel(Hotel.from_form(form))
        flash("Hotel '{}' added!".format(form.name.data))
        return redirect("/hotels")
    
    return render_template(
        'hotel.html',
        page_title=page,
        form=form,
        add=True
    )

@app.route("/hotel/delete/<id>")
def delete_hotel(id: int):
    hotel = hm.get_hotel(id)
    hotel_name = hotel.name
    hm.delete_hotel(hotel)
    flash("Hotel '{}' deleted!".format(hotel_name))
    return redirect("/hotels")
