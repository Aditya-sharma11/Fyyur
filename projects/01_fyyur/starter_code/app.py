#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email import message
import itertools
import json
from operator import itemgetter
from os import abort
from threading import local
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, Logger
from flask_wtf import Form
from flask_migrate import Migrate
from sqlalchemy import and_
from flask_wtf import CsrfProtect
from forms import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf = CsrfProtect()
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column((db.Integer), primary_key=True)
    name = db.Column((db.String), nullable=False)
    genres = db.Column((db.String(200)), nullable=False)
    city = db.Column((db.String(120)), nullable=False)
    state = db.Column((db.String(120)), nullable=False)
    address = db.Column((db.String(120)), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    

    #website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # Venue is the parent (one-to-many) of a Show (Artist is also a foreign key, in def. of Show)
    # In the parent is where we put the db.relationship in SQLAlchemy
    shows = db.relationship('Show', backref='venue', lazy=True)    # Can reference show.venue (as well as venue.shows)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column((db.Integer), primary_key=True)
    name = db.Column((db.String), nullable=False)
    city = db.Column((db.String(100)), nullable=False)
    state = db.Column((db.String(100)), nullable=False)
    phone = db.Column(db.String(100))
    genres = db.Column((db.String(100)), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(100))
    website_link = db.Column(db.String(100))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

 

    # Artist is the parent (one-to-many) of a Show (Venue is also a foreign key, in def. of Show)
    # In the parent is where we put the db.relationship in SQLAlchemy
    shows = db.relationship('Show', backref='artist', lazy=True)    # Can reference show.artist (as well as artist.shows)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    """'Represents show data model.'"""
    __tablename__ = 'show'
    id = db.Column((db.Integer), primary_key=True)
    venue_id = db.Column((db.Integer), (db.ForeignKey('venue.id')), nullable=False)
    artist_id = db.Column((db.Integer), (db.ForeignKey('artist.id')), nullable=False)
    venue = db.relationship('Venue', backref='shows', lazy=True)
    artist = db.relationship('Artist', backref='shows', lazy=True)
    start_time = db.Column((db.DateTime), nullable=False, server_default=(db.func.now()))

    def __init__(self, venue_id, artist_id, start_time):
        """Instantiates a new show with initial values.

        Args:
            venue_id(int): The venue ID.
            artist_id(int): The artist ID.
            start_time(datetime): The start date and time.
        """
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def insert(self):
        """Adds this instance to the session and then persist it to the database."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Persists any changes made to the database."""
        db.session.commit()

    def format(self):
        """dict: Gets this instance as a dictionary containing all attributes."""
        return {'venue_id':self.venue.id, 
         'venue_name':self.venue.name, 
         'artist_id':self.artist.id, 
         'artist_name':self.artist.name, 
         'artist_image_link':self.artist.image_link, 
         'start_time':self.start_time.isoformat()}

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

def __repr__(self):
        return f"<Show start_time={self.start_time}, venue={self.venue}, artist={self.artist}>"
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
    """Renders venues page."""
    venues = Venue.query.all()
    data = []   # A list of dictionaries, where city, state, and venues are dictionary keys

    # Create a set of all the cities/states combinations uniquely
    cities_states = set()
    for venue in venues:
        cities_states.add( (venue.city, venue.state) )  # Add tuple
    
    # Turn the set into an ordered list
    cities_states = list(cities_states)
    cities_states.sort(key=itemgetter(1,0)) 

    now = datetime.now()   

    
    for loc in cities_states:
    
        venues_list = []
        for venue in venues:
            if (venue.city == loc[0]) and (venue.state == loc[1]):

           
                venue_shows = Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming = 0
                for show in venue_shows:
                    if show.start_time > now:
                        num_upcoming += 1

                venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming
                })

        
        data.append({
            "city": loc[0],
            "state": loc[1],
            "venues": venues_list
        })

    return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.like('%' + search + '%' )).all()
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {'count':len(venues),  'data':list(venues)}
  
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id 
     venue = Venue.query.get(venue_id)   # Returns object by primary key, or None
     print(venue)
     if not venue:
        # Didn't return one, user must've hand-typed a link into the browser that doesn't exist
        # Redirect home
        return redirect(url_for('index'))
     else:
        # genres needs to be a list of genre strings for the template
        genres = [ genre.name for genre in venue.genres ]
        
        # Get a list of shows, and count the ones in the past and future
        past_shows = []
        past_shows_count = 0
        upcoming_shows = []
        upcoming_shows_count = 0
        now = datetime.now()
        for show in venue.shows:
            if show.start_time > now:
                upcoming_shows_count += 1
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
            if show.start_time < now:
                past_shows_count += 1
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })

        data = {
            "id": venue_id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            # Put the dashes back into phone number
            "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
            "website_link": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count
        }
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
  form = VenueForm()
  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  address = form.address.data.strip()
  phone = form.phone.data

  genres = form.genres.data                 
  seeking_talent = True if form.seeking_talent.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website_link = form.website_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
    
    # Redirect back to form if errors in form validation
  if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_venue_submission'))

  else:
        error_in_insert = False

        # Insert form data into DB
        try:
            # creates the new venue with all fields but not genre yet
            new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
                seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
                website_link=website_link, facebook_link=facebook_link)
            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                # fetch_genre = session.query(Genre).filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                fetch_genre = genre.query.filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                if fetch_genre:
                    # if found a genre, append it to the list
                    new_venue.genres.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = genre(name=genre)
                    db.session.add(new_genre)
                    new_venue.genres.append(new_genre)  # Create a new Genre item and append it

            db.session.add(new_venue)
            db.session.commit()
        except Exception as e:
            error_in_insert = True
            print(f'Exception "{e}" in create_venue_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_insert:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))
        else:
            flash('An error occurred. Venue ' + name + ' could not be listed.')
            print("Error in create_venue_submission()")
            # return redirect(url_for('create_venue_submission'))
            abort(500)
        return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.filter_by(id=venue_id).first()
  if venue is None:
      return abort(404)
  try:
        venue.delete()
        flash(f"Venue {venue.name} was successfully deleted!", 'success')
        return redirect(url_for('index'))
  except exec.IntegrityError:
        Logger.exception(f"Error trying to delete venue {venue}",
          exc_info=True)
        flash(f"Venue {venue.name} cant be deleted.", 'danger')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.order_by(Artist.name).all()  # Sort alphabetically

    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)
  
def search_artists():
    # Most of code is from search_venues()
    search_term = request.form.get('search_term', '').strip()

    # Use filter, not filter_by when doing LIKE search (i=insensitive to case)
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()   # Wildcards search before and after
    #print(artists)
    artist_list = []
    now = datetime.now()
    for artist in artists:
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming = 0
        for show in artist_shows:
            if show.start_time > now:
                num_upcoming += 1

        artist_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming  # FYI, template does nothing with this
        })

    response = {
        "count": len(artists),
        "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist is None:
        return abort(404)
  else:
        data = artist.format()
        return render_template('pages/show_artist.html', artist=data)
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_edited = Artist.query.filter_by(id=artist_id).first()
  if artist_edited is None:
        abort(404)
  form = ArtistForm(request.form)
  if form.validate_on_submit():
        form.genres.data = ', '.join(form.genres.data)
        form.populate_obj(artist_edited)
        artist_edited.update()
        return redirect(url_for('show_artist', artist_id=artist_id))
  else:
        return render_template('forms/edit_artist.html', form=form, artist=artist_edited)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_found = Venue.query.filter_by(id=venue_id).first()
  if venue_found is None:
        abort(404)
  venue = {'id':venue_found.id, 
     'name':venue_found.name, 
     'genres':venue_found.genres.split(', '), 
     'address':venue_found.address, 
     'city':venue_found.city, 
     'state':venue_found.state, 
     'phone':venue_found.phone, 
     'website_link':venue_found.website_link, 
     'facebook_link':venue_found.facebook_link, 
     'seeking_talent':venue_found.seeking_talent, 
     'seeking_description':venue_found.seeking_description, 
     'image_link':venue_found.image_link}
  form = VenueForm(formdata=None, data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)


  # form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # # TODO: populate form with values from venue with ID <venue_id>
  # return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue_edited = Venue.query.filter_by(id=venue_id).first()
  if venue_edited is None:
        abort(404)
  form = VenueForm(request.form)
  if form.validate_on_submit():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(venue_edited)
    venue_edited.update()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venue_edited)

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    # Much of this code is similar to create_venue view
    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    # address = form.address.data.strip()
    phone = form.phone.data
    
    genres = form.genres.data                  
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website_link = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()
    
    # Redirect back to form if errors in form validation
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_artist_submission'))

    else:
        error_in_insert = False

        # Insert form data into DB
        try:
            # creates the new artist with all fields but not genre yet
            new_artist = Artist(name=name, city=city, state=state, phone=phone, \
                seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link, \
                websit_link=website_link, facebook_link=facebook_link)
            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                # fetch_genre = session.query(Genre).filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                fetch_genre = genre.query.filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                if fetch_genre:
                    # if found a genre, append it to the list
                    new_artist.genres.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = genre(name=genre)
                    db.session.add(new_genre)
                    new_artist.genres.append(new_genre)  # Create a new Genre item and append it

            db.session.add(new_artist)
            db.session.commit()
        except Exception as e:
            error_in_insert = True
            print(f'Exception "{e}" in create_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_insert:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))
        else:
            flash('An error occurred. Artist ' + name + ' could not be listed.')
            print("Error in create_artist_submission()")
            abort(500)

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = [show.format() for show in shows]
  return render_template('pages/shows.html', shows=data)

  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data = []
  # shows = Show.query.order_by(Show.start_time.desc()).all()

  # for show in shows:
  #   data.extend([{
  #       "venue_id": show.venue.id,
  #       "venue_name": show.venue.name,
  #       "artist_id": show.artist.id,
  #       "artist_name": show.artist.name,
  #       "artist_image_link": show.artist.image_link,
  #       "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
  #   }])
 
  # return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = create_shows()
  if not form.validate_on_submit():
        error_message = 'Theres errors within the form. Please review it firstly.'
  else:
        try:
            artist_id = form.artist.data
            venue_id = form.venue.data
            start_time = form.start_time.data
            venue_exists = db.session.query(Venue.id).filter_by(id=venue_id).scalar() is not None
            artist_exists = db.session.query(Artist.id).filter_by(id=artist_id).scalar() is not None
            if not artist_exists:
                error_message = f"The artist with ID {artist_id} doesn't exists!"
            elif not venue_exists:
                error_message = f"The venue with ID {venue_id} doesn't exists!"
            else:
                exists = db.session.query(Show.id).filter(and_((Show.artist_id == artist_id) & (Show.venue_id == venue_id) & (Show.start_time == start_time))).scalar() is not None
                if exists:
                    error_message = 'This show is already registered!'
                else:
                    new_show = Show(venue_id, artist_id, start_time)
                    new_show.insert()
                    flash(f"Show at {new_show.venue.name} with {new_show.artist.name} at {new_show.start_time} was successfully created!", 'success')
                    return redirect(url_for('shows'))
        except exec.SQLAlchemyError as error:
            try:
                Logger.exception(error, exc_info=True)
                error_message = 'An error occurred while show creation. Sorry, this show could not be created.'
            finally:
                error = None
                del error

        if error_message is not None:
            flash(error_message, 'danger')
        

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
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
