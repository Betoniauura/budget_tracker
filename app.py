from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, instance_relative_config=True)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'budget.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False) 
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)

@app.route('/')
def index():
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    return render_template('index.html', transactions=transactions, balance=balance)

@app.route('/add', methods=['POST'])
def add_transaction():
    type_ = request.form['type']
    category = request.form['category']
    amount = float(request.form['amount'])
    description = request.form.get('description', '')
    transaction = Transaction(type=type_, category=category, amount=amount, description=description)
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/data')
def get_data():
    transactions = Transaction.query.all()
    expenses = {}
    incomes = {}
    for t in transactions:
        if t.type == 'expense':
            expenses[t.category] = expenses.get(t.category, 0) + t.amount
        elif t.type == 'income':
            incomes[t.category] = incomes.get(t.category, 0) + t.amount
    return jsonify({'expenses': expenses, 'incomes': incomes})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
