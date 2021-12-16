from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///flashcards.sqlite3"
app.config["SECRET_KEY"]='thisismysecretkey123@34'

db=SQLAlchemy(app)

####USER MODEL###
class User(UserMixin,db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  username=db.Column(db.String(30),unique=True,nullable=False)
  password=db.Column(db.String(30),nullable=False)
  decks = db.relationship('User_Deck_Rel',backref='User')
  cards = db.relationship('User_Card_Rel',backref='User')
  # Use cascade="all,delete" 
  user_decks=db.relationship('Deck',backref='User')
  user_cards=db.relationship('Card', backref='User')

####CARD MODEL###
class Card(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  card_name=db.Column(db.String(30),nullable=False)
  front_content=db.Column(db.String(30),nullable=False)
  back_content=db.Column(db.String(30),nullable=False)
  category=db.Column(db.String(30),nullable=False)
  owner = db.Column(db.String(30),db.ForeignKey('user.username'),nullable=False)
  decks = db.relationship('Card_Deck_Rel',backref='Card')

####DECK MODEL###
class Deck(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  deck_name=db.Column(db.String(30),nullable=False)
  subtitle=db.Column(db.String(30),nullable=False)
  summary=db.Column(db.String(30),nullable=False)
  owner = db.Column(db.String(30),db.ForeignKey('user.username'),nullable=False)
  cards = db.relationship('Card_Deck_Rel',backref='Deck')
# 
####CARD_DECK_REL MODEL###
class Card_Deck_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  card_id = db.Column(db.Integer,db.ForeignKey('card.id'),nullable=False)
  deck_id = db.Column(db.Integer,db.ForeignKey('deck.id'),nullable=False)

####USER_CARD_REL MODEL###
class User_Card_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  card_id = db.Column(db.Integer,db.ForeignKey('card.id'),nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
  difficulty_level = db.Column(db.Integer)
  last_reviewed = db.Column(db.Date)

####USER_DECK_REL MODEL###
class User_Deck_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  deck_id = db.Column(db.Integer,db.ForeignKey('deck.id'),nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
  score = db.Column(db.Integer)
  last_reviewed = db.Column(db.Date)

# db.create_all()
# a1 = User(username="admin",password="pass123")
# db.session.add(a1)
# db.session.commit()
# a1=User.query.filter_by(username='admin').first()
# a1.password="pass123"
# db.session.commit()