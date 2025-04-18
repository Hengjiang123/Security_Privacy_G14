# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Transaction
from passlib.hash import pbkdf2_sha256
from config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY
)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = SECRET_KEY

    db.init_app(app)

    return app

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account_no = request.form.get('account_no')
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(account_no=account_no).first()
        if existing_user:
            flash("This account number is already registered.")
            return redirect(url_for('register'))

        password_hash = pbkdf2_sha256.hash(password)

        new_user = User(
            account_no=account_no,
            username=username,
            password_hash=password_hash
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # login use username and password
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and pbkdf2_sha256.verify(password, user.password_hash):
            session['user_id'] = user.id
            flash("Logged in successfully!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    tx_list = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', user=user, transactions=tx_list)


# Add this to app.py
@app.route('/admin')
def admin_panel():
    # VULNERABLE: Missing authentication check
    # Should check if user is logged in AND is an admin

    # Get all users in the system
    all_users = User.query.all()
    return render_template('admin_panel.html', users=all_users)


# Add these routes to app.py

# Add these routes to app.py

@app.route('/admin/dashboard')
def admin_dashboard():
    # VULNERABLE: No proper authorization check
    # Just checks if a user is logged in, not if they should have admin access
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    # Get system statistics
    user_count = User.query.count()
    transaction_count = Transaction.query.count()

    # Calculate some financial stats
    total_deposits = db.session.query(db.func.sum(Transaction.deposit_amt)).filter(
        Transaction.deposit_amt != None).scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(Transaction.withdrawal_amt)).filter(
        Transaction.withdrawal_amt != None).scalar() or 0

    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           transaction_count=transaction_count,
                           total_deposits=total_deposits,
                           total_withdrawals=total_withdrawals)



@app.route('/account/<int:account_id>')
def account_details(account_id):
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    # VULNERABLE: No authorization check to verify the logged-in user
    # has access to the requested account
    account = User.query.get(account_id)

    if not account:
        flash("Account not found.")
        return redirect(url_for('dashboard'))

    transactions = Transaction.query.filter_by(user_id=account_id).order_by(Transaction.date.desc()).limit(10).all()

    return render_template('account_details.html', account=account, transactions=transactions)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False)
