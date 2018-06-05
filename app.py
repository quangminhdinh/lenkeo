from flask import Flask, render_template, request, redirect, session
from passlib.hash import sha256_crypt
import mlab
from base64 import b64encode
from bson.objectid import ObjectId
from mongoengine import *
import datetime
app = Flask(__name__)
app.config["SECRET_KEY"] = "piudfpasudfpa7wr09a113Q$ả$#2221y"
mlab.connect()

@app.route('/')
def index():
    try:
        username = session['username']
    except KeyError:
        username = None
    if username is None:
        return render_template('homepage.html')
    else:
        url = "/profile/" + username
        return redirect(url)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == "GET":
        prompt=0
        return render_template('signup.html',prompt=prompt,usn="",psw="",nm="",eml="")
    elif request.method == "POST":
        form = request.form
        username = form['username']
        password1=form['password']
        password = sha256_crypt.encrypt(password1)
        name = form['name']
        email = form['email']
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            account = None
        if account is None:
            account = Account(name=name, password=password, username=username, email=email)
            account.save()
            session["username"] = account.username
            url = "/profile/" + account.username
            return redirect(url)
        else:
            prompt=1
            return render_template('signup.html',prompt=prompt,usn=username,psw=password1,nm=name,eml=email)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        prompt=0
        return render_template('login.html',prompt=prompt,usn="",psw="")
    elif request.method == "POST":
        form = request.form
        username = form['username']
        password = form['password']
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            account = None
        if account is None:
            prompt=1
            # message = "Tài khoản không tồn tại"
            return render_template('login.html', prompt = prompt,usn=username,psw=password)
        else:
            if sha256_crypt.verify(password, account.password) == True:
                session["username"] = account.username
                url = "/profile/" + account.username
                return redirect(url)
            else:
                # message = "Sai mật khẩu"
                prompt=2
                return render_template('login.html', prompt = prompt,usn=username,psw=password)

class Account(Document):
    username = StringField()
    name = StringField()
    image = StringField()
    password = StringField()
    email = StringField()
    phone = StringField()
    #friend system
    friendlist = ListField()
    friend_accepted = ListField()
    #
    #bet system
    pending_bet = ListField()
    active_bet = ListField()
    win_bet = ListField()
    lost_bet = ListField()
    lost_bet_earned = ListField()
    other_claiming_winner_bets = ListField()
    #friend notify about game
    bet_spectator = ListField()

class Contract_type_1(Document):
    contract_maker = ListField()
    contract_term = StringField()
    contract_name = StringField()
    #traditional\
    party_left = ListField()
    party_right = ListField()
    party_left_pending = ListField()####
    party_right_pending = ListField()####
    #multiparty
    party_multiplayers = ListField()
    party_multiplayers_pending = ListField()####
    number_of_winner = StringField()
    #times
    dates = StringField()
    control = StringField()
    #
    spectator = ListField()
    punishment = StringField()
    #claim victory
    victory_claim = ListField()
    accept_verification_accept = ListField()
    accept_verification_decline = ListField()
    winner = ListField()
    loser  = ListField()
    #comments
    comments = ListField()

# def for traditional bet
def win_action(user_win, account, bet_id, bet):
    bet.update(add_to_set__winner = user_win)
    clone = Account.objects().get(username = user_win)
    clone.update(pull__other_claiming_winner_bets = bet_id)
    clone.update(pull__active_bet = bet_id)
    clone.update(add_to_set__win_bet = bet_id)

def lost_action(user_lost, account, bet_id, bet):
    bet.update(add_to_set__loser = user_lost)
    clone = Account.objects().get(username = user_lost)
    clone.update(pull__other_claiming_winner_bets = bet_id)
    clone.update(pull__active_bet = bet_id)
    clone.update(add_to_set__lost_bet = bet_id)

def reject_claim(user_reject, bet_id, bet):
    clone = Account.objects().get(username = user_reject)
    clone.update(pull__other_claiming_winner_bets = bet_id)
    bet.victory_claim = []
    bet.accept_verification_accept = []
    bet.accept_verification_decline = []
#
def call_element_include(notification, account, account_other, bets_to_show):
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for bet in account_other.active_bet:
        bets_to_show.insert(0, Contract_type_1.objects().with_id(bet))



@app.route('/facepage/<username_url>', methods=['GET','POST'])
def facepage(username_url):
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    hints = Account.objects()
    notification =[]
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    return render_template('facepage.html',     account = account,
                                                hints = hints,
                                                account_other = account_other,
                                                notification = notification)

@app.route('/lost.bet.unearned/<username_url>', methods=['GET','POST'])
def unearned_lost_bet(username_url):
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    hints = Account.objects()
    notification =[]
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    bets_to_show = []
    for bet in bets_to_show:
        if bet.dates != "":
            bet_dates = datetime.datetime.strptime(bet.dates, "%m/%d/%Y %I:%M %p")
            if bet_dates <  var_now:
                bet.update(control = 'out of date')
    for each in account_other.lost_bet:
        bets_to_show.insert(0, Contract_type_1.objects().with_id(each))
    if request.method == "GET":
        return render_template('lost-bet-unearned.html',    account = account,
                                                            hints = hints,
                                                            account_other = account_other,
                                                            notification = notification,
                                                            bets_to_show = bets_to_show)
    # elif request.method == "POST":
@app.route('/lost.bet.earned/<bet_id>/<username_url>', methods=['GET','POST'])
def earned_lost_bet(bet_id, username_url):
    account_other = Account.objects.get(username = username_url)
    account_other.update(pull__lost_bet = bet_id)
    account_other.update(add_to_set__lost_bet_earned = bet_id)
    url = '/lost.bet.unearned/' + username_url
    return redirect(url)


@app.route('/profile/<username_url>', methods=['GET','POST'])
def profile(username_url):
    hints = Account.objects()
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    bets_to_show = []
    notification =[]
    call_element_include(notification, account, account_other, bets_to_show)
    var_now = datetime.datetime.now()
    for bet in bets_to_show:
        if bet.dates != "":
            bet_dates = datetime.datetime.strptime(bet.dates, "%m/%d/%Y %I:%M %p")
            if bet_dates <  var_now:
                bet.update(control = 'out of date')
    bets_invited = []
    for bet in account_other.bet_spectator:
        bets_invited.insert(0, Contract_type_1.objects().with_id(bet))
    return render_template('profile.html',  account = account,
                                            account_other = account_other,
                                            bets_to_show = bets_to_show,
                                            hints = hints,
                                            notification = notification,
                                            bets_invited = bets_invited)


@app.route('/active.bet/<bet_id>', methods=['GET','POST'])
def active_bet(bet_id):
    hints = Account.objects()
    username = session['username']
    account = Account.objects.get(username = username)
    bet = Contract_type_1.objects().with_id(bet_id)
    hints = hints
    notification =[]
    var_now = datetime.datetime.now()
    if (len(bet.party_right_pending) + len(bet.party_right)) != 0 or (len(bet.party_left_pending) == 0 + len(bet.party_left)) != 0 :
        if bet.dates != "":
            bet_dates = datetime.datetime.strptime(bet.dates, "%m/%d/%Y %I:%M %p")
            if bet_dates <  var_now:
                bet.update(control = 'out of date')
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    return render_template('active_bet.html',   account = account,
                                                bet = bet,
                                                hints =hints,
                                                notification = notification)


@app.route('/delete.follow/<bet_id>/<username>', methods=['GET','POST'])
def delete_follow(bet_id, username):
    bet = Contract_type_1.objects.with_id(str(bet_id))
    account = Account.objects.get(username = username)
    account.update(pull__bet_spectator = bet_id)
    bet.update(pull__spectator = username)
    url = '/profile/' + username
    return redirect(url)







@app.route('/contract.type.1/<contract_class>', methods=['GET','POST'])
def contract_type_1(contract_class):
    username = session['username']
    account = Account.objects.get(username = username)
    friendlist_information = []
    notification =[]
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for friend in account.friendlist:
        friendlist_information.insert(0, Account.objects().get(username = friend))
    if request.method == "GET":
        hints = Account.objects()
        if contract_class == "traditional":
            return render_template('contract_type_1_traditional.html',  account = account,
                                                                        friendlist_information = friendlist_information,
                                                                        hints = hints,
                                                                        notification = notification)
        elif contract_class == "multiparty":
            return render_template('contract_type_1_multiparty.html',   account = account,
                                                                        friendlist_information = friendlist_information,
                                                                        hints = hints,
                                                                        notification = notification)
    elif request.method == "POST":
        form = request.form
        if contract_class == "traditional":
            contract_maker = []
            contract_name = form['contract_name']
            contract_maker.append(username)
            contract_term = form['contract_term']
            party_right_pending = form.getlist('party_right')
            party_left_pending = form.getlist('party_left')
            spectator = form.getlist('spectator')
            punishment = form['punishment']
            #times

            dates = form['dates']
            # times = form['times']
            contract_type_1 = Contract_type_1(  contract_maker = contract_maker,
                                                contract_term = contract_term,
                                                party_left_pending = party_left_pending,
                                                party_right_pending = party_right_pending,
                                                spectator = spectator,
                                                punishment = punishment,
                                                dates = dates,
                                                # times = times,
                                                contract_name = contract_name)
            contract_type_1.save()
            account.update(add_to_set__active_bet = str(contract_type_1.id))
            for account_other in contract_type_1.party_right_pending:
                if username in party_right_pending:
                    contract_type_1.update(pull__party_right_pending = username)
                    contract_type_1.update(add_to_set__party_right = username)
                clone = Account.objects().get(username = account_other)
                clone.update(add_to_set__pending_bet = str(contract_type_1.id))
            for account_other_1 in contract_type_1.party_left_pending:
                if username in party_left_pending:
                    contract_type_1.update(pull__party_left_pending = username)
                    contract_type_1.update(add_to_set__party_left = username)
                clone = Account.objects().get(username = account_other_1)
                clone.update(add_to_set__pending_bet = str(contract_type_1.id))
            for account_other_spec in contract_type_1.spectator:
                clone = Account.objects().get(username = account_other_spec)
                clone.update(add_to_set__bet_spectator = str(contract_type_1.id))
            account.update(pull__pending_bet = str(contract_type_1.id))
            url = '/profile/' + username
            return redirect(url)
        elif contract_class == "multiparty":
            contract_maker = []
            contract_name = form['contract_name']
            contract_maker.append(username)
            contract_term = form['contract_term']
            party_multiplayers_pending = form.getlist('party_multiplayers')
            number_of_winner = form['number_of_winner']
            spectator = form.getlist('spectator')
            punishment = form['punishment']
            #times

            dates = form['dates']
            # times = form['times']
            contract_type_1 = Contract_type_1(  contract_maker = contract_maker,
                                                contract_term = contract_term,
                                                party_multiplayers_pending = party_multiplayers_pending,
                                                number_of_winner = number_of_winner,
                                                spectator = spectator,
                                                punishment = punishment,
                                                dates = dates,
                                                # times = times,
                                                contract_name = contract_name)
            contract_type_1.save()
            contract_type_1.update(pull__party_multiplayers_pending = username)
            contract_type_1.update(add_to_set__party_multiplayers = username)
            account.update(add_to_set__active_bet = str(contract_type_1.id))
            for account_other in contract_type_1.party_multiplayers_pending:
                clone = Account.objects().get(username = account_other)
                clone.update(add_to_set__pending_bet = str(contract_type_1.id))
            for account_other_spec in contract_type_1.spectator:
                clone = Account.objects().get(username = account_other_spec)
                clone.update(add_to_set__bet_spectator = str(contract_type_1.id))
            account.update(pull__pending_bet = str(contract_type_1.id))
            url = '/profile/' + username
            return redirect(url)



@app.route('/bet.request/<method>/<bet_id>/<redirect_link>', methods=['GET','POST'])
def bet_request_method(method, bet_id, redirect_link):
    username = session['username']
    account = Account.objects.get(username = username)
    bet = Contract_type_1.objects.with_id(bet_id)
    if method == "decline":
        if len(bet.party_multiplayers) == 0:
            if username in bet.party_right_pending:
                bet.update(pull__party_right_pending = account.username)
            elif username in bet.party_left_pending:
                bet.update(pull__party_left_pending = account.username)
            url = '/check.decline/' + username + '/' +bet_id
            account.update(pull__pending_bet = bet_id)
            return redirect(url)
        else:
            bet.update(pull__party_multiplayers_pending = account.username)
        account.update(pull__pending_bet = bet_id)
    elif method == "accept":
        if len(bet.party_multiplayers) == 0:
            if username in bet.party_right_pending:
                bet.update(pull__party_right_pending = account.username)
                bet.update(add_to_set__party_right = account.username)
            elif username in bet.party_left_pending:
                bet.update(pull__party_left_pending = account.username)
                bet.update(add_to_set__party_left = account.username)
        else:
            bet.update(pull__party_multiplayers_pending = account.username)
            bet.update(add_to_set__party_multiplayers = account.username)
        account.update(pull__pending_bet = bet_id)
        account.update(add_to_set__active_bet = bet_id)
        if redirect_link == "profile":
            url = '/profile/' + username
        elif redirect_link == "active.bet":
            url = '/active.bet/' + bet_id
        return redirect(url)

@app.route('/check.decline/<username>/<bet_id>', methods=['GET','POST'])
def bet_decline_check(username, bet_id):
    username = session['username']
    account = Account.objects.get(username = username)
    bet = Contract_type_1.objects.with_id(bet_id)
    if (len(bet.party_right_pending) + len(bet.party_right)) == 0 or (len(bet.party_left_pending) == 0 + len(bet.party_left)) == 0 :
        for account in bet.party_left:
            clone = Account.objects.get(username = account)
            clone.update(pull__active_bet = bet_id)
        for account in bet.party_left_pending:
            clone = Account.objects.get(username = account)
            clone.update(pull__pending_bet = bet_id)
        for account in bet.party_right:
            clone = Account.objects.get(username = account)
            clone.update(pull__active_bet = bet_id)
        for account in bet.party_right_pending:
            clone = Account.objects.get(username = account)
            clone.update(pull__pending_bet = bet_id)
        for account in bet.spectator:
            clone = Account.objects.get(username = account)
            clone.update(pull__bet_spectator = bet_id)
        for account in bet.party_multiplayers_pending:
            clone = Account.objects.get(username = account)
            clone.update(pull__active_bet = bet_id)
        for account in bet.party_multiplayers:
            clone = Account.objects.get(username = account)
            clone.update(pull__pending_bet = bet_id)
        bet.delete()
    url = '/profile/' + username
    return redirect(url)

@app.route('/claim.victory/<username>/<bet_id>', methods=['GET','POST'])
def claim_victory(username, bet_id):
    username = session['username']
    account = Account.objects.get(username = username)
    bet = Contract_type_1.objects.with_id(bet_id)
    if len(bet.victory_claim) == 0:
        if len(bet.party_multiplayers) == 0:
            bet.update(add_to_set__victory_claim = account.username)
            if username in bet.party_right:
                for name_0 in bet.party_left:
                    clone = Account.objects().get(username = name_0)
                    clone.update(add_to_set__other_claiming_winner_bets = str(bet_id))
            if username in bet.party_left:
                for name_1 in bet.party_right:
                    clone = Account.objects().get(username = name_1)
                    clone.update(add_to_set__other_claiming_winner_bets = str(bet_id))
        else:
            bet.update(add_to_set__victory_claim = {'username' : account.username,
                                                    'vote_count_accept' : [],
                                                    'vote_count_decline' : []})
            for name_2 in bet.party_multiplayers:
                clone = Account.objects().get(username = name_2)
                clone.update(add_to_set__other_claiming_winner_bets = str(bet_id))
        url = '/active.bet/' + bet_id
        return redirect(url)
    elif len(bet.victory_claim) != 0:
        url = '/active.bet/' + bet_id
        return redirect(url)






@app.route('/bet.vote.victory/<method>/<bet_id>', methods=['GET','POST'])
def bet_vote_victory(method, bet_id):
    username = session['username']
    account = Account.objects.get(username = username)
    bet = Contract_type_1.objects.with_id(bet_id)
    if method == "accept":
        bet.update(add_to_set__accept_verification_accept = username)
        account.update(pull__other_claiming_winner_bets = bet_id)
        url = '/check/accept/' + bet_id
        return redirect(url)
    if method == "decline":
        bet.update(add_to_set__accept_verification_decline = username)
        account.update(pull__other_claiming_winner_bets = bet_id)
        url = '/check/decline/' + bet_id
        return redirect(url)
    # elif len(bet.party_multiplayers) != 0:

@app.route('/check/<method>/<bet_id>', methods=['GET','POST'])
def check_victory(method, bet_id):
    username = session['username']
    account = Account.objects.get(username = username)
    bet = Contract_type_1.objects.with_id(bet_id)
    if len(bet.party_multiplayers) == 0:
        if method == "accept":
            if bet.victory_claim[0] in bet.party_right:
                if len(bet.accept_verification_accept) >= 2/3 * len(bet.party_left):
                    for user_right in bet.party_right:
                        win_action(user_right, account, bet_id, bet)
                    for user_left in bet.party_left:
                        lost_action(user_left, account, bet_id, bet)
                    for pending in bet.party_left_pending:
                        clone = Account.objects().get(username = pending)
                        clone.update(pull__pending_bet = bet_id)
                    for pending in bet.party_right_pending:
                        clone = Account.objects().get(username = pending)
                        clone.update(pull__pending_bet = bet_id)
            elif bet.victory_claim[0] in bet.party_left:
                if len(bet.accept_verification_accept) >= 2/3 * len(bet.party_right):
                    for user_left in bet.party_left:
                        win_action(user_left, account, bet_id, bet)
                    for user_right in bet.party_right:
                        lost_action(user_right, account, bet_id, bet)
                    for pending in bet.party_left_pending:
                        clone = Account.objects().get(username = pending)
                        clone.update(pull__pending_bet = bet_id)
                    for pending in bet.party_right_pending:
                        clone = Account.objects().get(username = pending)
                        clone.update(pull__pending_bet = bet_id)
        elif method == "decline":
            if bet.victory_claim[0] in bet.party_right:
                if len(bet.accept_verification_decline) >= 2/3 * len(bet.party_left):
                    for user_right in bet.party_right:
                        reject_claim(user_right, bet_id, bet)
            elif bet.victory_claim[0] in bet.party_left:
                if len(bet.accept_verification_decline) >= 2/3 * len(bet.party_right):
                    for user_left in bet.party_left:
                        reject_claim(user_left, bet_id, bet)
        url = '/profile/' + username
        return redirect(url)
    if len(bet.party_multiplayers) != 0:
        if bet.number_of_winner == "Không giới hạn":
            number = ( len(bet.party_multiplayers) + len (party_multiplayers_pending))
            number_of_winner = number
        else:
            number_of_winner = int(bet.number_of_winner)
        if method == "accept":
            if len(bet.accept_verification_accept) >= 1/2 * len(bet.party_multiplayers):
                winner = bet.victory_claim
                bet.update(add_to_set__winner = winner)
                bet.victory_claim = []
                bet.accept_verification_accept = []
                bet.accept_verification_decline = []
                for name in bet.party_multiplayers:
                    clone = Account.objects().get(username = name)
                    clone.update(pull__other_claiming_winner_bets = bet_id)
            url = '/check.level.2/' + bet_id + '/' + number_of_winner
            return redirect(url)

        elif method == "decline":
            if len(bet.accept_verification_decline) >= 1/2 * len(bet.party_multiplayers):
                bet.victory_claim = []
                bet.accept_verification_accept = []
                bet.accept_verification_decline = []
                for name in bet.party_multiplayers:
                    clone = Account.objects().get(username = name)
                    clone.update(pull__other_claiming_winner_bets = bet_id)
            url = '/profile/' + username
            return redirect(url)


@app.route('/check.level.2/<bet_id>/<number_of_winner>', methods=['GET','POST'])
def check_victory_2(bet_id, number_of_winner):
    username = session['username']
    account = Account.objects.get(username = username)
    number_of_winner = int(number_of_winner)
    bet = Contract_type_1.objects.with_id(bet_id)
    for user in bet.party_multiplayers:
        if user not in bet.winner:
            clone = Account.objects().get(username = user)
            clone.update(pull__active_bet = bet_id)
            clone.update(add_to_set__lost_bet = bet_id)
    for user in bet.party_multiplayers_pending:
            clone = Account.objects().get(username = user)
            clone.update(pull__pending_bet = bet_id)
    url = '/profile/' + username
    return redirect(url)
















@app.route('/edit.profile/<username_url>', methods=['GET','POST'])
def edit_profile(username_url):
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    notification =[]
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    if request.method == "GET":
        hints = Account.objects()
        return render_template('edit_profile.html', account = account, hints = hints, account_other = account_other, notification = notification)
    elif request.method == "POST":
        form = request.form
        name = form['name']
        email = form['email']
        phone = form['phone']
        hidd = form['hidd']
        if hidd == "0":
            image = request.files['image']
            image = b64encode(image.read()).decode("utf-8")
            account.update(name = name, image = image, email = email, phone = phone)
        elif hidd == "1":
            background = request.files['background']
            background = b64encode(background.read()).decode("utf-8")
            account.update(name = name, background=background, email = email, phone = phone)
        else:
            account.update(name = name, email = email, phone = phone)
        url = '/edit.profile/' + username_url
        return redirect(url)



@app.route('/friend.list/<username_url>', methods=['GET','POST'])
def friend_list(username_url):
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    notification =[]
    hints = Account.objects()
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    return render_template('friend_list.html', account = account, hints = hints, account_other = account_other, notification = notification)



@app.route('/contract.list/<username_url>', methods=['GET','POST'])
def contract_list(username_url):
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    notification =[]
    hints = Account.objects()
    for each in account.pending_bet:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    for each in account.other_claiming_winner_bets:
        notification.insert(0, Contract_type_1.objects().with_id(each))
    bets_to_show = []
    for each in account_other.active_bet:
        bets_to_show.insert(0, Contract_type_1.objects().with_id(each))
    return render_template('contract_list.html', account = account, hints = hints, account_other = account_other, notification = notification, bets_to_show = bets_to_show)

@app.route('/friend.request/<method>/<username_url>', methods=['GET','POST'])
def friend_request_method(method, username_url):
    username = session['username']
    account = Account.objects.get(username = username)
    account_other = Account.objects.get(username = username_url)
    url = '/profile/' + username_url
    url_self = '/friend.list/' + username
    if method == "delete.friend":
        account.update(pull__friendlist = account_other.username)
        account_other.update(pull__friend_accepted = account.username)
        return redirect(url)
    elif method == "accept":
        account.update(add_to_set__friendlist = account_other.username)
        account_other.update(add_to_set__friend_accepted = account.username)
        return redirect(url)
    elif method == "clear":
        account.update(pull__friend_accepted = account_other.username)
        return redirect(url)


@app.route('/comment/<bet_id>/<username_url>/<link>', methods=['GET','POST'])
def comments(bet_id, username_url, link):
    username = session['username']
    bet = Contract_type_1.objects.with_id(bet_id)
    form = request.form
    comment = form['comment']
    bet.update(add_to_set__comments = {'username': username,
                                        'comment': comment})
    url = "/active.bet/" + bet_id
    return redirect(url)


@app.route('/logout', methods = ['GET'])
def logout():
    del session['username']
    return redirect('/login')

@app.route('/google71f185714e0c0e1a.html')
def search_console_gg():
    return render_template('google71f185714e0c0e1a.html')

if __name__ == '__main__':
  app.run(debug=True)
