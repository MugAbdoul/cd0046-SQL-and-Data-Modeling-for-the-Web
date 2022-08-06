#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import date, datetime
from email.policy import default
import json
from posixpath import split
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)



# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]

  city_states = Venue.query.distinct(Venue.city, Venue.state).all()

  for city_state in city_states:
        
        res = {
          "city": city_state.city,
          "state": city_state.state,
          "venues": []
        }

        venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == city_state.city, Venue.state == city_state.state).all()

        for venue in venues:
            
            shows = db.session.query(Show.start_time).filter(Show.venue_id == venue.id).all()
            res["venues"].append({
              "id": venue.id,
              "name":  venue.name,
              "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), shows)))
            })
        
        data.append(res)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term =request.form["search_term"]
  venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  
  response={
    "count": len(venues),
    "data": []
  }
  
  for venue in venues:
        count = 0
        for show in venue.shows:
              if show.start_time > datetime.now():
                    count += 1
        response["data"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": count,
        })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()


  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
  }


  for show in shows_query:
    if show.start_time > datetime.now():
          data["upcoming_shows"].append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
          })
    else:
          data["past_shows"].append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
          })
  
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  if form.validate_inputs():
    try:
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data, facebook_link=form.facebook_link.data, website_link=form.website_link.data,seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  else:
      flash('An error occurred. Please enter valid inputs')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue " + venue.name + " was deleted successfully!")
  except:
      db.session.rollback()
      flash("Something went wrong!")
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = db.session.query(Artist).with_entities(Artist.id, Artist.name).order_by(Artist.id.asc()).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term =request.form["search_term"]
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  
  response={
    "count": len(artists),
    "data": []
  }

  
  for artist in artists:
        count = 0
        for show in artist.shows:
              if show.start_time > datetime.now():
                    count += 1
        response["data"].append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": count,
        }) 

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all() 

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
  }


  for show in shows_query:
    if show.start_time > datetime.now():
          data["upcoming_shows"].append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
          })
    else:
          data["past_shows"].append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
          })
  
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  data = Artist.query.get(artist_id)

  if data:
    artist={
      "id": data.id,
      "name": data.name,
      "genres": data.genres,
      "city": data.city,
      "state": data.state,
      "phone": data.phone,
      "website": data.website_link,
      "facebook_link": data.facebook_link,
      "seeking_venue": data.seeking_venue,
      "seeking_description": data.seeking_description,
      "image_link": data.image_link
    } 
  else:
    artist = {}

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  data = Artist.query.get(artist_id)
  form = ArtistForm(request.form)

  data.id = artist_id
  data.name = form.name.data
  data.genres = form.genres.data
  data.city = form.city.data
  data.state = form.state.data
  data.phone = form.phone.data
  data.website_link = form.website_link.data
  data.facebook_link = form.facebook_link.data
  data.seeking_venue = form.seeking_venue.data
  data.seeking_description = form.seeking_description.data
  data.image_link = form.image_link.data

  try:
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  data = Venue.query.get(venue_id)

  if data:
    venue={
      "id": data.id,
      "name": data.name,
      "genres": data.genres,
      "address": data.address,
      "city": data.city,
      "state": data.state,
      "phone": data.phone,
      "website": data.website_link,
      "facebook_link": data.facebook_link,
      "seeking_talent": data.seeking_talent,
      "seeking_description": data.seeking_description,
      "image_link": data.image_link
    } 
  else:
    venue = {}
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  data = Venue.query.get(venue_id)
  form = VenueForm(request.form)

  data.id = venue_id
  data.name = form.name.data
  data.genres = form.genres.data
  data.address = form.address.data
  data.city = form.city.data
  data.state = form.state.data
  data.phone = form.phone.data
  data.website_link = form.website_link.data
  data.facebook_link = form.facebook_link.data
  data.seeking_talent = form.seeking_talent.data
  data.seeking_description = form.seeking_description.data
  data.image_link = form.image_link.data

  try:
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead

  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate_inputs():
    try:
      artist = Artist(name=form.name.data,city=form.city.data,state=form.state.data,phone=form.phone.data,image_link=form.image_link.data,genres=form.genres.data,facebook_link=form.facebook_link.data,website_link=form.website_link.data,seeking_venue=form.seeking_venue.data,seeking_description=form.seeking_description.data)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  else:
      flash('An error occurred. Please enter valid inputs')


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = db.session.query(Venue.id.label('venue_id'), Venue.name.label('venue_name'), Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time.label('start_time')).filter(Show.artist_id == Artist.id).filter(Show.venue_id == Venue.id).all()
    data = []

    for show in shows:
        data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue_name,
          "artist_id": show.artist_id,
          "artist_name": show.artist_name,
          "artist_image_link": show.artist_image_link,
          "start_time": format_datetime(str(show.start_time))
        })
        
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  try:
      show = Show(artist_id = form.artist_id.data, venue_id= form.venue_id.data, start_time=format_datetime(str(form.start_time.data)))
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
