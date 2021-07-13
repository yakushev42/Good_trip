from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DateField,IntegerField,SelectMultipleField,SelectField
from wtforms.validators import DataRequired,EqualTo
from datetime import date
import connectDB as cn

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
class RegistrationForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    worker = BooleanField('I am worker')
    submit = SubmitField('Register')
class SearchForm(FlaskForm):
    LeghtMin=IntegerField('продолжительность от',default=1)
    LeghtMax=IntegerField('продолжительность до',default=365)
    MinCost=IntegerField('минимальная стоимость',default=1)
    MaxCost=IntegerField('максимальная стоимость',default=99999)
    Pers=IntegerField('количество персон',default=1)
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "select name,name from country;"
    curs.execute(sql)
    result = curs.fetchall()
    sql = "select name,name from city;"
    curs.execute(sql)
    result2 = curs.fetchall()
    Country=SelectMultipleField('Страны',choices=result)
    City=SelectMultipleField('Города',choices=result2)
    Stay0=IntegerField('от',default=1)
    Stay1=IntegerField('до',default=99)
    Hotel0=IntegerField('от',default=1)
    Hotel1=IntegerField('до',default=5)
    Sortroute=SelectField('Сортировать по ',choices=[('name','названию'),('cost','стоимости'),('route.duration','длительности'),('stay','количеству остановок')])
    Sortgroup=SelectField('Сортировать по ',choices=[('name','названию'),('cost','стоимости'),('route.duration','длительности'),('stay','количеству остановок'),('datestart','дате начала'),('size','заполненности')])
    SortType=SelectField(choices=[('ASC','возрастанию'),('DESC','убыванию')])
    submit = SubmitField('искать')
class AddRouteForm(FlaskForm):
    Name=StringField('Название', validators=[DataRequired()])
    Cost=IntegerField('стоимость')
    MaxSize=IntegerField('максимальньное колличество человек', validators=[DataRequired()])
    MinSize=IntegerField('минимальное колличество человек', validators=[DataRequired()])
    BelaySize=IntegerField('размер страховки', validators=[DataRequired()])
    Duration=IntegerField('длительность', validators=[DataRequired()])
    Season=StringField('время года', validators=[DataRequired()])
    submit = SubmitField('добавить')
class AddCountryForm(FlaskForm):
    Name=StringField('Название', validators=[DataRequired()])
    submit = SubmitField('добавить')
class AddCityForm(FlaskForm):
     Name=StringField('Название', validators=[DataRequired()])
     submit = SubmitField('добавить')
class AddHotelForm(FlaskForm):
     Name=StringField('Название', validators=[DataRequired()])
     Type=SelectField('Тип',choices=[('3','3'),('4','4'),('5','5')])
     submit = SubmitField('добавить')
class AddRoomForm(FlaskForm):
     Type=StringField('Тип', validators=[DataRequired()])
     submit = SubmitField('добавить')
class AddGroupForm(FlaskForm):
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "select name,name from route;"
    curs.execute(sql)
    result = curs.fetchall()
    
    NameRoute=SelectField('Маршрут',choices= result)
    submit = SubmitField('добавить')
class VoucherForm(FlaskForm):
    Passport=StringField('Серия номер паспорта', validators=[DataRequired()])
    Fio=StringField('Фамилия Имя Отчество', validators=[DataRequired()]) 
    Address=StringField('Домашний адрес', validators=[DataRequired()])
    Phone=StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('оформить')
class StayForm(FlaskForm):
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "select name,name from city;"
    curs.execute(sql)
    result = curs.fetchall()
    Duration=IntegerField('длительность', validators=[DataRequired()])
    City=SelectField('город',choices= result)
    submit = SubmitField('добавить')
class ExcursionForm(FlaskForm):
    Name=StringField('Название', validators=[DataRequired()])
    Duration=IntegerField('длительность', validators=[DataRequired()])
    submit = SubmitField('добавить')
class Pay(FlaskForm):
    PayType=SelectField(choices=[('наличные','наличные'),('карта','карта'),('биткоины','биткоины')])
    submit = SubmitField('оплатить')
class SortGroup(FlaskForm):  
    Sortgroup=SelectField(choices=[('nameroute','Названию'),('groupid','Номеру'),('datestart','дате')])
    SortType=SelectField(choices=[('ASC','возрастанию'),('DESC','убыванию')])
    submit = SubmitField('OK')
    