from pycricbuzz import Cricbuzz
from datetime import date
import time
import mysql.connector


mydb= mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="scratch"
)
mycursor=mydb.cursor()


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


def db_to_plyr(name,team):
    sql="SELECT * FROM PLAYER WHERE PLAYER_NAME LIKE '%"+name+"%' AND PLAYER_ID LIKE '"+team+"%';"
    iplcursor = mydb.cursor()
    iplcursor.execute(sql)
    players = iplcursor.fetchall()
    print(players)

c=Cricbuzz()
global_pr={}
live_score={}


class IPLive:
    # match = c.matches()

    def __init__(self):
        self.lst=[]

        for i in c.matches():
            if i['srs'] == "Indian Premier League 2020" and i['start_time'].split()[0] == str(date.today()):
                self.lst.append(i)
                self.mchinfo = c.matchinfo(self.lst[0]['id'])
        if len(self.lst) == 2 and self.mchinfo['mchstate'] != 'mom' and 'won' not in self.mchinfo['status'].split():
                # if c.matchinfo(i['id'])['mchstate'] == 'inprogress' or c.matchinfo(i['id'])['mchstate'] == 'innings break' or c.matchinfo(i['id'])['mchstate'] == 'toss' or c.matchinfo(i['id'])['mchstate'] != 'mom':
            self.match_id = self.lst[0]['id']
            self.team1 = self.lst[0]['team1']['name']
            self.team2 = self.lst[0]['team2']['name']
            self.venue = self.lst[0]['venue_name']
            self.match_date = self.lst[0]['start_time'].split()[0]
            self.result = self.lst[0]['status']
            self.commentary = c.commentary(self.match_id)
            self.score = c.scorecard(self.match_id)
        elif len(self.lst) == 2: #and c.matchinfo(lst[1]['id']) != 'mom':
            self.match_id = self.lst[1]['id']
            self.team1 = self.lst[1]['team1']['name']
            self.team2 = self.lst[1]['team2']['name']
            self.venue = self.lst[1]['venue_name']
            self.match_date = self.lst[1]['start_time'].split()[0]
            self.result = self.lst[1]['status']
            self.commentary = c.commentary(self.match_id)
            self.score = c.scorecard(self.match_id)
        else:
            self.match_id = self.lst[0]['id']
            self.team1 = self.lst[0]['team1']['name']
            self.team2 = self.lst[0]['team2']['name']
            self.venue = self.lst[0]['venue_name']
            self.match_date = self.lst[0]['start_time'].split()[0]
            self.result = self.lst[0]['status']
            self.commentary = c.commentary(self.match_id)
            self.score = c.scorecard(self.match_id)


#stat at the time of fall of wicket
#overall score
#max/min runs, strike rate, wicket, economy, sixes, fours, boundaries, extras
    #def get_batsman_details(self):
     #
      #  if len(scorecard['batting']['batsman']) == 2:
    def insert_matchh_details(self):
        for i in self.lst:
            try:
                strng="insert into matchh values ('"+i['id']+"', '"+teamname(i['team1']['name'])+"', '"+teamname(i['team2']['name'])+"', '"+i['venue_name']+"', '"+i['start_time'].split()[0]+"', '"+i['status']+"');"
                mycursor.execute(strng)
                #print(strng)
                mydb.commit()
            except:
                mycursor.execute("update matchh set result = '"+i['status']+"' where match_id = '"+i['id']+"';")
                #print("update matchh set result = '"+i['status']+"' where match_id = '"+i['id']+"';")
                mydb.commit()


    def insert_batsman_details(self):
        try:
            # live=c.scorecard(self.match_id)
            team=teamname(self.score['scorecard'][0]['batteam'])
            num = 1

            if self.mchinfo['mchstate'] == 'innings break':
                num = 1
            for i in self.score['scorecard'][0]['batcard']:
                # j = int(live['batting']['score'][0]['wickets'])
                #print( "batsman:", i['name'])
                mycursor.execute("select player_id from player where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';")
                p_id = mycursor.fetchall()[0][0]
                den = 1
                if int(i['balls']) != 0:
                    den = int(i['balls'])
                try:
                    mycursor.execute("insert into batsman values ('"+p_id+"', '"+self.match_id+"', "+str(num)+", "+i['runs']+", "+str(int(i['runs'])/den *100)+", "+i['balls']+", "+str(int(i['fours'])+int(i['six']))+", "+i['fours']+","+i['six']+");")
                    #print("insert into batsman values ('"+p_id+"', '"+self.match_id+"', "+str(num)+", "+i['runs']+", "+str((int(i['runs'])/den)*100)+", "+i['balls']+", "+str(int(i['fours'])+int(i['six']))+", "+i['fours']+","+i['six']+");")
                except:
                    num+=1
                    continue
                num+=1
                mydb.commit()
            for i in self.score['scorecard'][0]['batcard']:
                # j = int(live['batting']['score'][0]['wickets'])
                #print(i['name'])
                mycursor.execute("select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                p_id = mycursor.fetchall()[0][0]
                den = 1
                if int(i['balls']) != 0:
                    den = int(i['balls'])
                mycursor.execute("update batsman set runs = "+i['runs']+", batting_strike_rate = "+str(int(i['runs'])/den*100)+", balls_faced = "+i['balls']+", boundaries = "+str(int(i['fours'])+int(i['six']))+", fours = "+i['fours']+", sixes = "+i['six']+" where player_id = '"+p_id+"' and match_id = '"+self.match_id+"';")
                #print("update batsman set runs = "+i['runs']+", batting_strike_rate = "+str((int(i['runs'])/den)*100)+", balls_faced = "+i['balls']+", boundaries = "+str(int(i['fours'])+int(i['six']))+", fours = "+i['fours']+", sixes = "+i['six']+" where player_id = '"+p_id+"' and match_id = '"+self.match_id+"';")
                mydb.commit()
        except:
            pass

    def insert_player_details(self):
        # score=c.scorecard(self.match_id)
        batlst=[]
        bowllst=[]


        for i in self.score['scorecard'][0]['batcard']:
            team=teamname(self.score['scorecard'][0]['batteam'])
            mycursor.execute("select runs from player where player_name like '%" + i['name'] + "%' and player_id like '%"+team+"%';")
            data=mycursor.fetchall()
            print(i['name'],data)
            if data[0][0] == None:
                strng="update player set runs="+i['runs']+" where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';"
                mycursor.execute("update player set balls_faced = "+i['balls']+" where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';")
                playerretriever="select player_id from player where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    batlst.append(l[0])
            else:
                strng = "update player set runs=runs+" + i['runs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%"+team+"%';"
                mycursor.execute("update player set balls_faced = balls_faced + " + i['balls'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    batlst.append(l[0])
            mycursor.execute(strng)


        for i in self.score['scorecard'][0]['bowlcard']:
            team = teamname(self.score['scorecard'][1]['batteam'])
            mycursor.execute("select wicket from player where player_name like '%" + i['name'] + "%'and player_id like '%"+team+"%';")
            data = mycursor.fetchall()
            #print(i['name'],data)
            if data[0][0]==None:
                strng="update player set wicket="+i['wickets']+" where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';"
                mycursor.execute("update player set runs_conceded = "+i['runs']+" where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';")
                mycursor.execute("update player set overs_bowled = " + i['overs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    bowllst.append(l[0])
            else:
                strng = "update player set wicket=wicket+" + i['wickets'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute("update player set runs_conceded = runs_conceded + " + i['runs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                mycursor.execute("select overs_bowled from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                initial_overs_bowled = mycursor.fetchall()[0][0]
                overs_bowled = float(initial_overs_bowled) + float(i['overs'])
                overs_bowled = int(overs_bowled + (overs_bowled - int(overs_bowled)) // 0.6) + (overs_bowled - int(overs_bowled)) % 0.6
                mycursor.execute("update player set overs_bowled = " + str(overs_bowled) + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    bowllst.append(l[0])
            mycursor.execute(strng)


        for i in self.score['scorecard'][1]['batcard']:
            team = teamname(self.score['scorecard'][1]['batteam'])
            mycursor.execute("select runs from player where player_name like '%" + i['name'] + "%' and player_id like '%"+team+"%';")
            data = mycursor.fetchall()
            #print(i['name'], i['runs'])
            if data[0][0]==None:
                strng="update player set runs="+i['runs']+" where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';"
                #print(strng)
                mycursor.execute("update player set balls_faced = " + i['balls'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    batlst.append(l[0])
            else:
                strng = "update player set runs=runs+" + i['runs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%"+team+"%';"
                mycursor.execute("update player set balls_faced = balls_faced + " + i['balls'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    batlst.append(l[0])
            mycursor.execute(strng)


        for i in self.score['scorecard'][1]['bowlcard']:
            team = teamname(self.score['scorecard'][0]['batteam'])
            mycursor.execute("select wicket from player where player_name like '%" + i['name'] + "%' and player_id like '%"+team+"%';")
            data = mycursor.fetchall()
            if data[0][0] == None:
                strng="update player set wicket="+i['wickets']+" where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';"
                mycursor.execute("update player set runs_conceded = " + i['runs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                mycursor.execute("update player set overs_bowled = " + i['overs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    bowllst.append(l[0])
            else:
                strng = "update player set wicket=wicket+" + i['wickets'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute("update player set runs_conceded = runs_conceded + " + i['runs'] + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                mycursor.execute("select overs_bowled from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                initial_overs_bowled = mycursor.fetchall()[0][0]
                overs_bowled = float(initial_overs_bowled) + float(i['overs'])
                overs_bowled = str(int(overs_bowled + (overs_bowled - int(overs_bowled)) // 0.6) + (overs_bowled - int(overs_bowled)) % 0.6)
                mycursor.execute("update player set overs_bowled = " + overs_bowled + " where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                playerretriever = "select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';"
                mycursor.execute(playerretriever)
                for l in mycursor.fetchall():
                    bowllst.append(l[0])
            mycursor.execute(strng)


        batlst=list(set(batlst))
        bowllst=list(set(bowllst))
        playerlist = list(set(list(batlst + bowllst)))
        for k in playerlist:
            mycursor.execute("select matches_played from player where player_id = '"+k+"';")
            value = mycursor.fetchall()[0][0]
            if value == None:
                mycursor.execute("update player set matches_played = 1 where player_id = '"+k+"';")
            else:
                mycursor.execute("update player set matches_played = matches_played + 1 where player_id = '" + k + "';")
        mycursor.execute("update player set batting_strike_rate = runs * 100 / balls_faced;")
        mycursor.execute("update player set economy = runs_conceded / overs_bowled;")
        mycursor.execute("update player set bowling_average = runs_conceded / wicket;")
        mycursor.execute("update player set bowling_strike_rate = (floor(overs_bowled) * 6 + overs_bowled - floor(overs_bowled))/ wicket;")
       #mycursor.execute("update player set batting_average = runs / ")

        mydb.commit()


    def insert_fall_of_wicket(self):
        # score = c.scorecard(self.match_id)
        team = teamname(self.score['scorecard'][0]['batteam'])
        for i in self.score['scorecard'][0]['fall_wickets']:
            mycursor.execute("select player_id from player where player_name like '%"+i['name']+"%' and player_id like '%"+team+"%';")
            batid = mycursor.fetchall()[0][0]
            for j in self.score['scorecard'][0]['batcard']:
                if i['name'] == j['name']:
                    try:
                        strng = "insert into wickets values ('" + self.match_id + "','" + batid + "','"+i['wkt_num']+"','" + j['dismissal'] + "','"+i['overs']+"');"
                        mycursor.execute(strng)
                        #print(strng)
                    except:
                        pass

        try:
            team = teamname(self.score['scorecard'][1]['batteam'])
            for i in self.score['scorecard'][1]['fall_wickets']:
                strng=""
                mycursor.execute("select player_id from player where player_name like '%" + i['name'] + "%' and player_id like '%" + team + "%';")
                batid = mycursor.fetchall()[0][0]
                for j in self.score['scorecard'][1]['batcard']:
                    if i['name'] == j['name']:
                        strng = "insert into wickets values ('" + self.match_id + "','" + batid + "','"+i['wkt_num']+"','" +j['dismissal']+"','" + i['overs'] +"');"
                mycursor.execute(strng)
                #print(strng)
            mydb.commit()
        except:
            pass

    def get_commentary(self):
        # commentary = c.commentary(self.match_id)['commentary'][0]
        team = teamname(self.score['scorecard'][0]['batteam'])
        for i in self.commentary['commentary']:
            if i['over'] != None:
                mycursor.execute("update score set commentary = '"+i['comm']+"' where over_ball = '"+i['over']+"' and match_id = '"+self.match_id+"' and team = '"+team+"';")
                mydb.commit()
                #print("update score set commentary = '"+i['comm']+"' where over_ball = '"+i['over']+"' and match_id = '"+self.match_id+"' and team = '"+team+"';")



    def get_score(self, pr,live_score):
        global global_pr
        sc = self.score
        crr=""
        over_ball = sc['scorecard'][0]['overs']
        over = int(float(over_ball))
        if float(over_ball) != int(float(over_ball)):
            ball = float(over_ball) - int(float(over_ball))
            ball /= 0.6
            over += ball
        if over != 0:
            crr = int(sc['scorecard'][0]['runs']) / over
        runs_req = 'NULL'
        if int(sc['scorecard'][0]['inng_num']) == 2:
            runs_req = int(sc['scorecard'][1]['runs']) + 1 - int(sc['scorecard'][0]['runs'])
        over_left = 20 - over
        rrr = 'NULL'
        bat_1 = -1
        for i in range(len(sc['scorecard'][0]['batcard'])):
            if sc['scorecard'][0]['batcard'][i]['dismissal'] == 'batting' or sc['scorecard'][0]['batcard'][i][
                'dismissal'] == 'not out':
                bat_1 = i
                break
        if over_left != 0 and int(sc['scorecard'][0]['inng_num']) == 2:
            rrr = runs_req / over_left
        runs_req = str(runs_req)
        rrr = str(rrr)
        crr = str(crr)
        # (OVER_BALL, MATCH_ID, BATSMAN_1_ID, BATSMAN_2_ID, BOWLER_ID, TEAM , RUNS, WICKET, RUNS_REQ, RRR, CRR, COMMENTARY)
        bowl_name = ""

        if len(pr.keys()) != 0:
            for i in pr['scorecard'][0]['bowlcard']:
                ind = 0
                for j in range(len(sc['scorecard'][0]['bowlcard'])):
                    if sc['scorecard'][0]['bowlcard'][j]['name'] == i['name']:
                        ind = j
                        break
                if i['overs'] != sc['scorecard'][0]['bowlcard'][ind]['overs']:
                    bowl_name = i['name']
                    break
            if bowl_name == '' and len(live_score):
                bowl_name = live_score['bowl']
        else:
            bowl_name = sc['scorecard'][0]['bowlcard'][-1]['name']
        sql = "INSERT IGNORE INTO score VALUES (" + sc['scorecard'][0][
            'overs'] + "," + self.match_id + "," + "(SELECT PLAYER_ID FROM PLAYER WHERE PLAYER_NAME LIKE '%" + \
              sc['scorecard'][0]['batcard'][bat_1][
                  'name'] + "%')" + "," + "(SELECT PLAYER_ID FROM PLAYER WHERE PLAYER_NAME LIKE '%" + \
              sc['scorecard'][0]['batcard'][-1][
                  'name'] + "%')" + "," + "(SELECT PLAYER_ID FROM PLAYER WHERE PLAYER_NAME LIKE '%" + bowl_name + "%')" + ",'" + teamname(
            sc['scorecard'][0]['batteam']) + "'," + sc['scorecard'][0]['runs'] + "," + sc['scorecard'][0][
                  'wickets'] + "," + runs_req + "," + rrr + "," + crr + ", NULL" + ");"
        mycursor.execute(sql)
        mydb.commit()
        if (over != 20):
            return sc
        else:
            return {}

    def get_short_score(self, pr):
        sc = self.score
        crr=""
        over_ball = sc['scorecard'][0]['overs']
        over = int(float(over_ball))
        if float(over_ball) != int(float(over_ball)):
            ball = float(over_ball) - int(float(over_ball))
            ball /= 0.6
            over += ball
        if over != 0:
            crr = int(sc['scorecard'][0]['runs']) / over
        runs_req = 'NULL'
        if int(sc['scorecard'][0]['inng_num']) == 2:
            runs_req = int(sc['scorecard'][1]['runs']) + 1 - int(sc['scorecard'][0]['runs'])
        over_left = 20 - over
        rrr = 'NULL'

        if over_left != 0 and int(sc['scorecard'][0]['inng_num']) == 2:
            rrr = runs_req / over_left

        if rrr !='NULL':
            rrr=round(rrr,2)

        bowl_name = ""
        bowl_wicks = ""
        bowl_runs = ""

        if len(pr) != 0:
            for i in pr['scorecard'][0]['bowlcard']:
                ind = 0
                for j in range(len(sc['scorecard'][0]['bowlcard'])):
                    if sc['scorecard'][0]['bowlcard'][j]['name'] == i['name']:
                        ind = j
                        break
                if i['overs'] != sc['scorecard'][0]['bowlcard'][ind]['overs']:
                    bowl_name = i['name']
                    bowl_runs = i['runs']
                    bowl_wicks = i['wickets']
                    break
        else:
            bowl_name = sc['scorecard'][0]['bowlcard'][-1]['name']
            bowl_runs = sc['scorecard'][0]['bowlcard'][-1]['runs']
            bowl_wicks = sc['scorecard'][0]['bowlcard'][-1]['wickets']

        # print(live_score)
        if bowl_name == "" and len(live_score.keys()) != 0:
            bowl_name = live_score['bowl']
            bowl_wicks = live_score['bowl_wick']
            bowl_runs = live_score['bowl_run']
            # print("Change ho raha hai")
        bat_1 = -1
        for i in range(len(sc['scorecard'][0]['batcard'])):
            if sc['scorecard'][0]['batcard'][i]['dismissal'] == 'batting' or sc['scorecard'][0]['batcard'][i][
                'dismissal'] == 'not out':
                bat_1 = i
                break
        print(live_score)
        return {'runs': sc['scorecard'][0]['runs'], 'wickets': sc['scorecard'][0]['wickets'], 'crr': round(crr,2), 'rrr': rrr,
                'req_runs': runs_req, 'bat1': sc['scorecard'][0]['batcard'][bat_1]['name'],
                'bat2': sc['scorecard'][0]['batcard'][-1]['name'], 'run1': sc['scorecard'][0]['batcard'][bat_1]['runs'],
                'run2': sc['scorecard'][0]['batcard'][-1]['runs'], 'bowl': bowl_name, 'bowl_wick': bowl_wicks,
                'bowl_run': bowl_runs, 'team': teamname(sc['scorecard'][0]['batteam']),
                'over_ball': sc['scorecard'][0]['overs'], 'ball_faced_1': sc['scorecard'][0]['batcard'][bat_1]['balls'],
                'ball_faced_2': sc['scorecard'][0]['batcard'][-1]['balls']}

    def insert_bowler_details(self):
        sc = self.score

        for i in sc['scorecard'][0]['bowlcard']:
            over_ball = i['overs']
            over = int(float(over_ball))
            if float(over_ball) != int(float(over_ball)):
                ball = float(over_ball) - int(float(over_ball))
                ball /= 0.6
                over += ball
            econ = "NULL"
            if over != 0:
                econ = str(int(i['runs']) / over)
            avg="NULL"
            if int(i['wickets'])!=0:
                avg=str(int(i['runs'])/int(i['wickets']))
            sr="NULL"
            if int(i['wickets'])!=0:
                sr=str(int(i['overs'])*6/int(i['wickets']))
            ins = "INSERT INTO BOWLER VALUES ((SELECT PLAYER_ID FROM PLAYER WHERE PLAYER_NAME LIKE '%" + i[
                'name'] + "%' AND PLAYER_ID LIKE'" + teamname(
                sc['scorecard'][0]['bowlteam']) + "%'),'" + self.match_id + "'," + i[
                      'wickets'] + "," + econ + "," +avg+ ','+sr+"," + i['runs'] + "," + i['overs'] + ");"
            upd = "UPDATE BOWLER SET WICKET=" + i['wickets'] + ",ECONOMY=" + econ + ",RUNS_CONCEDED=" + i[
                'runs'] + ",OVER_BOWLED=" + i[
                      'overs'] + " WHERE PLAYER_ID=(SELECT PLAYER_ID FROM PLAYER WHERE PLAYER_NAME LIKE '%" + i[
                      'name'] + "%' AND PLAYER_ID LIKE'" + teamname(sc['scorecard'][0]['bowlteam']) + "%');"

            try:
                mycursor.execute(ins)
            except mysql.connector.IntegrityError:
                mycursor.execute(upd)
            except :
                mycursor.execute(upd)
            mydb.commit()

    def display_orange_cap(self) :
        mycursor.execute("select player_name from player where runs = (select max(runs) from player);")
        return mycursor.fetchall()[0][0]

    def display_purple_cap(self) :
        mycursor.execute("select player_name from player where wicket = (select max(wicket) from player);")
        return mycursor.fetchall()[0][0]

    def best_economy(self) :
        mycursor.execute("select player_name from player where economy = (select max(economy) from player);")
        return mycursor.fetchall()[0][0]

    def best_strike_rate(self) :
        mycursor.execute("select player_name from player where batting_strike_rate = (select max(batting_strike_rate) from player);")
        return mycursor.fetchall()[0][0]

    def bowling_strike_rate(self) :
        mycursor.execute("select player_name from player where bowling_strike_rate = (select min(bowling_strike_rate) from player);")
        return mycursor.fetchall()[0][0]

    def bowling_average(self) :
        mycursor.execute("select player_name from player where bowling_average = (select min(bowling_average) from player);")
        return mycursor.fetchall()[0][0]

    def batting_average(self) :
        mycursor.execute("select player_name from player where batting_average = (select max(batting_average) from player);")
        return mycursor.fetchall()[0][0]


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
    print(live_score)
    #time.sleep(30)
    '''if c.matchinfo(x.match_id)['mchstate'] != 'mom' and 'won' not in c.matchinfo(x.match_id)['status'].split():
        try:
            do_it()
        except:
            #time.sleep(120)
            do_it()'''

'''while True:
    do_it()
    time.sleep(20)'''
# try:
#     while c.matchinfo(y.match_id)['mchstate'] != 'mom' and 'won' not in c.matchinfo(y.match_id)['status'].split():
#         try:
#             do_it()
#             time.sleep(60)
#         except:
#             time.sleep(120)
# except:
#     time.sleep(120)


'''try:
    y=IPLive()
except:
    time.sleep(120)
    y=IPLive


try:
    y.insert_matchh_details()
    print("Inserting player details")
    y.insert_player_details()
except:
    pass'''
'''while True:
    do_it()
    time.sleep(20)'''