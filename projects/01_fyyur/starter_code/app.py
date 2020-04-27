#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.sql import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable = False)
    city = db.Column(db.String(120),nullable = False)
    state = db.Column(db.String(120),nullable = False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,nullable = False)
    seeking_description = db.Column(db.String(120))
   




class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable = False)
    city = db.Column(db.String(120),nullable = False)
    state = db.Column(db.String(120),nullable = False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable = False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable = False)
    seeking_description = db.Column(db.String(120))

  

class Show(db.Model):
  __tablename__ = 'Show'
  id=db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime,nullable = False)
  venue = db.relationship('Venue',backref = 'shows',)
  artist = db.relationship('Artist',backref = 'shows')




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format,locale='en_US')

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
  
  data = []
  areas = Venue.query\
              .with_entities(Venue.city,Venue.state)\
              .group_by(Venue.city,Venue.state)\
              .all()
  venues = []
  for area in areas:
    venue = Venue.query\
              .with_entities(Venue.id,Venue.name)\
              .filter(Venue.city == area.city)\
              .filter(Venue.state == area.state)\
              .all()
    
    data.append({
      "city" : area.city,
      "state": area.state,
      "venues" : venue
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  query = '%' + request.form.get('search_term','') + '%'

  search_query = Venue.query.filter(Venue.name.ilike(query))

  search_results  = {
    "count": search_query.count(),
    "data": search_query.with_entities(Venue.id,Venue.name).all()
  }
 
  return render_template('pages/search_venues.html', results=search_results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  current_time = datetime.now()
  
  venue = Venue.query\
              .filter(Venue.id == venue_id)\
              .one()
              

  show_query = Show.query\
              .filter(Show.venue_id == venue_id)\
              .join(Artist)\
              .with_entities(Show.artist_id,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'),Show.start_time)

  past_query = show_query.filter(Show.start_time < current_time)

  upcoming_query = show_query.filter(Show.start_time > current_time)

  venue.upcoming_shows = upcoming_query.all()
  venue.past_shows  = past_query.all()
  venue.upcoming_shows_count = len(venue.upcoming_shows)
  venue.past_shows_count = len(venue.past_shows)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  
  if not form.validate():
    flash('An error occurred in your form. Please fill it out again')
    return render_template('forms/new_venue.html', form=form)
  
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_talent = request.form.get('seeking_talent','n') == 'y'
  seeking_description = request.form['seeking_description']

  venue = Venue(name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                image_link=image_link,
                facebook_link = facebook_link,
                website=website,
                seeking_talent = seeking_talent,
                seeking_description = seeking_description
                )
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' +  request.form['name']+ ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  
  try:
    db.seesion.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query\
            .with_entities(Artist.id,Artist.name)\
            .all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  query = '%' + request.form.get('search_term','') + '%'

  search_query = Artist.query.filter(Artist.name.ilike(query))

  search_results  = {
    "count": search_query.count(),
    "data": search_query.with_entities(Artist.id,Artist.name).all()
  }

  return render_template('pages/search_artists.html', results=search_results, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  current_time = datetime.now()
  artist = Artist.query\
              .filter(Artist.id == artist_id)\
              .one()
              

  show_query = Show.query\
              .filter(Show.artist_id == artist_id)\
              .join(Venue)\
              .with_entities(Show.venue_id,Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link'),Show.start_time)

  past_query = show_query.filter(Show.start_time < current_time)

  upcoming_query = show_query.filter(Show.start_time > current_time)

  artist.upcoming_shows = upcoming_query.all()
  artist.past_shows  = past_query.all()
  artist.upcoming_shows_count = len(artist.upcoming_shows)
  artist.past_shows_count = len(artist.past_shows)

  print(artist.past_shows)

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj= artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj= artist)

  if not form.validate():
    flash('An error occurred in your form. Please fill it out again')
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()

  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj= venue)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj= venue)
  if not form.validate():
    flash('An error occurred in your form. Please fill it out again')
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
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
  form = ArtistForm()
  if not form.validate():
    flash('An error occurred in your form. Please fill it out again')
    return render_template('forms/new_artist.html', form=form)

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_venue = request.form.get('seeking_venue', 'n') == 'y'
  seeking_description = request.form['seeking_description']

  try:
    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      image_link=image_link,
      facebook_link=facebook_link,
      website=website,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description
    )
    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + name + ' was successfully listed!')
  except:
    db.session.rollback()

    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query \
              .join(Show.artist) \
              .join(Show.venue) \
              .order_by(Show.start_time.desc()) \
              .with_entities(Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time) \
              .all()
  
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  if not form.validate():
    flash('An error occurred in your form. Please fill it out again')
    return render_template('forms/new_show.html', form=form)

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
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
