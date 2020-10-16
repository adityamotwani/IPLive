from flask import Flask, render_template,request,redirect
from pycricbuzz import Cricbuzz
import mysql.connector
from iplive import IPLive
c = Cricbuzz()
global_pr={}
live_score={}

myconn = mysql.connector.connect(
  host="localhost",
  user="username",
  password="password",
  database="scratch"
)

def teamname(s):
    if s == "Chennai Super Kings":
        return "CSK"
    elif s == "Mumbai Indians":
        return "MI"
    elif s == "Royal Challengers Bangalore":
        return "RCB"
    elif s == "Kolkata Knight Riders":
        return "KKR"
    elif s == "Sunrisers Hyderabad":
        return "SRH"
    elif s == "Kings XI Punjab":
        return "KXIP"
    elif s == "Delhi Capitals":
        return "DC"
    elif s == "Rajasthan Royals":
        return "RR"
'''def short_score(match_id,pr):
        live_score={}
        sc=c.scorecard(match_id)
        over_ball= sc['scorecard'][0]['overs']
        over=int(float(over_ball))
        if float(over_ball)!=int(float(over_ball)):
            ball=float(over_ball)-int(float(over_ball))
            ball/=0.6
            over+=ball
        if over!=0:
            crr=int(sc['scorecard'][0]['runs'])/over
        crr=round(crr,2)
        runs_req='NULL'
        if int(sc['scorecard'][0]['inng_num'])==2:
            runs_req=int(sc['scorecard'][1]['runs'])+1-int(sc['scorecard'][0]['runs'])
        over_left=20-over
        rrr='NULL'
            
        if over_left!=0 and int(sc['scorecard'][0]['inng_num'])==2:
            rrr=runs_req/over_left
        if rrr!='NULL':
            rrr=round(rrr,2)

        bowl_name=""
        bowl_wicks=""
        bowl_runs=""
        if len(pr)!=0:
            for i in pr['scorecard'][0]['bowlcard']:
                ind=0
                for j in range(len(sc)):
                    if sc['scorecard'][0]['bowlcard'][j]['name']==i['name']:
                        ind=j
                        break
                if i['overs']!=sc['scorecard'][0]['bowlcard'][ind]['overs']:
                    bowl_name=i['name']
                    bowl_runs=i['runs']
                    bowl_wicks=i['wickets']
                    break
        else:
            bowl_name=sc['scorecard'][0]['bowlcard'][-1]['name']
            bowl_runs=sc['scorecard'][0]['bowlcard'][-1]['runs']
            bowl_wicks=sc['scorecard'][0]['bowlcard'][-1]['wickets']
        bat_1=-1
        for i in range(len(sc['scorecard'][0]['batcard'])):
            if sc['scorecard'][0]['batcard'][i]['dismissal']=='batting' or sc['scorecard'][0]['batcard'][i]['dismissal']=='not out':
                bat_1=i
                break
        live_score= { 'runs': sc['scorecard'][0]['runs'] , 'wickets':sc['scorecard'][0]['wickets'], 'crr':crr, 'rrr':rrr,'req_runs':runs_req, 'bat1':sc['scorecard'][0]['batcard'][bat_1]['name'],'bat2':sc['scorecard'][0]['batcard'][-1]['name'], 'run1':sc['scorecard'][0]['batcard'][bat_1]['runs'],'run2':sc['scorecard'][0]['batcard'][-1]['runs'],'bowl':bowl_name,'bowl_wick':bowl_wicks,'bowl_run':bowl_runs ,'team':teamname(sc['scorecard'][0]['batteam']), 'over_ball':sc['scorecard'][0]['overs'],'ball_faced_1':sc['scorecard'][0]['batcard'][bat_1]['balls'],'ball_faced_2':sc['scorecard'][0]['batcard'][-1]['balls'] }
        #print(live_score)
        return live_score'''

def prv_inn(sc):
    if len(sc['scorecard'])>1:
        over_ball= sc['scorecard'][1]['overs']
        over=int(float(over_ball))
        if float(over_ball)!=int(float(over_ball)):
            ball=float(over_ball)-int(float(over_ball))
            ball/=0.6
            over+=ball
        crr=0
        if over!=0:
            crr=int(sc['scorecard'][0]['runs'])/over
        
        return {'runs': sc['scorecard'][1]['runs'] , 'wickets':sc['scorecard'][1]['wickets'], 'crr':crr,'team':teamname(sc['scorecard'][1]['batteam']), 'over_ball':sc['scorecard'][1]['overs']}
    else:
            return {'runs': '-' , 'wickets':'-', 'crr':'-','team':teamname(sc['scorecard'][0]['bowlteam']), 'over_ball':'-'}

def db_to_bowl(match_id):
    sql="SELECT * FROM BOWLER where MATCH_ID='"+ match_id+"';"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql)
    bowtable = iplcursor.fetchall()
    table=[]
    for j in bowtable:
        table.append({})
        for i in range(len(j)):
            if i==0:
                a="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+j[i]+"';"
                iplcursor.execute(a)
                name = iplcursor.fetchall()
                table[-1]['name']=name[0][0]
                table[-1]['team']=j[i][:2:]
            if i==2:
                table[-1]['wicks']=j[i]
            if i==3:
                table[-1]['econ']=j[i]
            if i==6:
                table[-1]['runs']=j[i]
            if i==7:
                table[-1]['over']=j[i]
    return table

def db_to_match():
  sql="SELECT * FROM MATCHH ;"
  iplcursor = myconn.cursor()
  iplcursor.execute(sql)
  matchtable = iplcursor.fetchall()
  match={}
  matchtb=[]
  for i in matchtable:
    if 'won' in i[-1].split():
      match['id']=i[0]
      match['team1']=i[1]
      match['team2']=i[2]
      match['stad']=i[3]
      match['date']=i[4]
      match['result']=i[-1]
      matchtb.append(match)
      match={}
  return matchtb[::-1]

def do_it():
    x = IPLive()
    global live_score
    global global_pr
    try:
        x.insert_matchh_details()
    except:
        pass
    try:
        x.insert_fall_of_wicket()
    except:
        pass
    try:
        x.insert_batsman_details()
    except:
        pass
    lss=live_score.copy()
    try:
        live_score=x.get_short_score(global_pr)
    except:
        pass
    
    try:
        global_pr=x.get_score(global_pr,lss)
    except:
        pass
    try:
        x.insert_bowler_details()
    except:
        pass
    try:
        x.get_commentary()
    except:
        pass
    return x.match_id
    print(live_score)

def db_to_bat(match_id):
  sql="SELECT * FROM BATSMAN WHERE MATCH_ID="+match_id+";"
  sql2="SELECT * FROM WICKETS WHERE MATCH_ID="+match_id+";"
  sql3="SELECT TEAM_1,TEAM_2 from MATCHH WHERE MATCH_ID="+match_id+";"
  iplcursor = myconn.cursor()
  iplcursor.execute(sql)
  battable = iplcursor.fetchall()
  iplcursor.execute(sql2)
  wittable = iplcursor.fetchall()
  iplcursor.execute(sql3)
  teams = iplcursor.fetchall()
  print(teams)
  t1=teams[0][0]
  t2=teams[0][1]
  prt=""
  try:
    prt=battable[0][0][:2:]
  except:
    pass
  bat_tb=[]
  d=0
  if len(battable) and t1[:2:]==battable[0][0][:2:] :
    bat_tb.append(t1)
    bat_tb.append([])
    d=1
  else:
    bat_tb.append(t2)
    bat_tb.append([])
    d=0
    
  for i in battable:
    if i[0][:2:]!=prt:
      bat_tb.append(teams[0][d])
      prt=i[0][:2:]
      bat_tb.append([])
    bat_i={}
    bat_i['pos']=i[2]
    a="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[0]+"';"
    #print(a)
    iplcursor.execute(a)
    name = iplcursor.fetchall()
    c=1
    bat_i['name']=name[0][0]
    for j in wittable:
      if j[1]==i[0]:
        c=0
        bat_i['stat']=j[3]
        break
    if c:
      bat_i['stat']='Not Out'
    bat_i['4s']=i[-2]
    bat_i['6s']=i[-1]
    bat_i['bounds']=i[-3]
    bat_i['runs']=i[3]
    bat_i['ball']=i[5]
    bat_i['sr']=i[4]
    bat_tb[-1].append(bat_i)
  bat_tb[1].sort(key = lambda i: int(i['pos']))
  bat_tb[-1].sort(key = lambda i: int(i['pos']))
  #print(bat_tb)
  return bat_tb     

def db_to_wick(match_id):
  sql2="SELECT * FROM WICKETS WHERE MATCH_ID="+match_id+";"
  iplcursor = myconn.cursor()
  iplcursor.execute(sql2)
  wittable = iplcursor.fetchall()
  sql3="SELECT TEAM_1,TEAM_2 from MATCHH WHERE MATCH_ID="+match_id+";"
  iplcursor.execute(sql3)
  teams = iplcursor.fetchall()
  #print(teams)
  t1=teams[0][0]
  t2=teams[0][1]
  prt=""
  try:
    prt=wittable[0][1][:2:]
  except:
      pass
  d=0
  wick=[]
  if len(wittable) and t1[:2:]==wittable[0][0][:2:] :
    wick.append(t1)
    wick.append([])
    d=1
  else:
    wick.append(t2)
    wick.append([])
    d=0
  #print(prt)
  for i in wittable:
    if i[1][:2:]!=prt:
      wick.append(teams[0][d])
      prt=i[1][:2:]
      wick.append([])
    wi={}
    wi['over']=i[-1]
    a="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[1]+"';"
    iplcursor.execute(a)
    name = iplcursor.fetchall()[0][0]
    a="SELECT RUNS FROM SCORE WHERE OVER_BALL='"+i[-1]+"' AND MATCH_ID='"+match_id+ "'AND TEAM ='"+wick[-2]+"';"
    iplcursor.execute(a)
    score=""
    try:
      score=iplcursor.fetchall()[0][0]
    except:
      pass
    wi['score']=score
    wi['wicks']=i[2]
    wi['name']=name
    wick[-1].append(wi)
  wick[1].sort(key = lambda i: i['wicks'])
  wick[-1].sort(key = lambda i: i['wicks'])
  #print(wick)
  return wick

def db_to_plyr(name,team):
    sql="SELECT * FROM PLAYER WHERE PLAYER_NAME LIKE '%"+name+"%' AND PLAYER_ID LIKE '%"+team+"%';"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql)
    players = iplcursor.fetchall()
    print(players)
    return players
#db_to_plyr("","")

def plr(id):
    sql="SELECT * FROM PLAYER WHERE PLAYER_ID='"+id+"';"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql)
    player = iplcursor.fetchall()[0]
    return player

def db_to_scr(match_id,team1,team2):
    sql="SELECT * FROM SCORE WHERE MATCH_ID='"+match_id+"' AND TEAM='"+team1+"';"
    sql2="SELECT * FROM SCORE WHERE MATCH_ID='"+match_id+"' AND TEAM='"+team2+"';"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql)
    scores1 = iplcursor.fetchall()
    iplcursor.execute(sql2)
    scores2 = iplcursor.fetchall()
    scores1.sort(key = lambda i: float(i[0]))
    scores2.sort(key = lambda i: float(i[0]))
    for i in scores1:
        i=list(i)
        sql4="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[2]+"';"
        iplcursor.execute(sql4)
        i[2]=iplcursor.fetchall()[0][0]
        
        sql41="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[3]+"';"
        iplcursor.execute(sql41)
        i[3]=iplcursor.fetchall()[0][0]

        sql5="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[4]+"';"
        iplcursor.execute(sql5)
        i[4] = iplcursor.fetchall()[0][0]

    for i in scores2:
        i=list(i)
        sql4="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[2]+"';"
        iplcursor.execute(sql4)
        i[2]=iplcursor.fetchall()[0][0]
        
        sql41="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[3]+"';"
        iplcursor.execute(sql41)
        i[3]=iplcursor.fetchall()[0][0]

        sql5="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+i[4]+"';"
        iplcursor.execute(sql5)
        i[4] = iplcursor.fetchall()[0][0]
    scores={}
    scores[team1]=scores1
    scores[team2]=scores2
    #print(scores)
    return scores

def db_to_scr1(match_id,team,over):
    sql="SELECT * FROM SCORE WHERE MATCH_ID='"+match_id+"' AND TEAM='"+team+"' AND OVER_BALL='"+over+"';"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql)
    score=iplcursor.fetchall()[0]
    score=list(score)

    sql4="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+score[2]+"';"
    iplcursor.execute(sql4)
    score[2]=iplcursor.fetchall()[0][0]
        
    sql41="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+score[3]+"';"
    iplcursor.execute(sql41)
    score[3]=iplcursor.fetchall()[0][0]

    sql5="SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID='"+score[4]+"';"
    iplcursor.execute(sql5)
    score[4] = iplcursor.fetchall()[0][0]
    #print(score)
    return score

def getts(id):
    iplcursor = myconn.cursor()
    sql3="SELECT TEAM_1,TEAM_2 from MATCHH WHERE MATCH_ID="+id+";"
    iplcursor.execute(sql3)
    teams = iplcursor.fetchall()
    #print(teams)
    t1=teams[0][0]
    t2=teams[0][1]
    return t1,t2


def db_to_scr2(match_id, team1, team2):
    mycursor=myconn.cursor()
    final_score = {'inning1': {}, 'inning2': {}}
    mycursor.execute("select * from score where match_id = '"+match_id+"' and rrr is NULL;")
    data = mycursor.fetchall()
    lst_ball = max(data , key = lambda i : float(i[0]))[0]
    mycursor.execute("select runs, wicket, team from score where match_id ='"+match_id+"' and over_ball = '"+str(lst_ball)+"' and rrr is NULL;")
    inn1_data = mycursor.fetchall()
    final_score['inning1']['runs'] = inn1_data[0][0]
    final_score['inning1']['wicket'] = inn1_data[0][1]
    final_score['inning1']['team'] = inn1_data[0][2]
    final_score['inning1']['over_ball'] = lst_ball

    mycursor.execute("select * from score where match_id = '" + match_id + "' and team !='"+inn1_data[0][2]+"'")
    data = mycursor.fetchall()
    lst_ball = max(data, key=lambda i: float(i[0]))[0]
    mycursor.execute("select * from score where match_id = '"+match_id+"' and over_ball = '"+lst_ball+"' and team <> '"+inn1_data[0][2]+"';")
    inn2_data = mycursor.fetchall()
    final_score['inning2']['team'] = inn2_data[0][5]
    final_score['inning2']['runs'] = inn2_data[0][6]
    final_score['inning2']['wickets'] = inn2_data[0][7]
    final_score['inning2']['over_ball'] =inn2_data[0][0]

    mycursor.execute("select player_name from player where player_id = '"+inn2_data[0][2]+"';")
    final_score['inning2']['bat1'] =mycursor.fetchall()[0][0]

    mycursor.execute("select player_name from player where player_id = '" + inn2_data[0][3] + "';")
    final_score['inning2']['bat2'] = mycursor.fetchall()[0][0]

    mycursor.execute("select player_name from player where player_id = '" + inn2_data[0][4] + "';")
    final_score['inning2']['bowl'] = mycursor.fetchall()[0][0]

    mycursor.execute("select * from batsman where match_id = '"+match_id+"' and player_id = '"+inn2_data[0][2]+"';")
    bat1 = mycursor.fetchall()
    final_score['inning2']['run1'] = bat1[0][3]
    final_score['inning2']['balls_faced_1'] = bat1[0][5]

    mycursor.execute("select * from batsman where match_id = '" + match_id + "' and player_id = '" + inn2_data[0][3] + "';")
    bat2 = mycursor.fetchall()
    final_score['inning2']['run2'] = bat2[0][3]
    final_score['inning2']['balls_faced_2'] = bat2[0][5]

    mycursor.execute("select * from bowler where match_id = '" + match_id + "' and player_id = '" + inn2_data[0][4] + "';")
    bowl = mycursor.fetchall()
    try:
        final_score['inning2']['bowl_wick'] = bowl[0][2]
        final_score['inning2']['balls_run'] = bowl[0][6]
    except:
        pass
    overs = final_score['inning2']['over_ball']
    over = int(float(overs))
    if float(overs) != int(float(overs)):
        ball = float(overs) - int(float(overs))
        ball /= 0.6
        over += ball
    final_score['inning2']['crr'] = round(final_score['inning2']['runs']/over,2)
    #print(final_score)
    return final_score







app = Flask(__name__)

@app.route('/')

def index ():
    matchid = do_it()
    #print(matchid)
    sc=c.scorecard(matchid)
    pr_in={}
    bowl_tbl=[]
    bat_t=[]
    w_t=[]
    if len(sc['scorecard'])>0:
        pr_in=prv_inn(sc)
        bowl_tbl=db_to_bowl(matchid)
        bat_t=db_to_bat(matchid)
        w_t=db_to_wick(matchid)
    return render_template('index.html',ls =live_score,prin=pr_in,bt=bowl_tbl,batt=bat_t,wt=w_t)
    #return live_score



@app.route('/archive/')
def arhive():
    m_tb=db_to_match()
    return render_template('archive.html',mtb=m_tb)

@app.route('/archive/match')
def matchc():
    id=request.args.get('id',default="",type=str)
    #print(id)
    bat_t=db_to_bat(id)
    bowl_tbl=db_to_bowl(id)
    w_t=db_to_wick(id)
    f_s={}
    try:
        f_s=db_to_scr2(id, bat_t[0], bat_t[2])
    except:
        pass
    return render_template('match.html',batt=bat_t,bt=bowl_tbl,wt=w_t,fs=f_s)

@app.route('/playerstats/',methods=['GET','POST'])
def player():
    teams=['MI','CSK','DC','KXIP','SRH','KKR','RR','RCB']
    plyrs=db_to_plyr("","")
    #print("Hi Ojas")
    #print()
    #print(plyrs)
    x=IPLive()
    o_c=""
    p_c=""
    b_e=""
    s_r=""
    b_sr=""
    b_a=""
    a=""
    try:
        o_c=x.display_orange_cap()
        p_c=x.display_purple_cap()
        b_e=x.best_economy()
        s_r=x.best_strike_rate()
        b_sr=x.bowling_strike_rate()
        b_a=x.bowling_average()
        a=x.batting_average()
    except:
        pass
    
    if request.method == 'POST':
        plyrs=db_to_plyr("","")
        try:
            plname=request.form['plyr']
            plteam=request.form['team']
            plyrs=db_to_plyr(plname,plteam)
        except:
            pass
        return render_template('playerstat.html',pls=plyrs,ts=teams,oc=o_c,pc=p_c,be=b_e,sr=s_r,bsr=b_sr,bav=b_a,av=a)
    else:
        plyrs=db_to_plyr("","")
        return render_template('playerstat.html',pls=plyrs,ts=teams,oc=o_c,pc=p_c,be=b_e,sr=s_r,bsr=b_sr,bav=b_a,av=a)

@app.route('/playerstats/player')
def playerst():
    id=request.args.get('id',default="",type=str)
    pl_r=plr(id)
    teams=['MI','CSK','DC','KXIP','SRH','KKR','RR','RCB']
    return render_template('player.html',player=pl_r,ts=teams)

@app.route('/archive/score',methods=['GET','POST'])
def score_bb():
    id=request.args.get('id',default="",type=str)
    team1,team2=getts(id)
    scrs=db_to_scr(id,team1,team2)
    if request.method == 'POST':
        scrover=request.form['over']
        scrteam=request.form['team']
        scr=db_to_scr1(id,scrteam,scrover)
        return render_template('score.html',scores=scrs,score=scr,match=id)
    else:
        return render_template('score.html',scores=scrs,score=[],match=id)


if __name__ == "__main__":
    app.run(debug=True)