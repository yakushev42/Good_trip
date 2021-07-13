from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm,RegistrationForm,SearchForm,AddRouteForm,AddCountryForm,AddCityForm,AddGroupForm,VoucherForm,StayForm,ExcursionForm,AddHotelForm,AddRoomForm,Pay,SortGroup
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import connectDB as cn
from app.models import User
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():

    form=SearchForm()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM groups inner join route on groups.nameroute=route.name;"
    curs.execute(sql)
    result = curs.fetchall()
    if "create_voucher" in request.form:
        return redirect(url_for('create_voucher',groupid=request.form['groupid']))
    if "submit" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "select groupid,datestart,size,groups.nameroute,cost,maxsize,minsize,belaysize,route.duration,season, count(distinct staynum) as stay\
        from groups left outer join route on groups.nameroute=route.name LEFT OUTER JOIN stay on route.name=stay.nameroute  \
        where route.cost <=%s  and route.cost>=%s  and\
        groups.datestart>=%s and groups.datestart+route.duration<=%s\
        and route.duration<=%s and route.duration>%s and route.maxsize-groups.size>=%s\
        and route.name in(          \
        select route.name from route left outer join stay on route.name=stay.nameroute group by route.name\
        HAVING count(distinct stay.staynum)>=%s and count(distinct stay.staynum)<=%s )\
        and route.name in(\
        select route.name from route left outer join stay on route.name=stay.nameroute \
        left outer join city on city.name=stay.city left outer join hotel on hotel.city=city.name where hotel.type>=%s and hotel.type<=%s)"
        if(form.Country.data):
            for country in form.Country.data:
                sql=sql+"and route.name in(\
                select route.name from route left outer join stay on route.name=stay.nameroute \
                left outer join city on city.name=stay.city where city.country='"+country+"')"
        if(form.City.data):
            for City in form.City.data:
                sql=sql+"and route.name in(\
                select route.name from route left outer join stay on route.name=stay.nameroute\
                where stay.city='"+City+"')"
        sql=sql+"group by groupid,name "
        sql=sql+"ORDER BY "+form.Sortgroup.data+" "+form.SortType.data
        curs.execute(sql,(form.MaxCost.data,form.MinCost.data,request.form['DateStart'],request.form['DateEnd'],\
        form.LeghtMax.data,form.LeghtMin.data,form.Pers.data,form.Stay0.data,form.Stay1.data,form.Hotel0.data,form.Hotel1.data))
        result = curs.fetchall()
    return render_template('index.html', title='Home',group=result,form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # во избежание повторной авторизации
    form = LoginForm()
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE nickname = %s;"
        curs.execute(sql, (form.username.data,))
        result = curs.fetchone()
        conn.close()
        if result is None:
            user = None
        else:
            user = User(result['userid'], result['nickname'], result['pass_hash'], result['role'])
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(
                next_page).netloc != '':  # перенаправление на след страницу, если не был авторизован
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.worker.data: role="worker"
        else: role="user"
        user = User(nickname=form.nickname.data,role=role)
        user.set_password(form.password.data)
        conn = cn.get_connection()
        curs = conn.cursor()
        
        sql = "INSERT INTO users (nickname, pass_hash,role) VALUES (%s, %s, %s);"
        try:
            curs.execute(sql, (user.nickname, user.pass_hash, user.role,))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
             flash('Вы зарегистрировались')
             conn.commit()
             conn.close()
             return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)    
    
@app.route('/edit', methods=['GET', 'POST'])
def edit():   
   return render_template('Edit.html', title='Редактирование')
@app.route('/groups', methods=['GET', 'POST'])
def groups(): 
    form2=SortGroup()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM groups"
    if form2.validate_on_submit():
        sql=sql+" ORDER BY "+form2.Sortgroup.data+" "+form2.SortType.data
    curs.execute(sql)
    result = curs.fetchall()
    sql = "SELECT * FROM voucher;"
    curs.execute(sql)
    result2 = curs.fetchall()
    form=AddGroupForm()
    
    if "add_group" in request.form:
        return render_template('edit_group.html', title='Редактирование групп',form=form,group=result,voucher=result2,form2=form2)
    if "delete_group" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "DELETE FROM groups WHERE groupid=%s;"
        try:
            curs.execute(sql,(request.form['groupid'],))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            conn.commit()
            flash('Группа удалена')
            redirect(url_for('groups'))
        conn.close()
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO groups (datestart,size,nameroute)  VALUES (%s,%s,%s);"
        curs.execute(sql,(request.form['DateStart'],0,form.NameRoute.data))
        conn.commit()
        conn.close()
        flash('Группа добавлена')
        return redirect(url_for('groups'))
    return render_template('edit_group.html', title=' редактирование групп',group=result,voucher=result2,form2=form2)
@app.route('/routes', methods=['GET', 'POST'])
def routes(): 
   conn = cn.get_connection()
   curs = conn.cursor()
   sql = "select name,cost,maxsize,minsize,belaysize,route.duration,season,count(distinct staynum) as stay\
          from route LEFT OUTER JOIN stay on route.name=stay.nameroute \
          group by name ;"
   curs.execute(sql)
   result = curs.fetchall()
   form=AddRouteForm()
   form2=SearchForm()
   if "add_route" in request.form:
        return render_template('edit_route.html', title='Редактирование маршрутов',route=result,form=form,form2=form2)
   if "delete_route" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "DELETE FROM route WHERE name=%s;"
        try:
            curs.execute(sql,(request.form['name'],))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            conn.commit()
            flash('Маршрут удален')
            redirect(url_for('routes'))
        conn.close()
   if form.validate_on_submit() and request.form['form']=='route':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO route (name, cost, maxsize,minsize,belaysize,duration,season) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        try:
            curs.execute(sql, (form.Name.data, form.Cost.data, form.MaxSize.data, form.MinSize.data, form.BelaySize.data, form.Duration.data, form.Season.data))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            conn.commit()
            conn.close()
            flash('Маршрут добавлен')
            return redirect(url_for('routes'))
   if "submit" in request.form and request.form['form']=='search':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "select name,cost,maxsize,minsize,belaysize,route.duration,season,count(distinct staynum) as stay \
               from route LEFT OUTER JOIN stay on route.name=stay.nameroute \
        where cost <=%s and cost>=%s\
        and route.duration<=%s and route.duration>%s \
        and route.name in(          \
        select route.name from route left outer join stay on route.name=stay.nameroute group by route.name\
        HAVING count(distinct stay.staynum)>=%s and count(distinct stay.staynum)<=%s )\
        and route.name in(\
        select route.name from route left outer join stay on route.name=stay.nameroute \
        left outer join city on city.name=stay.city left outer join hotel on hotel.city=city.name where hotel.type>=%s and hotel.type<=%s)"
        if(form2.Country.data):
            for country in form2.Country.data:
                sql=sql+"and route.name in(\
                select route.name from route left outer join stay on route.name=stay.nameroute \
                left outer join city on city.name=stay.city where city.country='"+country+"')"
        if(form2.City.data):
            for City in form2.City.data:
                sql=sql+"and route.name in(\
                select route.name from route left outer join stay on route.name=stay.nameroute\
                where stay.city='"+City+"')"
        sql=sql+" group by name "
        sql=sql+"ORDER BY "+form2.Sortroute.data+" "+form2.SortType.data
        curs.execute(sql,(form2.MaxCost.data,form2.MinCost.data,\
        form2.LeghtMax.data,form2.LeghtMin.data,form2.Stay0.data,form2.Stay1.data,form2.Hotel0.data,form2.Hotel1.data))
        result = curs.fetchall()
   return render_template('edit_route.html', title='редактирование маршрутов',route=result,form2=form2)
@app.route('/maps', methods=['GET', 'POST'])
def maps():
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM country;"
    curs.execute(sql)
    result = curs.fetchall()
    sql = "select city.name,city.country,count(distinct hotel.name) as hotel \
    from city left outer join hotel on city.name=hotel.city group by city.name;"
    curs.execute(sql)
    result2 = curs.fetchall()
    conn.close()
    form=AddCountryForm()
    form2=AddCityForm()
    if "add_country" in request.form:
        return render_template('edit_map.html', title='Редактирование карт',form=form,country=result,city=result2)
        
    if "add_city" in request.form:
        sel=request.form
        return render_template('edit_map.html', title='Редактирование карт',form2=form2,country=result,city=result2,sel=sel['name'])
    if form.validate_on_submit() and request.form['form']=='country':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO country (name)  VALUES (%s);"
        try:
            curs.execute(sql,(form.Name.data,))
        except conn.Error as e:
             flash(e.diag.message_primary)
        else:
            conn.commit()
            conn.close()
            flash('Страна добавлена')
            return redirect(url_for('maps'))
    if form2.validate_on_submit() and request.form['form']=='city':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO city (name,country)  VALUES (%s,%s);"
        try:
            curs.execute(sql,(form.Name.data,request.form['name'],))
        except conn.Error as e:
             flash(e.diag.message_primary)
        else:
            conn.commit()
            conn.close()
            flash('Город добавлен')
            return redirect(url_for('maps'))
    if "delete_country" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "DELETE FROM country WHERE name=%s;"
        try:
            curs.execute(sql,(request.form['name'],))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            conn.commit()
            flash('Cтрана удалена')
        conn.close()
        return redirect(url_for('maps'))
    if "delete_city" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "DELETE FROM city WHERE name=%s;"
        try:
            curs.execute(sql,(request.form['name'],))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            conn.commit()
            flash('Город удалён')
        conn.close()
        return redirect(url_for('maps'))
    return render_template('edit_map.html', title='редактирование карт',country=result,city=result2)
@app.route('/basket', methods=['GET', 'POST'])
def basket():
    print(request.form)
    form=Pay()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT contract.contractid,contract.paytype,sum(route.cost) \
    FROM voucher inner join contract using (contractid) inner join groups using (groupid)\
    inner join route on route.name=groups.nameroute   where userid=%s group by contract.contractid;"
    curs.execute(sql, (current_user.userid,))
    result = curs.fetchall()
    sql = "SELECT * FROM voucher inner join contract using (contractid) inner join groups using (groupid) WHERE userid=%s;"
    curs.execute(sql, (current_user.userid,))
    result2 = curs.fetchall()
    conn.close()
    if "delete_voucher" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "DELETE FROM voucher WHERE contractid=%s and passport=%s;"
        curs.execute(sql,(request.form['contractid'],request.form['passport']))
        conn.commit()
        flash('Путёвка удалена')
        conn.close()
        return redirect(url_for('basket'))
    if "submit" in request.form:
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "UPDATE contract SET paytype=%s WHERE contractid=%s"
        curs.execute(sql, (form.PayType.data,request.form['contractid']))
        conn.commit()
        conn.close()
        flash('Договор успешно оплачен') 
        return redirect(url_for('basket'))
    return render_template('basket.html', title='корзина',contract=result,voucher=result2,form=form)
    
@app.route('/voucher/<groupid>', methods=['GET', 'POST'])
@login_required
def create_voucher(groupid):
    form=VoucherForm()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM groups inner join route on route.name=groups.nameroute WHERE groupid = %s;"
    curs.execute(sql, (groupid,))
    result = curs.fetchone()
    conn.close()
    if result['size']==result['maxsize']:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        result2=''
        while not result2:
            conn = cn.get_connection()
            curs = conn.cursor()
            sql = "SELECT * FROM contract WHERE userid = %s and paytype=%s;"
            curs.execute(sql, (current_user.userid,'No'))
            result2 = curs.fetchone()
            conn.close()
            if not result2:
                conn = cn.get_connection()
                curs = conn.cursor()
                sql ="INSERT INTO contract (paytype,userid) VALUES (%s,%s)"
                curs.execute(sql,('No',current_user.userid))
                conn.commit()
                conn.close()
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO voucher (passport,groupid,fio,address,phone,datebirth,contractid)  VALUES (%s,%s,%s,%s,%s,%s,%s);"                     
        curs.execute(sql, (form.Passport.data,groupid,form.Fio.data,form.Address.data,form.Phone.data,request.form['DateBirth'],result2['contractid']))
        conn.commit()
        conn.close()
        flash('Путёвка оформленна')
        return redirect(url_for('create_voucher',groupid=groupid))
    return render_template('create_voucher.html', title='Оформление путёвки',group=result,form=form)
@app.route('/stay/<nameroute>', methods=['GET', 'POST'])
def stay(nameroute):
    form=StayForm()
    form2=ExcursionForm()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM stay WHERE nameroute = %s;"
    curs.execute(sql, (nameroute,))
    result = curs.fetchall()
    sql = "SELECT name,duration,staynum from excursion inner join stay_excursion on excursion.name=stay_excursion.excursionname where nameroute=%s;"
    curs.execute(sql, (nameroute,))
    result3 = curs.fetchall()
    conn.close()
    if "add_stay" in request.form:
        return render_template('stay.html', title='Остановки',stay=result,excursion=result3,form=form,namerout=nameroute)
    if form.validate_on_submit() and request.form['form']=='stay':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT count(*)+1 as cnt FROM stay WHERE nameroute = %s;"
        curs.execute(sql, (nameroute,))
        result2 = curs.fetchone()
        sql = "INSERT INTO stay (staynum,nameroute,duration,city) VALUES (%s, %s, %s, %s);"
        curs.execute(sql, (result2['cnt'],nameroute,form.Duration.data,form.City.data))
        conn.commit()
        conn.close()
        flash('Остановка добавлена')
        return redirect(url_for('stay',nameroute=nameroute))
    if "add_excursion" in request.form:
        return render_template('stay.html', title='Остановки',stay=result,excursion=result3,form2=form2,namerout=nameroute,sel=int(request.form['staynum']))
    if form2.validate_on_submit() and request.form['form']=='excursion':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO excursion (name,duration) VALUES (%s,%s)"
        try:
            curs.execute(sql,(form2.Name.data,form2.Duration.data))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            sql = "INSERT INTO stay_excursion (staynum,nameroute,excursionname) VALUES (%s,%s,%s)"
            curs.execute(sql,(request.form['staynum'],nameroute,form2.Name.data))
            conn.commit()
            conn.close()
            flash('экскурсия добавлена')
            return redirect(url_for('stay',nameroute=nameroute))
    return render_template('stay.html', title='Остановки',stay=result,excursion=result3,namerout=nameroute)
@app.route('/map/<city>/hotel', methods=['GET', 'POST'])
def hotel(city):
    form=AddHotelForm()
    form2=AddRoomForm()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM hotel WHERE city = %s;"
    curs.execute(sql, (city,))
    result = curs.fetchall()
    sql = "select roomtype.type,namehotel from hotel inner join roomtype on hotel.name=roomtype.namehotel where city=%s;"
    curs.execute(sql, (city,))
    result2 = curs.fetchall()
    conn.close()
    if "add_hotel" in request.form:
       return render_template('hotel.html', title='Отели',hotel=result,room=result2,city=city,form=form) 
    if "add_room" in request.form:
       return render_template('hotel.html', title='Отели',hotel=result,room=result2,city=city,form2=form2)
    if form.validate_on_submit() and request.form['form']=='hotel':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO hotel (name,type,city) VALUES(%s,%s,%s)"
        try:
            curs.execute(sql, (form.Name.data,form.Type.data,city))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:
            conn.commit()
            conn.close()
            flash('Отель добавлен')
            return redirect(url_for('hotel',city=city))
    if form2.validate_on_submit() and request.form['form']=='room':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO roomtype (type,namehotel) VALUES(%s,%s)"
        try:
            curs.execute(sql, (form.Type.data,request.form['hotel']))
        except conn.Error as e:
            flash(e.diag.message_primary)
        else:  
            conn.commit()
            conn.close()
            flash('Тип комнаты добавлен') 
    return render_template('hotel.html', title='Отели',hotel=result,room=result2,city=city)