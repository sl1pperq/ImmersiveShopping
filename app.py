import smtplib
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect
import json
import datetime
import random


app = Flask(__name__)
items = []
orders = []

try:
    with open('items.json', 'r') as file:
        items = json.loads(file.read())
    with open('orders.json', 'r') as file:
        orders = json.loads(file.read())
except:
    pass


def save_data():
    with open('items.json', 'w') as file:
        file.write(json.dumps(items, ensure_ascii=False))
    with open('orders.json', 'w') as file:
        file.write(json.dumps(orders, ensure_ascii=False))


@app.route('/')
def hello_world():
    return render_template("main.html")

@app.route('/cat')
def cat():
    return render_template("cat.html", items=items)

@app.route('/item/<id>')
def item(id):
    item = find_item(id)
    return render_template("basket.html", item=item)

@app.route('/my')
def my_orders():
    user_orders = find_user_orders('averin.sergey.dm@mail.ru')
    return render_template('my.html', orders=user_orders)

@app.route('/order/<id>', methods=['POST'])
def order_new(id):
    item = find_item(id)
    data = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    num = f'{datetime.datetime.now().strftime("%d%m")}-{random.randint(100000, 999999)}'
    orders.append({
        'status': 'В обработке',
        'id': num,
        'item': item['title'],
        'price': item['price'],
        'date': data,
        'info': {
            'f_name': request.form.get('f_name'),
            'l_name': request.form.get('l_name'),
            'mail': request.form.get('mail'),
            'class': request.form.get('class'),
            'school': request.form.get('school'),
        }
    })
    save_data()
    return render_template('message.html')

@app.route('/admin/123456')
def admin_console():
    return render_template('admin.html', items=items, orders=orders)

@app.route('/admin/123456/change/<id>', methods=['POST'])
def admin_change(id):
    new_stat = request.form.get('new_stat')
    change_order_stat(id, new_stat)
    order = get_info_order(id)
    if new_stat == 'В сборке':
        send_email_message(
            'averin.seregy.dm@mail.ru',
            f'Ваш заказ №{order["id"]} находится в сборке. Ожидайте уведомления о готовности к выдаче.',
            'Заказ в сборке'
        )
    elif new_stat == 'Ожидает получения':
        send_email_message(
            'averin.seregy.dm@mail.ru',
            f'Ваш заказ №{order["id"]} готов к получению. Вы можете получить его в {order["info"]["school"]}',
            'Заказ в готов к получению'
        )
    elif new_stat == 'Получен':
        send_email_message(
            'averin.seregy.dm@mail.ru',
            f'Ваш заказ №{order["id"]} выдан. По всем вопросам - звоните +79162267351',
            'Заказ выдан'
        )
    return redirect('/admin/123456')

@app.route('/admin/123456/del/item/<id>')
def admin_item_del(id):
    delete_item(id)
    return redirect('/admin/123456')

@app.route('/admin/123456/create')
def create_item_admin():
    return render_template('create.html')

@app.route('/admin/123456/create', methods=['POST'])
def post_create_item_admin():
    title = request.form.get('title')
    image = request.form.get('image')
    text = request.form.get('text')
    price = request.form.get('price')
    id = random.randint(100000, 999999)
    items.append({
        'id': str(id),
        'title': title,
        'image': image,
        'text': text,
        'price': price
    })
    save_data()
    return redirect('/admin/123456')



def get_info_order(id):
    for order in orders:
        if order['id'] == id:
            return order


def delete_item(id):
    for i in range(len(items)):
        if items[i]['id'] == id:
            del items[i]
            save_data()
            break

def change_order_stat(id, stat):
    for order in orders:
        if order['id'] == id:
            order['status'] = stat
            save_data()
            break

def find_user_orders(mail):
    user_orders = []
    for order in orders:
        # if order['info']['mail'] == mail:
        #     user_orders.append(order)
        user_orders.append(order)
    return user_orders

def find_item(id):
    for item in items:
        if item['id'] == id:
            return item

def send_email_message(receiver_mail, text, title):
    port = 465
    password = 's86wCq6pfwVJ9Bc6DKkp'
    sender_mail = 'banjobot@mail.ru'
    smtp_server = 'smtp.mail.ru'
    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_mail, password)
            msg = MIMEText(f'{text}', 'html')
            msg['Subject'] = title
            msg['From'] = sender_mail
            msg['To'] = receiver_mail
            server.sendmail(sender_mail, receiver_mail, msg.as_string())
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True)
