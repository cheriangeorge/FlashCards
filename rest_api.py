##############################   API
##############################
####################################
####################################

from flask import jsonify, make_response
from flask_restful import Api, Resource, fields, marshal_with, reqparse, abort, marshal
from model import  *

# Parse the body of the HTTP METHOD. Needs to have card_parser, user_parser and deck_parser
card_parser = reqparse.RequestParser()
card_parser.add_argument('card_name', type = str)
card_parser.add_argument('front_content', type = str)
card_parser.add_argument('back_content', type = str)
card_parser.add_argument('category', type = str)

deck_parser = reqparse.RequestParser()
deck_parser.add_argument('deck_name', type = str)
deck_parser.add_argument('subtitle', type = str)
deck_parser.add_argument('summary', type = str)

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type = str)
user_parser.add_argument('password', type = str)

api = Api(app)

#Validation Function to validate for type and length
def validate(var,type_sample,size):
  if var==None:
    return False
  if type(var)!=type(type_sample):
    return False
  if type(type_sample)==type("abc"):
    if len(var.strip())>size:
      return False
  elif type(type_sample)==type(123):
    if var>size:
      return False  
  return True
#Custom Error Generator Function
def error_generator(id,http_code):
  error_dict = {
    "CARD_ERROR_001":{
                  "error_code": "CARD_ERROR_001",
                  "error_message": "Card Name is required and should be a non-empty string upto 30 characters."
                },
    "CARD_ERROR_002":{
                  "error_code": "CARD_ERROR_002",
                  "error_message": "Front Content is required and should be a non-empty string upto 30 characters."
                },
    "CARD_ERROR_003":{
                  "error_code": "CARD_ERROR_003",
                  "error_message": "Back Content is required and should be a non-empty string upto 30 characters."
                },
    "CARD_ERROR_004":{
                  "error_code": "CARD_ERROR_004",
                  "error_message": "Category is required and  should be a non-empty string upto 30 characters."
                },
    "DECK_ERROR_001":{
                  "error_code": "DECK_ERROR_001",
                  "error_message": "Deck Name is required and should be a non-empty string upto 30 characters."
                },
    "DECK_ERROR_002":{
                  "error_code": "DECK_ERROR_002",
                  "error_message": "Subtitle is required and should be a non-empty string upto 30 characters."
                },
    "DECK_ERROR_003":{
                  "error_code": "DECK_ERROR_003",
                  "error_message": "Summary is required and should be a non-empty string upto 30 characters."
                },
    "USER_ERROR_001":{
                  "error_code": "USER_ERROR_001",
                  "error_message": "Username is required and should be a non-empty string upto 10 characters."
                },
    "USER_ERROR_002":{
                  "error_code": "USER_ERROR_002",
                  "error_message": "Password is required and should be a non-empty string upto 10 characters."
                },
    "USER_ERROR_003":{
                  "error_code": "USER_ERROR_003",
                  "error_message": "The provided username already exists. Please choose another one."
                }
  }
  if id not in error_dict.keys():
    response = make_response(
                    id,
                    http_code,
                )
    #response.headers["Content-Type"] = "application/json"
    return response 
  else:    
    response = make_response(
                    jsonify(
                        error_dict[id]
                    ),
                    http_code,
                )
    response.headers["Content-Type"] = "application/json"
    return response 

card_resourse_fields = {
    'id': fields.Integer,
    'card_name': fields.String,
    'front_content': fields.String,
    'back_content': fields.String,
    'category' : fields.String,
    'owner':fields.String
}

deck_resourse_fields = {
    'id': fields.Integer,
    'deck_name': fields.String,
    'subtitle': fields.String,
    'summary': fields.String,
    'owner': fields.String
}

user_resourse_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String
}

user_deck_resourse_fields = {
    'user_id': fields.Integer,
    'deck_id': fields.String,
    'last_reviewed': fields.String,
    'score': fields.String
}

# # Card GET,PUT,DELETE
class CardResource(Resource):
  def get(self,card_id):
    # Response codes 200,404,500
    if type(card_id)!=type(12) or card_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      cardx=Card.query.filter_by(id = int(card_id)).first()
      if cardx is None:
        return error_generator("ID not found",404)
      return marshal(cardx,card_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

  def delete(self,card_id):
    if type(card_id)!=type(12) or card_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      cardx=Card.query.filter_by(id = int(card_id)).first()
      if cardx is None:
        return error_generator("ID not found",404)
      else:
        #Delete card from all relations - CardDeckRel and CardUserRel
        User_Card_Rel.query.filter_by(card_id=card_id).delete()
        Card_Deck_Rel.query.filter_by(card_id=card_id).delete()
        # Will the above delete multiple tuples in the relation?
        db.session.delete(cardx)
        db.session.commit()
        return error_generator("Successfully deleted",200)
    except:
      return error_generator("Internal Server Error",500)
  def put(self,card_id):
    data = card_parser.parse_args()
    card_name=data.get('card_name',None)
    front_content=data.get('front_content',None)
    back_content=data.get('back_content',None)
    category=data.get('category',None)
    if not validate(card_name,"aa",30):
      return error_generator("CARD_ERROR_001",405)
    if not validate(front_content,"aa",30):
      return error_generator("CARD_ERROR_002",405)
    if not validate(back_content,"aa",30):
      return error_generator("CARD_ERROR_003",405)
    if not validate(category,"aa",30):
      return error_generator("CARD_ERROR_004",405)
    if type(card_id)!=type(12) or card_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      cardx=Card.query.filter_by(id = int(card_id)).first()
      if cardx is None:
        return error_generator("Card with given ID not found",404)
      else:
        #update card now
        cardx.card_name=card_name
        cardx.front_content=front_content
        cardx.back_content=back_content
        if category:
          cardx.category=category
        db.session.commit()
        return marshal(cardx,card_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

# # Deck GET,PUT,DELETE
class DeckResource(Resource):
  def get(self,deck_id):
    # Response codes 200,404,500
    if type(deck_id)!=type(12) or deck_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      deckx=Deck.query.filter_by(id = int(deck_id)).first()
      if deckx is None:
        return error_generator("ID not found",404)
      return marshal(deckx,deck_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

  def delete(self,deck_id):
    if type(deck_id)!=type(12) or deck_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      deckx=Deck.query.filter_by(id = int(deck_id)).first()
      if deckx is None:
        return error_generator("ID not found",404)
      else:
        #Delete Deck from all relations - CardDeckRel and DeckUserRel
        User_Deck_Rel.query.filter_by(deck_id=deck_id).delete()
        Card_Deck_Rel.query.filter_by(deck_id=deck_id).delete()
        # Will the above delete multiple tuples in the relation?
        db.session.delete(deckx)
        db.session.commit()
        return error_generator("Successfully deleted",200)
    except:
      return error_generator("Internal Server Error",500)

  def put(self,deck_id):
    data = deck_parser.parse_args()
    deck_name=data.get('deck_name',None)
    subtitle=data.get('subtitle',None)
    summary=data.get('summary',None)

    if not validate(deck_name,"aa",30):
      return error_generator("DECK_ERROR_001",405)
    if not validate(subtitle,"aa",30):
      return error_generator("DECK_ERROR_002",405)
    if not validate(summary,"aa",30):
      return error_generator("DECK_ERROR_003",405)
    
    if type(deck_id)!=type(12) or deck_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      deckx=Deck.query.filter_by(id = int(deck_id)).first()
      if deckx is None:
        return error_generator("Deck with given ID not found",404)
      else:
        #update deck now
        deckx.deck_name=deck_name
        deckx.subtitle=subtitle
        deckx.summary=summary
        
        db.session.commit()
        return marshal(deckx,deck_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

class DeckCardsResource(Resource):
  def get(self,deck_id):
    # Response codes 200,404,500
    if type(deck_id)!=type(12) or deck_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      deckx=Deck.query.filter_by(id = int(deck_id)).first()
      if deckx is None:
        return error_generator("ID not found",404)
      else:
        cards = [i for i in deckx.cards]
        if not cards:
          return error_generator("Deck has no cards",401)
        else:
          cardsindeck=[]
          for cardj in cards:
            cardi=Card.query.filter_by(id = int(cardj.card_id)).first()
            cardsindeck.append(cardi)
          return marshal(cardsindeck,card_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

class UsersCardsResource(Resource):
  def get(self,user_id):
    # Response codes 200,404,500
    if type(user_id)!=type(12) or user_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      userx=User.query.filter_by(id = int(user_id)).first()
      #deckx=Deck.query.filter_by(id = int(deck_id)).first()
      if userx is None:
        return error_generator("ID not found",404)
      else:
        cards = [i for i in userx.user_cards]
        if not cards:
          return error_generator("User has no cards",401)
        else:
          userscards=[]
          for cardj in cards:
            cardi=Card.query.filter_by(id = int(cardj.id)).first()
            userscards.append(cardi)
          return marshal(userscards,card_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

class UsersDecksResource(Resource):
  def get(self,user_id):
    # Response codes 200,404,500
    if type(user_id)!=type(12) or user_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      userx=User.query.filter_by(id = int(user_id)).first()
      if userx is None:
        return error_generator("ID not found",404)
      else:
        decks = [i for i in userx.user_decks]
        if not decks:
          return error_generator("User has no decks",401)
        else:
          usersdecks=[]
          for deckj in decks:
            decki=Deck.query.filter_by(id = int(deckj.id)).first()
            usersdecks.append(decki)
          return marshal(usersdecks,deck_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)


class UserResource(Resource):
  def post(self):
    data = user_parser.parse_args()
    username=data.get('username',None)
    password=data.get('password',None)

    if not validate(username,"aa",10):
      return error_generator("USER_ERROR_001",405)
    if not validate(password,"aa",10):
      return error_generator("USER_ERROR_002",405)
    usercheck = User.query.filter_by(username=username).first()
    if usercheck:
      return error_generator("USER_ERROR_003",405)   
    try:
      userx = User(username=username,password=password)
      db.session.add(userx)
      db.session.commit()
      return marshal(userx,user_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

class CardPostResource(Resource):
  def post(self,user_id):
    data = card_parser.parse_args()
    card_name=data.get('card_name',None)
    front_content=data.get('front_content',None)
    back_content=data.get('back_content',None)
    category=data.get('category',None)
    if not validate(card_name,"aa",30):
      return error_generator("CARD_ERROR_001",405)
    if not validate(front_content,"aa",30):
      return error_generator("CARD_ERROR_002",405)
    if not validate(back_content,"aa",30):
      return error_generator("CARD_ERROR_003",405)
    if not validate(category,"aa",30):
        return error_generator("CARD_ERROR_004",405)
    if type(user_id)!=type(12) or user_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      userx=User.query.filter_by(id = int(user_id)).first()
      if userx is None:
        return error_generator("User with given ID not found",404)
      else:
        #add card now
        if not category:
          category=""
        cardx=Card(card_name=card_name,front_content=front_content,back_content=back_content,category=category,owner=userx.username)
        db.session.add(cardx)
        db.session.commit()
        return marshal(cardx,card_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

class DeckPostResource(Resource):
  def post(self,user_id):
    data = deck_parser.parse_args()
    deck_name=data.get('deck_name',None)
    subtitle=data.get('subtitle',None)
    summary=data.get('summary',None)
    if not validate(deck_name,"aa",30):
      return error_generator("DECK_ERROR_001",405)
    if not validate(subtitle,"aa",30):
      return error_generator("DECK_ERROR_002",405)
    if not validate(summary,"aa",30):
      return error_generator("DECK_ERROR_003",405)
    if type(user_id)!=type(12) or user_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      userx=User.query.filter_by(id = int(user_id)).first()
      if userx is None:
        return error_generator("User with given ID not found",404)
      else:
        #add deck now
        deckx=Deck(deck_name=deck_name,subtitle=subtitle,summary=summary,owner=userx.username)
        db.session.add(deckx)
        db.session.commit()
        return marshal(deckx,deck_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

class ScoreResource(Resource):
  def get(self,user_id,deck_id):
    # Response codes 200,404,500
    if type(user_id)!=type(12) or user_id>10**17:
      return error_generator("Invalid ID supplied",400)
    if type(deck_id)!=type(12) or deck_id>10**17:
      return error_generator("Invalid ID supplied",400)
    try:
      userx=User.query.filter_by(id = int(user_id)).first()
      deckx=Deck.query.filter_by(id = int(deck_id)).first()
      if userx is None:
        return error_generator("User ID not found",404)
      elif deckx is None:
        return error_generator("Deck ID not found",404)
      else:
        ud=User_Deck_Rel.query.filter_by(user_id=user_id,deck_id=deck_id).first()
        if not ud:
          return error_generator("User has not reviewed this deck",401)
        else:
          return marshal(ud,user_deck_resourse_fields),200
    except:
      return error_generator("Internal Server Error",500)

#Adding resources to API
api.add_resource(CardResource,'/api/v1/card/<int:card_id>')
api.add_resource(DeckCardsResource,'/api/v1/deck/<int:deck_id>/cards')
api.add_resource(DeckResource,'/api/v1/deck/<int:deck_id>')
api.add_resource(UsersCardsResource,'/api/v1/user/<int:user_id>/cards')
api.add_resource(UsersDecksResource,'/api/v1/user/<int:user_id>/decks')
api.add_resource(UserResource,'/api/v1/user')
api.add_resource(CardPostResource,'/api/v1/user/<int:user_id>/card')
api.add_resource(DeckPostResource,'/api/v1/user/<int:user_id>/deck')
api.add_resource(ScoreResource,'/api/v1/user/<int:user_id>/deck/<int:deck_id>')
####################################
####################################
##############################
##############################   API