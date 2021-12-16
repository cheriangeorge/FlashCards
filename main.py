from flask import Flask,render_template,request,redirect

from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from model import *
from rest_api import *

login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user1(user_id):
  return User.query.get(int(user_id))

@app.route('/',methods =['GET','POST'])
def index():
  if request.method=="POST":
    uname=request.form.get('username',None)
    pwd=request.form.get('password',None)
    #Validation
    if uname == None or pwd == None or type(uname)!=type("abc") or type(pwd)!=type("abc"):
      if len(uname.strip())==0 or len(pwd.strip())==0 or len(uname.strip())>10 or len(pwd.strip())>10:
        return render_template("login.html",message="Invalid username or password.")
    userx=User.query.filter_by(username=uname,password=pwd).first()
    if userx:
      login_user(userx)
      #print('The user '+current_user.username+' is now logged in')
      return redirect("/dashboard")
    else:
      return render_template("login.html",message="Wrong username or password.")
  elif request.method=="GET":
    if current_user.is_authenticated:
      #return render_template("dashboard.html",username=current_user.username)
      return redirect('/dashboard')
    else:
      return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
  if current_user.is_authenticated:
    logout_user()
    return render_template("login.html",message="You have logged out successfully!")
  else:
    return redirect("/")

@app.route("/about")
@login_required
def about():
  return render_template("about.html",username=current_user.username)

@app.route("/apidoc")
@login_required
def api_docs():
  return render_template("swagger.html",username=current_user.username)

@app.route('/dashboard')
@login_required
def dashboard():
  #Get all decks 
  decksx=Deck.query.all()
  # Do not send decks that have no cards
  # Send dictionary with Deck_id,score,last_reviewed data
  userx=User.query.filter_by(username=current_user.username).first()
  deck_info={}
  deckswithcards=[]
  for i in decksx:
    # print(i.id)
    no_cards=len(i.cards)
    # print("deckid",i.id,",cards:",no_cards)
    if no_cards==0:
      #print("removing",i.id)
      #decksx.remove(i) # Don't pass empty decks
      continue
    else:
      deckswithcards.append(i)
      d_info = User_Deck_Rel.query.filter_by(deck_id=i.id,user_id=userx.id).first()
      # print(d_info)
      if d_info:
        deck_info[i.id]={'score':d_info.score,'no_cards':no_cards,'last_reviewed':d_info.last_reviewed,'e':0,'m':0,'d':0}
        # deck_info[i.id]['score']=d_info.score
        # deck_info[i.id]['no_cards']=no_cards
        # deck_info[i.id]['last_reviewed']=d_info.last_reviewed
        # deck_info[i.id]['e']=0
        # deck_info[i.id]['m']=0
        # deck_info[i.id]['d']=0
        for j in i.cards:
          card_data = User_Card_Rel.query.filter_by(card_id=j.card_id,user_id=userx.id).first()
          if not card_data:
            #pass
            continue
          if card_data.difficulty_level==1:
            deck_info[i.id]['e']+=1
          elif card_data.difficulty_level==2:
            deck_info[i.id]['m']+=1
          elif card_data.difficulty_level==3:
            deck_info[i.id]['d']+=1
      else:
        deck_info[i.id]={'score':'na','no_cards':no_cards,'last_reviewed':'Never','e':0,'m':0,'d':0}
        # deck_info[i.id]['score']='na'
        # deck_info[i.id]['no_cards']=no_cards
        # deck_info[i.id]['last_reviewed']='na'
        # deck_info[i.id]['e']='na'
        # deck_info[i.id]['m']='na'
        # deck_info[i.id]['d']='na'
    #Number of E/M/H cards
  # import pprint
  # pprint.pprint(decksx)
  # pprint.pprint(deck_info)
  return render_template("dashboard.html",username=current_user.username,decks=deckswithcards,deck_info=deck_info)


@app.route('/review',methods =['GET','POST'])
@login_required
def review():
  if request.method=="POST":
    from datetime import date
    today = date.today()
    userx=User.query.filter_by(username=current_user.username).first()
    user_id=userx.id
    deck_id=request.form.get('deck_id',None)
    deck_score=request.form.get('deck_score',None)
    difficulty_level=request.form.get('submit',None)
    completed_cards=request.form.getlist('completed_cards',None)
    remaining_cards=request.form.getlist('remaining_cards',None)
    current_card=request.form.get('current_card',None)
    #Validating form data

    #end validating form data
    deckx=Deck.query.filter_by(id=deck_id).first()
    # print(request.form)
    deck_info={}
    deck_info['id']=deckx.id
    deck_info['name']=deckx.deck_name
    deck_info['subtitle']=deckx.subtitle
    deck_info['summary']=deckx.summary
    cardslist=deckx.cards
    if len(cardslist)==0:
      return redirect('/review')
    deck_info['no_cards']=len(cardslist)
    deck_info['completed_cards']=completed_cards
    deck_info['remaining_cards']=remaining_cards

    if current_card==None and deck_id:
      #Dict of Deck data
      cardx=Card.query.filter_by(id=cardslist[0].card_id).first()
      deck_info['current_card']=cardx.id
      deck_info['remaining_cards']=[]
      for i in cardslist[1:]:
        deck_info['remaining_cards'].append(i.card_id)
      deck_info['completed_cards']=[deck_info['current_card']]
      deck_info['deck_score']=deck_info['no_cards']
      #Dict of Card data
      return render_template("review.html",username=current_user.username,deck=deck_info,card=cardx)
    elif len(deck_info['remaining_cards'])>0:
      #print(deck_info)

      #updated last_viewed and e/m/h of current card in the db
      user_card = User_Card_Rel.query.filter_by(card_id=current_card,user_id=user_id).first()
      if user_card:
        user_card.difficulty_level = difficulty_level
        user_card.last_reviewed = today
        db.session.commit()
      else:
        ucr = User_Card_Rel(card_id=current_card,user_id=user_id,difficulty_level= difficulty_level,last_reviewed=today)
        db.session.add(ucr)
        db.session.commit()

      deck_info['deck_score']=deck_score
      deck_info['current_card']=deck_info['remaining_cards'][0]
      deck_info['completed_cards'].append(deck_info['current_card'])
      cardx=Card.query.filter_by(id=deck_info['remaining_cards'][0]).first()
      deck_info['remaining_cards']=deck_info['remaining_cards'][1:]
      return render_template("review.html",username=current_user.username,deck=deck_info,card=cardx)
    elif len(cardslist)==len(completed_cards):
      #Add date,score to deck_user_rel
      from datetime import date
      today = date.today()
      #deck_id,user_id,score,last_reviewed
      #Adding to Card _ User Rel
      user_card = User_Card_Rel.query.filter_by(card_id=current_card,user_id=user_id).first()
      if user_card:
        user_card.difficulty_level = difficulty_level
        user_card.last_reviewed = today
        db.session.commit()
      else:
        ucr = User_Card_Rel(card_id=current_card,user_id=user_id,difficulty_level= difficulty_level,last_reviewed=today)
        db.session.add(ucr)
        db.session.commit()
      #Add deck data
      #if exists update else create
      udr = User_Deck_Rel.query.filter_by(deck_id=deck_id,user_id=user_id).first()
      if udr:
        #Update
        udr.score=deck_score
        udr.last_reviewed=today
        db.session.commit()
      else:
        #create
        deck_update=User_Deck_Rel(deck_id=deck_id,user_id=user_id,score=deck_score,last_reviewed=today)
        db.session.add(deck_update)
        db.session.commit()
      #Add last cards last_reviewed and E/M/H to 

      return redirect('/dashboard')
  elif request.method=="GET":
    #Select a random deck
    import random
    decks=Deck.query.all()
    if not decks:
      return redirect('/dashboard')
    deckx=random.choice(Deck.query.all())
    deck_info={}
    deck_info['id']=deckx.id
    deck_info['name']=deckx.deck_name
    deck_info['subtitle']=deckx.subtitle
    deck_info['summary']=deckx.summary
    cardslist=deckx.cards
    deck_info['no_cards']=len(cardslist)
    deck_info['deck_score']=deck_info['no_cards']
    if len(cardslist)==0:
      return redirect('/dashboard') #Avoiding an empty deck
    cardx=Card.query.filter_by(id=cardslist[0].card_id).first()
    deck_info['completed_cards']=[cardx.id]
    deck_info['current_card']=cardx.id
    deck_info['remaining_cards']=[]
    for i in cardslist[1:]:
      deck_info['remaining_cards'].append(i.card_id)
    return render_template("review.html",username=current_user.username,deck=deck_info,card=cardx)


@app.route('/deck_management',methods =['GET','POST'])
@login_required
def deck_management():
  if request.method=="POST":
    submit = request.form.get('submit',None)
    if submit==None:
      return redirect('/deck_management')
    ##### DELETING INDIVIDUAL Decks
    if submit.startswith("delete"):
      deck_id=submit.split('_')[-1]
      # print("need to delete "+deck_id)
      # Delete Deck from Deck table,Deck_User table, Card_Deck table
      User_Deck_Rel.query.filter_by(deck_id=deck_id).delete()
      Card_Deck_Rel.query.filter_by(deck_id=deck_id).delete()
      Deck.query.filter_by(id=deck_id).delete()
      db.session.commit()
      return redirect('/deck_management')
    ###### EDITING INDIVIDUAL DECKS
    if submit.startswith("edit"):
      deck_id=submit.split('_')[-1]
      ##redirect to edit card interface
      deckx=Deck.query.filter_by(id=deck_id).first()
      if deckx:
        return render_template('edit_deck.html',username=current_user.username,deck=deckx)
      else:
        return redirect('/deck_management')
    ####### SAVING EDIT 
    if submit == "save_edit":
      deck_id = request.form.get('id',None)
      deck_name = request.form.get('name',None)
      subtitle = request.form.get('subtitle',None)
      summary = request.form.get('summary',None)

      #Validate inputs 
      if deck_id==None or deck_name==None or subtitle==None or summary==None:
        return redirect('/deck_management')
      if type(deck_name)==type("abc") and type(subtitle)==type("abc") and type(summary)==type("abc"):
        if len(deck_name.strip())==0 or len(deck_name.strip())>30 or len(subtitle.strip())==0 or len(subtitle.strip())>30 or len(summary.strip())==0 or len(summary.strip())>30:
          return redirect('/deck_management')
      else:
        return redirect('/deck_management')
      #End validation

      deckx=Deck.query.filter_by(id=deck_id).first()
      deckx.deck_name=deck_name
      deckx.subtitle=subtitle
      deckx.summary=summary
      db.session.commit()
      return redirect('/deck_management')
  elif request.method=="GET":
    # users_cards=Card.query.filter_by(owner=current_user.username).all()
    users_decks=Deck.query.filter_by(owner=current_user.username).all()
    deck_info={}
    userx=User.query.filter_by(username=current_user.username).first()
    
    for d in users_decks:
      deck_scores=User_Deck_Rel.query.filter_by(user_id=userx.id,deck_id=d.id).first()
      if deck_scores:
        deck_info[d.id]={'no_cards':len(d.cards),'deck_name':d.deck_name,'subtitle':d.subtitle,'summary':d.summary,'score':deck_scores.score,'last_reviewed':deck_scores.last_reviewed}
      else:
        deck_info[d.id]={'no_cards':len(d.cards),'deck_name':d.deck_name,'subtitle':d.subtitle,'summary':d.summary,'score':'na','last_reviewed':'Never'}
    return render_template("view_decks.html",username=current_user.username,decks=users_decks,deck_info=deck_info)


@app.route('/deck_management/create_card',methods =['GET','POST'])
@login_required
def create_card():
  if request.method=="POST":
    cname=request.form.get('cname',None)
    fcontent=request.form.get('fcontent',None)
    bcontent=request.form.get('bcontent',None)
    category=request.form.get('category',None)
    #Validate inputs 
    if cname==None or fcontent==None or bcontent==None or category==None:
      return render_template("create_card.html",username=current_user.username,message="Please fill in all fields")
    if type(cname)==type("abc") and type(fcontent)==type("abc") and type(bcontent)==type("abc") and type(category)==type("abc"):
      if len(cname.strip())==0 or len(cname.strip())>30 or len(fcontent.strip())==0 or len(fcontent.strip())>30 or len(bcontent.strip())==0 or len(bcontent.strip())>30 or len(category.strip())==0 or len(category.strip())>30:
        return render_template("create_card.html",username=current_user.username,message="Fields cannot be empty and can have at most 30 characters.")
    else:
      return render_template("create_card.html",username=current_user.username,message="Invalid inputs")
    #End validation

    cardx=Card(card_name=cname,front_content=fcontent,back_content=bcontent,category=category,owner=current_user.username)
    db.session.add(cardx)
    db.session.commit()
    return render_template("create_card.html",username=current_user.username,message="Card Added Successfully")

  elif request.method=="GET":
    return render_template("create_card.html",username=current_user.username)

@app.route('/deck_management/create_deck',methods =['GET','POST'])
@login_required
def create_deck():
  if request.method=="POST":
    name=request.form.get('name',None)
    subtitle=request.form.get('subtitle',None)
    summary=request.form.get('summary',None)
        #Validate inputs 
    if name==None or subtitle==None or summary==None:
      return render_template("create_deck.html",username=current_user.username,message="Please fill in all fields")
    if type(name)==type("abc") and type(summary)==type("abc") and type(subtitle)==type("abc"):
      if len(name.strip())==0 or len(name.strip())>30 or len(summary.strip())==0 or len(summary.strip())>30 or len(subtitle.strip())==0 or len(subtitle.strip())>30:
        return render_template("create_deck.html",username=current_user.username,message="Fields cannot be empty and can have at most 30 characters.")
    else:
      return render_template("create_deck.html",username=current_user.username,message="Invalid inputs")
    #End validation
    deckx=Deck(deck_name=name,subtitle=subtitle,summary=summary,owner=current_user.username)
    db.session.add(deckx)
    db.session.commit()
    return render_template("create_deck.html",username=current_user.username,message="Deck Created Successfully. Go to 'View cards' to add cards to your new Deck.")

  elif request.method=="GET":
    return render_template("create_deck.html",username=current_user.username)

@app.route('/deck_management/view_cards',methods =['GET','POST'])
@login_required
def view_cards():
  if request.method=="POST":
    submit = request.form.get('submit',None)
    if submit==None:
      return redirect('/deck_management/view_cards')
    ###### ADDING CARDS TO DECK
    if submit == 'add_to_deck':
      selected_cards=request.form.getlist('selected')
      #print(selected_cards)
      if len(selected_cards)<1:
        return redirect('/deck_management/view_cards')
      selected_deck=request.form.get('selected_deck',None)
      if selected_deck==None:
        return redirect('/deck_management/view_cards')
      deckx=Deck.query.filter_by(id=selected_deck).first()
      cards_in_deck = []
      # print("deckx Cards")
      # print(deckx.cards)
      # print("end of deckx Cards")
      for i in deckx.cards:
        # print("i",i)
        cards_in_deck.append(i.card_id)
      # print (cards_in_deck)
      for i in selected_cards:
        if int(i) not in cards_in_deck:
          # cardx=Card.query.filter_by(id=i).first()
          # deckx.cards.append(cardx)
          # cardx.decks.append(deckx)
          rel = Card_Deck_Rel(card_id=i,deck_id=selected_deck)
          db.session.add(rel)
      db.session.commit()
      return redirect('/deck_management/view_cards')
    ##### DELETING INDIVIDUAL CARDS
    if submit.startswith("delete"):
      card_id=submit.split('_')[-1]
      # print("need to delete "+card_id)
      # Delete Card from Card table,Card_User table, Card_Deck table
      User_Card_Rel.query.filter_by(card_id=card_id).delete()
      Card_Deck_Rel.query.filter_by(card_id=card_id).delete()
      Card.query.filter_by(id=card_id).delete()
      db.session.commit()
      return redirect('/deck_management/view_cards')
    #############################
    ###### EDITING INDIVIDUAL CARDS
    if submit.startswith("edit"):
      card_id=submit.split('_')[-1]
      ##redirect to edit card interface
      cardx=Card.query.filter_by(id=card_id).first()
      decks=[]
      for i in cardx.decks:
        deckx= Deck.query.filter_by(id=i.deck_id).first()
        decks.append(deckx)
      if cardx:
        return render_template('edit_card.html',username=current_user.username,card=cardx,decks=decks)
      else:
        return redirect('/deck_management/view_cards')
    ####### SAVING EDIT 
    if submit == "save_edit":
      card_id = request.form.get('id',None)
      card_name = request.form.get('cname',None)
      front_content = request.form.get('fcontent',None)
      back_content = request.form.get('bcontent',None)
      category = request.form.get('category',None)
      #Validate inputs 
      if card_id==None or card_name==None or front_content==None or back_content==None or category==None:
        return redirect('/deck_management/view_cards')
      if type(card_name)==type("abc") and type(front_content)==type("abc") and type(back_content)==type("abc") and type(category)==type("abc"):
        if len(card_name.strip())==0 or len(card_name.strip())>30 or len(front_content.strip())==0 or len(front_content.strip())>30 or len(back_content.strip())==0 or len(back_content.strip())>30 or len(category.strip())==0 or len(category.strip())>30:
          return redirect('/deck_management/view_cards')
      else:
        return redirect('/deck_management/view_cards')
      #End validation
    
      cardx=Card.query.filter_by(id=card_id).first()
      cardx.card_name=card_name
      cardx.front_content=front_content
      cardx.back_content=back_content
      cardx.category=category
      db.session.commit()
      return redirect('/deck_management/view_cards')
    ####### Removing from deck
    if submit.startswith("removefromdeck"):
      deck_id=submit.split('_')[-1]
      card_id = request.form.get('id',None)
      if card_id:
        Card_Deck_Rel.query.filter_by(card_id=card_id,deck_id=deck_id).delete()
        db.session.commit()
      return redirect('/deck_management/view_cards')

###################################


  elif request.method=="GET":
    users_cards=Card.query.filter_by(owner=current_user.username).all()
    users_decks=Deck.query.filter_by(owner=current_user.username).all()
    card_deck={}
    for c in users_cards:
      card_deck[c.id]=[]
      # print(c.decks)
      for cc in c.decks:
        card_deck[c.id].append(cc.deck_id)
    # print (card_deck)

    #print (users_cards)
    
    deck_dict={}
    for i in users_decks:
      deck_dict[i.id]=i.deck_name

    return render_template("view_cards.html",username=current_user.username,cards=users_cards,decks=users_decks,card_deck=card_deck,deck_dict=deck_dict)
  


if __name__=='__main__':
  app.run(host='0.0.0.0',debug=True)