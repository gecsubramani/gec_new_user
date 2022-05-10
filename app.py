from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime
import db_connect
import io
import os.path
import os
import webbrowser
from os import path
import glob
import time


app = Flask(__name__)

ENV = "dev"

if ENV == "dev":
    app.debug=True
    db = db_connect.con()
    cur = db.cursor()
    

headings=("ID", "SOURCE LINK", "COUNTRY", "CHANGEDOCS")


# storing date
rawdt = datetime.datetime.now()
dt = str(rawdt.strftime("%d")) + "-" + str(rawdt.strftime("%m")) + "-" + str(rawdt.strftime("%Y"))
tt = str(rawdt.strftime("%H:%M %p"))
d_t = dt + ',' + tt


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/open', methods=['POST'])
def open():
    file_to_open = request.form['message_py']
    webbrowser.open_new_tab(f'changedocs\\{file_to_open}.html')
    return jsonify({"success":"success"})



def livelinkempty(username):
    db = db_connect.con()
    cur = db.cursor()
    # checking whether current user has any records lockedin livelinks
    sql = 'select dataid, srclink, country, region, linktype from livelinks where username=%s and userdate=%s'    
    cur.execute(sql, (username, dt))
    result = cur.fetchall()
    try: resultlen = len(result)
    except: resultlen = 0
    # if no records found or else will work
    if resultlen==0:
        # bringing all records from from livelinks chcking whether livelinks has any data
        sql = 'select dataid, srclink, country, region, linktype from livelinks'    
        cur.execute(sql)
        result = cur.fetchall()
        try: resultlen = len(result)
        except: resultlen = 0
        if resultlen == 0:
            return "empty"
        else:
            t_livelinks = resultlen
            # data exists in livelink so match user profile and but collect only unalloted links from the list
            sql='select * from userdetails where name=%s'
            cur.execute(sql, (username,))
            userresult=cur.fetchall()
            try: resultlen=len(result)
            except: resultlen=0
            if resultlen==0:
                return "user not found"
            else:
                # match user profile to the livelink records line by line
                u_region = userresult[0][3]
                u_linktype = userresult[0][5]
                # check for unalloted sites only
                sql='select dataid, srclink, country, region, linktype from livelinks where username is Null'
                cur.execute(sql)
                resultfromlivelinkunalloted=cur.fetchall()
                try: resultlen=len(resultfromlivelinkunalloted)
                except: resultlen=0
                if resultlen == 0:
                    return ("")
                else:
                    emptylist= []
                    rec_count = 0
                    for each in resultfromlivelinkunalloted:
                        if rec_count > 5:
                            break
                        region = each[3]
                        linktype = each[4]
                        if u_region.find(region)>=0 and u_linktype.find(linktype)>=0:
                            # profile match add this link to him
                            dataid = each[0]
                            url = each[1]
                            country = each[2]
                            newrow=()
                            # since this link is added to user it is update in live links date, username
                            sql='update livelinks set username=%s, userdate=%s where dataid=%s'
                            cur.execute(sql, (username, dt, dataid))
                            db.commit()
                            sql = 'select * from remarks where dataid=%s order by dataid DESC limit 2'    
                            cur.execute(sql, (dataid,))
                            try: 
                                result = cur.fetchall()
                                resultlen = len(result)
                            except: resultlen = 0
                            if resultlen == 0:
                                r1 = "No previous records"
                                r2 = "No previous records"
                            else:
                                r1 = result[0]
                                r2 = result[1]
                            newrow = dataid, url, country, r1, r2
                            emptylist.append(newrow)
                            rec_count = rec_count + 1
                            
                            # bringing the changeddoc content for later use also.****THIS can be avoided for slow****
                            sql='select htmldoc from changedocs where dataid=%s order by dataid DESC limit 1'
                            cur.execute(sql, (dataid,))
                            try:
                                changedocresult=cur.fetchall() 
                                changedocresultlen=len(changedocresult)
                            except: changedocresultlen=0
                            if changedocresult==0:
                                pass
                            else:
                                fname = f'changedocs\\{dataid}.html'
                                if path.isfile(fname) == False:
                                    try:
                                        ch=str(changedocresult[0][0])
                                        io.open(fname, 'w', encoding='utf8').write(ch)
                                    except: 
                                        ch="<h1>No Data Available</h1>"
                                        io.open(fname, 'w', encoding='utf8').write(ch)
                return (emptylist, t_livelinks)
    else:
        # current user has already locked data in livelinks
        emptylist = []
        rec_count = 0
        for each in result:
            # profile is already matched and alloted.
            if rec_count > 5:
                break
            dataid = each[0]
            url = each[1]
            country = each[2]
            newrow=()
            sql = 'select * from remarks where dataid=%s order by dataid DESC limit 2'    
            cur.execute(sql, (dataid,))
            try: 
                result = cur.fetchall()
                resultlen = len(result)
            except: resultlen = 0
            if resultlen == 0:
                r1 = "No previous records"
                r2 = "No previous records"
            else:
                r1 = result[0]
                r2 = result[1]
            newrow = dataid, url, country, r1, r2
            emptylist.append(newrow)
            rec_count = rec_count + 1
            # bringing the changeddoc content for later use also.****THIS can be avoided for slow****
            sql='select htmldoc from changedocs where dataid=%s order by dataid DESC limit 1'
            cur.execute(sql, (dataid,))
            try:
                changedocresult=cur.fetchall() 
                changedocresultlen=len(changedocresult)
            except: changedocresultlen=0
            if changedocresult==0:
                pass
            else:
                fname = f'changedocs\\{dataid}.html'
                if path.isfile(fname) == False:
                    try:
                        ch=str(changedocresult[0][0])
                        io.open(fname, 'w', encoding='utf8').write(ch)
                    except: 
                        ch="<h1>No Data Available</h1>"
                        io.open(fname, 'w', encoding='utf8').write(ch)
        sql = 'select dataid, srclink, country, region, linktype from livelinks'    
        cur.execute(sql)
        result = cur.fetchall()
        try: resultlen = len(result)
        except: resultlen = 0
        t_livelinks = resultlen
        return (emptylist, t_livelinks)




@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['upassword']
    
    if username=="" or password=="":
        return render_template('welcome.html', message="Fields cant be empty")

    s = 'select * from userdetails where name=%s and password=%s'
    v = (username, password)
    cur.execute(s, v)
    result = cur.fetchall()
    x = len(result)
    if x == 1:
        # check if he is already logged in 
        name = result[0][0]
        password = result[0][1]
        rights = result[0][2]
        region = result[0][3]
        linktype = result[0][5]
        sql = 'select * from userlogdetails where name=%s and logindate=%s'
        cur.execute(sql, (name, dt))
        result = cur.fetchall()
        try: resultlen = len(result)
        except: resultlen = 0
        lrecid = resultlen
        if lrecid == 0:
            rec_find = 0
        else:
            rec_find = lrecid-1

        # login empty
        if resultlen == 0:
            sql='insert into userlogdetails (name, logindate, logintime) values (%s, %s, %s)'
            val = (name, dt, tt)
            cur.execute(sql, val)
            db.commit()
            # chk for his data in livelink
            chklivelink = livelinkempty(name)
            if chklivelink[0]=="empty":
                # when no data in livelink
                return render_template('user.html', msg1=name, msg2=dt, msg3=tt, region=region, linktype=linktype)
            else:
                # loggin in firsttime but data in livelink so compared accor to the profile and result
                # total sites visited from user remarks
                sql="select dataid from remarks where remarkdate=%s and username=%s"
                cur.execute(sql, (dt, name,))
                visitedresult=cur.fetchall()
                try: visitedresultlen=len(visitedresult)
                except: visitedresultlen=0
                if visitedresultlen==0:
                    return render_template('user.html', msg1=name, msg2=dt, msg3=tt, dataTable=chklivelink[0], headings=headings, msg5="0", total_livelinks=chklivelink[1], region=region, linktype=linktype)
                else:
                    return render_template('user.html', msg1=name, msg2=dt, msg3=tt, dataTable=chklivelink[0], headings=headings, msg5=visitedresultlen, total_livelinks=chklivelink[1], region=region, linktype=linktype)
        else:
            # logged in but not logout in that case
            if result[rec_find][3] is None:
                # store to send
                logindate = result[rec_find][1]
                logintime = result[rec_find][2]
                # chk for his data in livelink
                chklivelink = livelinkempty(name)
                if chklivelink[0]=="empty":
                    # when no data in livelink
                    return render_template('user.html', msg1=name, msg2=logindate, msg3=logintime, headings=headings, dataTable="", msg5="", total_livelinks=chklivelink[1], region=region, linktype=linktype)
                else:
                    # already logged in but data in livelink so compared accor to the profile and result
                    # total sites visited from user remarks
                    sql="select dataid from remarks where remarkdate=%s and username=%s"
                    cur.execute(sql, (dt, name,))
                    visitedresult=cur.fetchall()
                    try: visitedresultlen=len(visitedresult)
                    except: visitedresultlen=0
                    if visitedresultlen==0:
                        return render_template('user.html', msg1=name, msg2=logindate, msg3=logintime, dataTable=chklivelink[0], headings=headings, msg5="0", total_livelinks=chklivelink[1], region=region, linktype=linktype)
                    else:
                        return render_template('user.html', msg1=name, msg2=logindate, msg3=logintime, dataTable=chklivelink[0], headings=headings, msg5=visitedresultlen, total_livelinks=chklivelink[1], region=region, linktype=linktype)
            else:
                sql='insert into userlogdetails (name, logindate, logintime) values (%s, %s, %s)'
                val = (name, dt, tt)
                cur.execute(sql, val)
                db.commit()
                # chk for his data in livelink
                chklivelink = livelinkempty(name)
                if chklivelink[0]=="empty":
                    # when no data in livelink
                    return render_template('user.html', msg1=name, msg2=dt, msg3=tt, total_livelinks=chklivelink[1], region=region, linktype=linktype)
                else:
                    # total sites visited from user remarks
                    sql="select dataid from remarks where remarkdate=%s and username=%s"
                    cur.execute(sql, (dt, name,))
                    visitedresult=cur.fetchall()
                    try: visitedresultlen=len(visitedresult)
                    except: visitedresultlen=0
                    if visitedresultlen==0:
                        return render_template('user.html', msg1=name, msg2=dt, msg3=tt, dataTable=chklivelink[0], headings=headings, msg5="0", total_livelinks=chklivelink[1], region=region, linktype=linktype)
                    else:
                        return render_template('user.html', msg1=name, msg2=dt, msg3=tt, dataTable=chklivelink[0], headings=headings, msg5=visitedresultlen, total_livelinks=chklivelink[1], region=region, linktype=linktype)
    else:
        return render_template('welcome.html', message="bad credentials")





@app.route('/loadremark', methods=['POST'])
def loadremark():
    dataid = request.form['message_py']
    
    # excute the query for remarks
    sql = 'select * from remarks where dataid=%s order by dataid DESC limit 2'    
    cur.execute(sql, (dataid,))
    try: 
        result = cur.fetchall()
        resultlen = len(result)
    except: resultlen = 0
    if resultlen==0:
        # bringing the changeddoc content for later use also.****THIS can be avoided for slow****
        sql='select htmldoc from changedocs where dataid=%s'
        cur.execute(sql, (dataid,))
        try:
            changedocresult=cur.fetchall() 
            changedocresultlen=len(changedocresult)
        except: changedocresultlen=0
        if changedocresult==0:
            pass
        else:
            fname = f'changedocs\\{dataid}.html'
            if path.isfile(fname) == False:
                try:
                    ch=str(changedocresult[changedocresultlen-1][0])
                    io.open(fname, 'w', encoding='utf8').write(ch)
                except: 
                    ch="<h1>No Data Available</h1>"
                    io.open(fname, 'w', encoding='utf8').write(ch)

        last1rec="No previous record"
        last2rec="No previous record"
        
        return jsonify({'r1':last1rec, 'r2':last2rec})        
    else:
        # record available so pull the last 2 records and save to send
        try:
            did = str(result[1][0])
            ddt = str(result[1][2])
            dtt = str(result[1][3])
            dre = str(result[1][1])
            dus = str(result[1][4])
            mytuple = (did, ddt, dtt, dre, dus)
            last1rec = "\n".join(mytuple)
        except:
            last1rec = "No previous record"
        try:
            did = str(result[0][0])
            ddt = str(result[0][2])
            dtt = str(result[0][3])
            dre = str(result[0][1])
            dus = str(result[0][4])
            mytuple = (did, ddt, dtt, dre, dus)
            last2rec = "\n".join(mytuple)
        except:
            last2rec = "No previous record"
        
        # bringing the changeddoc content for later use also.****THIS can be avoided for slow****
        sql='select htmldoc from changedocs where dataid=%s order by dataid DESC limit 1'
        cur.execute(sql, (dataid,))
        changedocresult=cur.fetchall()
        try: changedocresultlen=len(changedocresult)
        except: changedocresultlen=0
        if changedocresult==0:
            pass
        else:
            fname = f'changedocs\\{dataid}.html'
            if path.isfile(fname) == False:
                try:
                    ch=str(changedocresult[changedocresultlen-1][0])
                    io.open(fname, 'w', encoding='utf8').write(ch)
                except: 
                    ch="<h1>No Data Available</h1>"
                io.open(fname, 'w', encoding='utf8').write(ch)
        
        
        return jsonify({'r1':last1rec, 'r2':last2rec})


@app.route('/submitremark', methods=['POST'])
def submitremark():
    dataid = request.form['dataid']
    idremark = request.form['idremark']
    user = request.form['username']
    position = request.form['position']
    idremark = position + ' : ' + idremark

    sql = 'insert into remarks (dataid, remark, remarkdate, remarktime, username) values (%s, %s, %s, %s, %s)'    
    cur.execute(sql, (dataid, idremark, dt, tt, user))
    db.commit()
    sql="select dataid from remarks where remarkdate=%s and username=%s"
    cur.execute(sql, (dt, user))
    visitedresult=cur.fetchall()
    try: visitedresultlen=len(visitedresult)
    except: visitedresultlen=0
    sql = 'delete from livelinks where dataid=%s'    
    cur.execute(sql, (dataid,))
    db.commit()
    sql = 'select * from livelinks' 
    try:
        cur.execute(sql)
        r = cur.fetchall()
        t_livelinks = len(r)
    except:
        t_livelinks = 0  
    
    removechangedoc = 'changedocs\\' + dataid + '.html'
    try: os.remove(removechangedoc)  
    except: pass
    return jsonify({'sited_visited': visitedresultlen, 't_livelinks' : t_livelinks})


@app.route('/sameremark', methods=['POST'])
def sameremark():
    dataid = request.form['dataid']
    idremark = request.form['idremark']
    user = request.form['username']
    idk = str(idremark).split(',')
    idremark = idk[1]
    idremark = idremark.replace("'", "")
    idremark = idremark.strip()
    sql = 'insert into remarks (dataid, remark, remarkdate, remarktime, username) values (%s, %s, %s, %s, %s)'    
    cur.execute(sql, (dataid, idremark, dt, tt, user))
    db.commit()
    sql="select dataid from remarks where remarkdate=%s and username=%s"
    cur.execute(sql, (dt, user,))
    try:
        visitedresult=cur.fetchall() 
        visitedresultlen=len(visitedresult)
    except: visitedresultlen=0
    sql = 'delete from livelinks where dataid=%s'    
    cur.execute(sql, (dataid,))
    db.commit()
    sql = 'select * from livelinks' 
    try:
        cur.execute(sql)
        r = cur.fetchall()
        t_livelinks = len(r)
    except:
        t_livelinks = 0
    removechangedoc = 'changedocs\\' + dataid + '.html'
    try: os.remove(removechangedoc)  
    except: pass
    return jsonify({'sited_visited':visitedresultlen, 't_livelinks':t_livelinks})


@app.route('/userlogout', methods=['POST'])
def userlogout():
    name = request.form['username']

    sql = 'select * from userlogdetails where name=%s and logindate=%s order by logindate limit 1'
    cur.execute(sql, (name, dt))
    try:
        result = cur.fetchall() 
        resultlen = len(result)
    except: resultlen = 0    
    lrecid = resultlen

    if lrecid == 0:
        rec_find = 0
    else:
        rec_find = lrecid-1
    if resultlen>=1 and result[rec_find][3] is None:
        sql="""
            UPDATE userlogdetails
            SET logoutdate =%s , logouttime=%s 
            WHERE name = %s and logindate=%s and logintime=%s;
        """
        val = (dt, tt, name, result[rec_find][1], result[rec_find][2])
        cur.execute(sql, val)
        db.commit()
    
    time.sleep(2)
    return render_template('bye.html')



if __name__ == "__main__":
    app.run()