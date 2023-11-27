import sqlite3
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html') #work in progress

@app.route('/signup.html',methods=['GET'])
def signupPage():
    return render_template('signup.html')

@app.route('/login.html',methods=['GET'])
def loginPage():
    return render_template('login.html')

@app.route('/home.html')
def  homePage():
    return render_template('home.html')

@app.route('/about.html')
def aboutPage():
    return render_template('about.html')

@app.route('/signup', methods=['POST'])
def register():
    if request.method == 'POST':
        # print("nijesh")
        conn = sqlite3.connect('split.db')
        cur = conn.cursor()
        
        username = request.form['user-username']
        name  = request.form['user-name']
        email = request.form['user-email']
        password = request.form['user-password']
        confirm_password = request.form['user-confirm-password']
        country_code = request.form['user-mobile-country-code']
        phone_number = request.form['user-mobile-number']
        currency = request.form['user-currency']
##str( new friend id ) fetch fids concatenate new frnd id then update
        if password != confirm_password:
            # flash('Passwords do not match.')
            pass
        else:
            # Insert new user data into the 'users' table
            cur.execute('INSERT INTO users (uname, name, email, password, currency, country_code, mobile_number) VALUES (?, ?, ?, ?, ?, ?, ?);',
                         (username,name, email, password, currency, country_code, phone_number))
            conn.commit()
            # flash('Registration successful. Please log in.')
            
            # return redirect(url_for('login'))
        conn.close()
        return render_template('login.html')

@app.route('/user-page-dump', methods=['GET'])
def loadUserPage():
    uid=int(request.get_json()['uid'])

    conn = sqlite3.connect('split.db')
    cur = conn.cursor()
    
    cur.execute(f"select * from users WHERE uid={uid}")

    udata=cur.fetchone()
    user={"uid":udata[0], "uname":udata[1], "name":udata[2], "email":udata[3], "password":udata[4], "currency":udata[5], "country_code": udata[6], "mobile_number":udata[7], "friend_IDs":udata[8]}

    groups=[]
    cur.execute(f'SELECT * FROM groups WHERE members LIKE "% " || "{udata[0]}" || " %";')
    for group in cur.fetchall():
        groups+=[{'gid': group[0], 'group_name': group[1]}]
    
    friends=[]
    cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{udata[0]}" || " %";')
    for friend in cur.fetchall():
        friends+=[{"uid":friend[0], "uname":friend[1], "name":friend[2], "email":friend[3], "password":friend[4], "currency":friend[5], "country_code": friend[6], "mobile_number":friend[7], "friend_IDs":friend[8]}]

    transactions=[]
    cur.execute(f'SELECT * FROM transactions WHERE lender_id={udata[0]} OR borrower_id={udata[0]} ORDER BY timestamp DESC LIMIT 10;')
    result=cur.fetchall()
    for txn in cur.fetchall():
        lname=cur.execute(f'SELECT * FROM users WHERE uid="{txn[2]}";').fetchone()[1]
        bname=cur.execute(f'SELECT * FROM users WHERE uid="{txn[3]}";').fetchone()[1]
        transactions+=[{'uid': udata[0],'completed': txn[4],'lender_id':txn[2],'borrower_id': txn[3],'l_name': lname, 'b_name': bname, 'amount': txn[1], 'description':txn[8]}]
    print(transactions)
    conn.close()
    return render_template('user_page.html', user=user, groups=groups, friends=friends, transactions=transactions)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('split.db')
        cur = conn.cursor()
        username = request.form['user-username']
        password = request.form['user-password']
        
        #validate usename and password
        usernames=[x[0] for x in cur.execute('SELECT uname FROM users;').fetchall()]
        if username not in usernames:
            return render_template('login.html', username_not_found=1)
        
        correctPassword=cur.execute(f'SELECT password FROM users WHERE uname="{username}";').fetchone()[0]
        if password != correctPassword:
            return render_template('login.html', incorrect_password=1)

        # Insert new user data into the 'users' table
        cur.execute("select * from users WHERE uname=?", (username,))
        # flash('Logged in successfully')

        udata=cur.fetchone()
        user={"uid":udata[0], "uname":udata[1], "name":udata[2], "email":udata[3], "password":udata[4], "currency":udata[5], "country_code": udata[6], "mobile_number":udata[7], "friend_IDs":udata[8]}

        groups=[]
        cur.execute(f'SELECT * FROM groups WHERE members LIKE "% " || "{udata[0]}" || " %";')
        for group in cur.fetchall():
            groups+=[{'gid': group[0], 'group_name': group[1]}]
        
        friends=[]
        cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{udata[0]}" || " %";')
        for friend in cur.fetchall():
            friends+=[{"uid":friend[0], "uname":friend[1], "name":friend[2], "email":friend[3], "password":friend[4], "currency":friend[5], "country_code": friend[6], "mobile_number":friend[7], "friend_IDs":friend[8]}]

        transactions=[]
        cur.execute(f'SELECT * FROM transactions WHERE lender_id={udata[0]} OR borrower_id={udata[0]} ORDER BY timestamp DESC LIMIT 10;')
        result=cur.fetchall()
        for txn in cur.fetchall():
            lname=cur.execute(f'SELECT * FROM users WHERE uid="{txn[2]}";').fetchone()[1]
            bname=cur.execute(f'SELECT * FROM users WHERE uid="{txn[3]}";').fetchone()[1]
            transactions+=[{'uid': udata[0],'completed': txn[4],'lender_id':txn[2],'borrower_id': txn[3],'l_name': lname, 'b_name': bname, 'amount': txn[1], 'description':txn[8]}]
        
        conn.close()
        return render_template('user_page.html', user=user, groups=groups, friends=friends, transactions=transactions)


@app.route('/group-dump', methods=['GET','POST'])
def loadGroupPage():
    # print(request.get_json()['gid'],type(request.get_json()['gid']))
    gid=int(request.get_json()['gid'])
    uid=int(request.get_json()['uid'])
    
    con = sqlite3.connect('split.db')
    cur = con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    groupData=cur.execute(f'SELECT * FROM groups where gid={gid};').fetchone()
    group={'gid': groupData[0], 'group_name': groupData[1], 'members': groupData[2], 'group_type': groupData[3], 'date_created': groupData[4]}

    memberIDs=[int(x) for x in groupData[2].strip().split()]
    membersData=[]
    for mID in memberIDs:
        memData=cur.execute(f'SELECT * FROM users where uid={mID};').fetchone()
        membersData+=[{"uid":memData[0], "uname":memData[1], "name":memData[2], "email":memData[3], "password":memData[4], "currency":memData[5], "country_code": memData[6], "mobile_number":memData[7], "friend_IDs":memData[8]}]
    
    transactionsData=[]
    group_txn_IDs=[x[0] for x in cur.execute(f'SELECT DISTINCT group_txn_id FROM transactions WHERE group_id={gid};').fetchall()]

    for gtID in group_txn_IDs:
        txns=[]

        tData = cur.execute('SELECT * FROM transactions WHERE group_id=? AND group_txn_id=?', (gid, gtID)).fetchall()
        for txn in tData:
            txns+=[{'tid': txn[0], 'amount': txn[1], 'lender_id': txn[2], 'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]
        transactionsData.append(txns)

    #code for stats
    m2u=0 # how much user is owed by rest of the members (total)
    u2m=0 # how much user owes any other member (total)
    overall=0 # total dues wrt user

    m2u=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid};').fetchone()[0]
    u2m=cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid};').fetchone()[0]
    
    if u2m is None:
        u2m=0
    else:
        u2m=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid};').fetchone()[0])
    if m2u is None:
        m2u=0
    else:
        m2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid};').fetchone()[0])

    overall=m2u - u2m
    con.close()

    return render_template('group_page.html',dues={'u2m':u2m, 'm2u':m2u, 'overall':overall}, user=user, group=group, members=membersData, transactions=transactionsData)



@app.route('/friend-dump',methods=['GET','POST'])
def loadFriendPage():
    fid=int(request.get_json()['fid']) # friend's id
    uid=int(request.get_json()['uid']) # user's id

    con = sqlite3.connect('split.db')
    cur = con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    fData=cur.execute(f'SELECT * FROM users WHERE uid={fid};').fetchone()
    friend={"uid":fData[0], "uname":fData[1], "name":fData[2], "email":fData[3], "password":fData[4], "currency":fData[5], "country_code": fData[6], "mobile_number":fData[7], "friend_IDs":fData[8]}
    friends_of_friend=[]
    fofData=cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{fData[0]}" || " %";').fetchall()
    for fof in fofData:
        friends_of_friend+=[{"uid":fof[0], "uname":fof[1], "name":fof[2], "email":fof[3], "password":fof[4], "currency":fof[5], "country_code": fof[6], "mobile_number":fof[7], "friend_IDs":fof[8]}]
    
    mutual_txns=[]
    txnsData=cur.execute(f'SELECT * FROM transactions WHERE (lender_id ={uid} AND borrower_id={fid}) OR (lender_id ={fid} AND borrower_id={uid});').fetchall()
    for txn in txnsData:
        mutual_txns+=[{'tid': txn[0], 'amount': txn[1], 'lender_id': txn[2], 'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]


    #code for stats!
    # f2u=0 #amount owed by ffriend to user
    overall=0 #overall dues. if +ve, then f owes u, if -ve then u owes f

    u2f=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={fid} AND borrower_id={uid};').fetchone()[0]
    if u2f is None:
        u2f=0 #amount owed by user to friend
    else:
        u2f=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={fid} AND borrower_id={uid};').fetchone()[0])

    f2u=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND borrower_id={fid};').fetchone()[0]
    if f2u is None:
        f2u=0
    else:
        f2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND borrower_id={fid};').fetchone()[0])


    overall=f2u - u2f
    
    con.close()
    # return render_template('home.html')
    return render_template('friend_page.html', dues={'u2f':u2f, 'f2u':f2u, 'overall':overall}, user=user, friend=friend, friends_of_friend=friends_of_friend, mutual_txns=mutual_txns)

#code for adding friends

#loading page
@app.route('/add_friend.html', methods=['GET'])
def loadAddFriendPage():
    uid=int(request.args.get('uid'))

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    con.close()
    return render_template('add_friend.html', user=user)

#searching for users with a given name
@app.route('/fetch_add_friend_search_request', methods=['POST'])
def sendFriendCandidates():
    uid=int(request.form['uid'])
    candidateName=request.form['candidate']
    con = sqlite3.connect('split.db')
    cur=con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}

    
    candidates=[]
    cData=cur.execute(f'SELECT * FROM users WHERE lower(name)="{candidateName.lower()}";').fetchall()
    for c in cData:

        if int(c[0]) !=int(uid):
            candidates+=[{"uid":c[0], "uname":c[1], "name":c[2], "email":c[3], "password":c[4], "currency":c[5], "country_code": c[6], "mobile_number":c[7], "friend_IDs":c[8]}]

    con.close()
    return render_template('add_friend.html', user=user, candidates=candidates)

#add selected user as friend
@app.route('/addfriend', methods=['POST'])
def addCandidateAsFriend():
    uid=int(request.get_json()['uid'])
    fid=int(request.get_json()['candidate_id'])

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}

    user_friends= user['friend_IDs']
    friend_friends= cur.execute(f'SELECT friend_IDs FROM users WHERE uid={fid};').fetchone()[0]

    if user_friends is None:
        user_friends=" " + str(fid) + " "
    else:
        user_friends+= str(fid) + " "

    if friend_friends is None:
        friend_friends= " " + str(uid)+ " "
    else:
        friend_friends+= str(uid) + " "
        

    cur.execute(f'UPDATE users SET friend_IDs="{user_friends}" WHERE uid={uid};')
    cur.execute(f'UPDATE users SET friend_IDs="{friend_friends}" WHERE uid={fid};')

    con.commit()
    con.close()
    return render_template('add_friend.html', user=user)



#code for creating a group
#loading page
@app.route('/create_group.html', methods=['GET'])
def loadCreateGroupPage():
    uid=int(request.args.get('uid'))

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}

    con.close()
    return render_template('create_group.html', user=user)

#creating a group with given name, assuming user doesn't repeat names
@app.route('/create_group_dump', methods=['POST'])
def createGroup():
    gname=request.form['gname']
    uid=int(request.form['uid'])

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}

    existingGroups=cur.execute(f'SELECT group_name FROM groups WHERE members LIKE "% " || "{uid}" || " %";').fetchall()
    if (gname,) in existingGroups:
        return render_template('create_group.html', user=user, group_already_exists=1) ## to be done in html file and css

    #otherwise, create new group

    cur.execute(f'INSERT INTO groups (group_name, members) VALUES ("{gname}", " " || "{user["uid"]}" ||  " ");')

    con.commit()

    #get group id of new group
    gid=cur.execute(f'SELECT gid FROM groups WHERE group_name="{gname}";').fetchone()[0]

    #get friends' data to add to group
    friends=[]
    cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{uid}" || " %";')
    for friend in cur.fetchall():
        friends+=[{"uid":friend[0], "uname":friend[1], "name":friend[2], "email":friend[3], "password":friend[4], "currency":friend[5], "country_code": friend[6], "mobile_number":friend[7], "friend_IDs":friend[8]}]
    
    con.close()
    return render_template('create_group.html', user=user, gid=gid, gname=gname, friends=friends)

#adding members to group
@app.route('/add_member_to_group', methods=['POST'])
def addFriendToGroup():
    # print(request.get_json()['uid'], type(request.get_json()['uid']))
    uid=int(request.get_json()['uid'])
    fid=int(request.get_json()['friend_id'])
    gid=int(request.get_json()['gid'])

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}

    groupData=cur.execute(f'SELECT * FROM groups where gid={gid};').fetchone()
    print(groupData)
    group={'gid': groupData[0], 'group_name': groupData[1], 'members': groupData[2], 'group_type': groupData[3], 'date_created': groupData[4]}
    
    members=group['members']+ str(fid) + " "
    group['members']=members
    cur.execute(f'UPDATE groups SET members="{members}" WHERE gid={gid};')
    con.commit()

    friends=[]
    cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{uid}" || " %";')
    members=members.strip().split()
    for friend in cur.fetchall():
        if friend[0] not in members:
            friends+=[{"uid":friend[0], "uname":friend[1], "name":friend[2], "email":friend[3], "password":friend[4], "currency":friend[5], "country_code": friend[6], "mobile_number":friend[7], "friend_IDs":friend[8]}]
    
    con.close()
    return render_template('create_group.html', user=user, gid=gid, group=group, friends=friends)

#code for splitting a bill in a group
@app.route('/add_g_transaction', methods=['POST'])
def addGroupTransaction():
    uid=int(request.form['uid'])
    gid=int(request.form['gid'])
    description=request.form['description']
    amount=float(request.form['amount'])

    con = sqlite3.connect('split.db')
    cur = con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    groupData=cur.execute(f'SELECT * FROM groups where gid={gid};').fetchone()
    group={'gid': groupData[0], 'group_name': groupData[1], 'members': groupData[2], 'group_type': groupData[3], 'date_created': groupData[4]}
    
    group_txns_count=cur.execute(f'SELECT count(DISTINCT group_txn_id) FROM transactions WHERE group_id={gid};').fetchone()[0]

    memberIDs=[int(x) for x in groupData[2].strip().split()]
    membersData=[]
    for mID in memberIDs:
        memData=cur.execute(f'SELECT * FROM users where uid={mID};').fetchone()
        membersData+=[{"uid":memData[0], "uname":memData[1], "name":memData[2], "email":memData[3], "password":memData[4], "currency":memData[5], "country_code": memData[6], "mobile_number":memData[7], "friend_IDs":memData[8]}]
    
    #adding txns to txn table
    for mID in memberIDs:
        if mID != uid:
            cur.execute(f'INSERT INTO transactions(amount, lender_id, borrower_id, completed, group_txn_id, group_id, description) \
                    VALUES({round(amount/(len(memberIDs)), 2)},{uid}, {mID}, 0, {group_txns_count+1}, {gid}, "{description}");')
            con.commit()


    #refetching txn data to update group page
    transactionsData=[]
    group_txn_IDs=[x[0] for x in cur.execute(f'SELECT DISTINCT group_txn_id FROM transactions WHERE group_id={gid};').fetchall()]


    print(group_txn_IDs)
    for gtID in group_txn_IDs:
        txns=[]
        tData = cur.execute('SELECT * FROM transactions WHERE group_id=? AND group_txn_id=?', (gid, gtID)).fetchall()

        for txn in tData:
            txns+=[{'tid': txn[0], 'amount': txn[1], 'lender_id': txn[2], 'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]
        transactionsData+=[txns]

    #code for stats
    m2u=0 # how much user is owed by rest of the members (total)
    u2m=0 # how much user owes any other member (total)
    overall=0 # total dues wrt user

    m2u=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid};').fetchone()[0]
    u2m=cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid};').fetchone()[0]
    
    if u2m is None:
        u2m=0
    else:
        u2m=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid};').fetchone()[0])
    if m2u is None:
        m2u=0
    else:
        m2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid};').fetchone()[0])

    overall=m2u - u2m

    con.close()
    return render_template('group_page.html',dues={'u2m':u2m, 'm2u':m2u, 'overall':overall}, user=user, group=group, members=membersData, transactions=transactionsData)
    
#code for adding an indiv txn b/w 2 friends
@app.route('/add_f_transaction', methods=['POST'])
def addFriendTransaction():
    uid=int(request.form['uid'])
    fid=int(request.form['fid'])
    description=request.form['description']
    amount=float(request.form['amount'])

    con = sqlite3.connect('split.db')
    cur = con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}

    cur.execute(f'INSERT INTO transactions(amount, lender_id, borrower_id, completed, group_txn_id, group_id, description) \
                    VALUES({round(amount/2, 2)},{uid}, {fid}, 0, 0, 0, "{description}");')
    con.commit()

    #refetching required data
    fData=cur.execute(f'SELECT * FROM users WHERE uid={fid};').fetchone()
    friend={"uid":fData[0], "uname":fData[1], "name":fData[2], "email":fData[3], "password":fData[4], "currency":fData[5], "country_code": fData[6], "mobile_number":fData[7], "friend_IDs":fData[8]}
    friends_of_friend=[]
    fofData=cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{fData[0]}" || " %";').fetchall()
    for fof in fofData:
        friends_of_friend+=[{"uid":fof[0], "uname":fof[1], "name":fof[2], "email":fof[3], "password":fof[4], "currency":fof[5], "country_code": fof[6], "mobile_number":fof[7], "friend_IDs":fof[8]}]
    
    mutual_txns=[]
    txnsData=cur.execute(f'SELECT * FROM transactions WHERE (lender_id ={uid} AND borrower_id={fid}) OR (lender_id ={fid} AND borrower_id={uid});').fetchall()
    for txn in txnsData:
        mutual_txns+=[{'tid': txn[0], 'amount': txn[1], 'lender_id': txn[2], 'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]
    
    #code for stats!
    # f2u=0 #amount owed by ffriend to user
    overall=0 #overall dues. if +ve, then f owes u, if -ve then u owes f

    u2f=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={fid} AND borrower_id={uid};').fetchone()[0]
    if u2f is None:
        u2f=0 #amount owed by user to friend
    else:
        u2f=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={fid} AND borrower_id={uid};').fetchone()[0])

    f2u=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND borrower_id={fid};').fetchone()[0]
    if f2u is None:
        f2u=0
    else:
        f2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND borrower_id={fid};').fetchone()[0])


    overall=f2u - u2f
    
    
    con.close()
    return render_template('friend_page.html', dues={'u2f':u2f, 'f2u':f2u, 'overall':overall}, user=user, friend=friend, friends_of_friend=friends_of_friend, mutual_txns=mutual_txns)

#code for group transaction page, linked from group page
@app.route('/group-txn-page-dump', methods=['POST'])
def showGroupTxnDetails():
    uid=int(request.get_json()['uid'])
    gid=int(request.get_json()['gid'])
    group_txn_id=int(request.get_json()['group_txn_id'])

    con = sqlite3.connect('split.db')
    cur = con.cursor()

    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    groupData=cur.execute(f'SELECT * FROM groups where gid={gid};').fetchone()
    group={'gid': groupData[0], 'group_name': groupData[1], 'members': groupData[2], 'group_type': groupData[3], 'date_created': groupData[4]}
    
    memberIDs=[int(x) for x in groupData[2].strip().split()]
    membersData=[]
    for mID in memberIDs:
        memData=cur.execute(f'SELECT * FROM users where uid={mID};').fetchone()
        membersData+=[{"uid":memData[0], "uname":memData[1], "name":memData[2], "email":memData[3], "password":memData[4], "currency":memData[5], "country_code": memData[6], "mobile_number":memData[7], "friend_IDs":memData[8]}]

    txns=[]
    txn_details=cur.execute(f'SELECT * FROM transactions WHERE group_txn_id={group_txn_id} AND group_id={gid};')
    for txn in txn_details:
        txns+=[{'tid': txn[0], 'amount': txn[1],'lender_name': membersData[memberIDs.index(txn[2])]['name'],'lender_id': txn[2],'borrower_name': membersData[memberIDs.index(txn[3])]['name'],'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]
    
    #code for stats
    m2u=0 # how much user is owed by rest of the members (total)
    u2m=0 # how much user owes any other member (total)
    overall=0 # total dues wrt user

    m2u=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0]
    u2m=cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0]
    
    if u2m is None:
        u2m=0
    else:
        u2m=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0])
    if m2u is None:
        m2u=0
    else:
        m2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0])

    overall=m2u - u2m
    
    con.close()
    return render_template('group_transaction.html', dues={'u2m':u2m, 'm2u':m2u, 'overall':overall}, user=user, group=group, transactions=txns)


#code for deleting group txns from group page
@app.route('/delete-group-txn-dump', methods=['POST', 'GET'])
def deleteGroupTransaction():
    uid=int(request.get_json()['uid'])
    gid=int(request.get_json()['gid'])
    group_txn_id=int(request.get_json()['group_txn_id'])

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    cur.execute(f'DELETE FROM transactions WHERE group_id={gid} AND group_txn_id={group_txn_id};')
    con.commit()

    #refetch data to refresh group page
    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    groupData=cur.execute(f'SELECT * FROM groups where gid={gid};').fetchone()
    group={'gid': groupData[0], 'group_name': groupData[1], 'members': groupData[2], 'group_type': groupData[3], 'date_created': groupData[4]}

    memberIDs=[int(x) for x in groupData[2].strip().split()]
    membersData=[]
    for mID in memberIDs:
        memData=cur.execute(f'SELECT * FROM users where uid={mID};').fetchone()
        membersData+=[{"uid":memData[0], "uname":memData[1], "name":memData[2], "email":memData[3], "password":memData[4], "currency":memData[5], "country_code": memData[6], "mobile_number":memData[7], "friend_IDs":memData[8]}]
    
    transactionsData=[]
    # group_txn_IDs=cur.execute(f'SELECT group_txn_id FROM transactions WHERE group_id={gid};')
    group_txn_IDs=[x[0] for x in cur.execute(f'SELECT DISTINCT group_txn_id FROM transactions WHERE group_id={gid};').fetchall()]
    for gtID in group_txn_IDs:
        txns=[]
        tData=cur.execute(f'SELECT * FROM transactions WHERE group_id={gid} AND group_txn_id={gtID};').fetchall()
        for txn in tData:
            txns+=[{'tid': txn[0], 'amount': txn[1], 'lender_id': txn[2], 'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]
        transactionsData+=[txns]
    
    #code for stats
    m2u=0 # how much user is owed by rest of the members (total)
    u2m=0 # how much user owes any other member (total)
    overall=0 # total dues wrt user

    m2u=cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0]
    u2m=cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0]
    
    if u2m is None:
        u2m=0
    else:
        u2m=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE borrower_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0])
    if m2u is None:
        m2u=0
    else:
        m2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND group_id={gid} AND group_txn_id={group_txn_id};').fetchone()[0])

    overall=m2u - u2m

    con.close()
    return render_template('group_page.html',dues={'u2m':u2m, 'm2u':m2u, 'overall':overall}, user=user, group=group, members=membersData, transactions=transactionsData)

#code for deleting indiv (not those part of group) transactions from friend page
@app.route('/delete-friend-txn-dump', methods=['POST'])
def deleteFriendTransaction():
    uid=int(request.get_json()['ui'])
    fid=int(request.get_json()['fid'])
    tid=int(request.get_json['tid'])

    con = sqlite3.connect('split.db')
    cur=con.cursor()

    cur.execute(f'DELETE FROM transactions WHERE ((lender_id={uid} AND borrower_id={fid}) OR  (lender_id={fid} AND borrower_id={uid})) AND group_txn_id=0 AND group_id=0 AND tid={tid};')
    con.commit()

    #refetching data to refresh friend page
    userData=cur.execute(f'SELECT * FROM users WHERE uid={uid};').fetchone()
    user={"uid":userData[0], "uname":userData[1], "name":userData[2], "email":userData[3], "password":userData[4], "currency":userData[5], "country_code": userData[6], "mobile_number":userData[7], "friend_IDs":userData[8]}
    
    fData=cur.execute(f'SELECT * FROM users WHERE uid={fid};').fetchone()
    friend={"uid":fData[0], "uname":fData[1], "name":fData[2], "email":fData[3], "password":fData[4], "currency":fData[5], "country_code": fData[6], "mobile_number":fData[7], "friend_IDs":fData[8]}
    friends_of_friend=[]
    fofData=cur.execute(f'SELECT * FROM users WHERE friend_IDs LIKE "% " || "{fData[0]}" || " %";').fetchall()
    for fof in fofData:
        friends_of_friend+={"uid":fof[0], "uname":fof[1], "name":fof[2], "email":fof[3], "password":fof[4], "currency":fof[5], "country_code": fof[6], "mobile_number":fof[7], "friend_IDs":fof[8]}
    
    mutual_txns=[]
    txnsData=cur.execute(f'SELECT * FROM transactions WHERE (lender_id ={uid} AND borrower_id={fid}) OR (lender_id ={fid} AND borrower_id={uid});').fetchall()
    for txn in txnsData:
        mutual_txns+=[{'tid': txn[0], 'amount': txn[1], 'lender_id': txn[2], 'borrower_id': txn[3], 'completed': txn[4], 'group_txn_id': txn[5], 'group_id': txn[6], 'timestamp': txn[7], 'description': txn[8]}]
    
    #code for stats!
    u2f=0 #amount owed by user to friend
    f2u=0 #amount owed by ffriend to user
    overall=0 #overall dues. if +ve, then f owes u, if -ve then u owes f

    u2f=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={uid} AND borrower_id={fid};').fetchone()[0])
    f2u=float(cur.execute(f'SELECT sum(amount) FROM transactions WHERE lender_id={fid} AND borrower_id={uid};').fetchone()[0])
    overall=f2u - u2f
    
    con.close()
    return render_template('friend_page.html', dues={'u2f':u2f, 'f2u':f2u, 'overall':overall}, user=user, friend=friend, friends_of_friend=friends_of_friend, mutual_txns=mutual_txns)

def setupDatabase():
    con = sqlite3.connect('split.db')
    cur=con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY AUTOINCREMENT, uname varchar(100) NOT NULL, name varchar(100), email varchar(200), password varchar(300) NOT NULL, currency varchar(10), country_code varchar(5), mobile_number varchar(12), friend_IDs varchar(1000));")
    cur.execute("CREATE TABLE IF NOT EXISTS groups(gid INTEGER PRIMARY KEY AUTOINCREMENT, group_name varchar(100), members varchar(1000), group_type varchar(100), date_created datetime DEFAULT CURRENT_TIMESTAMP);")
    cur.execute("CREATE TABLE IF NOT EXISTS transactions(tid INTEGER PRIMARY KEY AUTOINCREMENT, amount float, lender_id INTEGER, borrower_id INTEGER, completed bit, group_txn_id INTEGER, group_id INTEGER, timestamp datetime DEFAULT CURRENT_TIMESTAMP, description varchar(300));")
    con.commit()
    con.close()


setupDatabase()

if __name__ == '__main__':
    app.run(debug=True)