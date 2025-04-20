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

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if this is part of the attack demo
    attack_redirect = request.args.get('attack_redirect') == 'true'

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and pbkdf2_sha256.verify(password, user.password_hash):
            # Log the user in
            session['user_id'] = user.id

            # If this is part of the attack demo, redirect to the transfer page
            if attack_redirect:
                flash("Logged in successfully! Redirecting to security verification...")
                # Use a JavaScript redirect to make it more visible
                return """
                <script>
                    alert("ATTACK DEMO: After login, redirecting to malicious transfer page");
                    window.location.href = "/transfer?to_account=8675309&amount=999.99&description=Security%20Verification&auto_confirm=true";
                </script>
                """
            else:
                flash("Logged in successfully!")
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            # Pass along the attack parameter if it was present
            if attack_redirect:
                return redirect(url_for('login', attack_redirect='true'))
            else:
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


@app.route('/admin')
def admin_panel():
    # VULNERABLE: Missing authentication check
    # Should check if user is logged in AND is an admin

    # Get all users in the system
    all_users = User.query.all()
    return render_template('admin_panel.html', users=all_users)


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


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # Pre-fill form if parameters are in the URL (part of the attack)
    to_account = request.args.get('to_account', '')
    amount = request.args.get('amount', '')
    description = request.args.get('description', '')

    if request.method == 'POST':
        to_account = request.form.get('to_account')
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', '')

        if not to_account or not amount or amount <= 0:
            flash("Please provide valid transfer details.")
            return render_template('transfer.html', user=user,
                                   to_account=to_account,
                                   amount=amount,
                                   description=description)

        # Create a new transaction record for the transfer
        from datetime import datetime
        try:
            new_transaction = Transaction(
                user_id=user.id,
                account_no=user.account_no,
                date=datetime.utcnow(),
                transaction_details=f"Transfer to {to_account}: {description}",
                value_date=datetime.utcnow(),
                withdrawal_amt=amount,
                deposit_amt=None,
                balance_amt=0  # We're not calculating the balance here for simplicity
            )
            db.session.add(new_transaction)
            db.session.commit()

            flash(f"ATTACK SUCCESSFUL: ${amount:.2f} transferred to account {to_account}")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Error processing transfer: {str(e)}")
            return render_template('transfer.html', user=user,
                                   to_account=to_account,
                                   amount=amount,
                                   description=description)

    return render_template('transfer.html', user=user,
                           to_account=to_account,
                           amount=amount,
                           description=description)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)
