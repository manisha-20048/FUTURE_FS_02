from flask import Flask,request,jsonify,render_template,redirect,url_for,flash,session
import mysql.connector
import os
app=Flask(__name__)
app.secret_key='mysecretekey123'
app.secret_key = os.environ.get("VIRAL_GENERATOR_SECRET")

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
        port=int(os.environ.get("MYSQLPORT", 3306))
    )

@app.route('/')
def welcome():
    return render_template('welcome.html')
@app.route('/adminpage')
def admin_page():
    return render_template('admin_page.html')
@app.route('/userpage')
def user_page():
    return render_template('user_page.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['username']
            email=request.form['email']
            password=request.form['password']
            conn = get_db_connection()
            cursor = conn.cursor()
            sql="insert into admins (name,email,password) values (%s,%s,%s)"
            values=(name,email,password)
            cursor.execute(sql,values)
            conn.commit()
            cursor.close()
            conn.close()

            flash('registered successfully')
            return redirect(url_for('admin_login'))
        except Exception as e:
            flash('registered already')
    return render_template('admin_register.html')
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM admins WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))
        admin = cursor.fetchone()

        if admin:
            session['user_id'] = admin[0]
            session['username'] = admin[1]
            session['admin'] = email
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid email or password")

    return render_template('admin_login.html')
@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method=='POST':
        try:
            name=request.form['username']
            email=request.form['email']
            password=request.form['password']
            conn = get_db_connection()
            cursor = conn.cursor()
            sql="insert into users (name,email,password) values (%s,%s,%s)"
            values=(name,email,password)
            cursor.execute(sql,values)
            conn.commit()
            flash('registered successfully')
            return redirect(url_for('user_login'))
        except Exception as e:
            flash('registered already')
    return render_template('user_register.html')
@app.route('/user_login', methods=['GET','POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['user'] = email
            flash("Login successful!")
            return redirect(url_for('contract'))
        else:
            flash("Invalid email or password")

    return render_template('user_login.html')
@app.route('/contract',methods=['GET','POST'])
def contract():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('user_login'))
    if request.method=='POST':
       try:
            name=request.form['name']
            email=request.form['email']
            phone=request.form['phone']
            source=request.form['source']
            message=request.form['message']
            conn = get_db_connection()
            cursor = conn.cursor()
            sql="insert into leads (name,email,phone,message,source) values (%s,%s,%s,%s,%s)"
            values=(name,email,phone,message,source)
            cursor.execute(sql,values)
            #user=cursor.fetchone()
            conn.commit()
            flash('Data submitted successfully')
            
            
       except Exception as e:
            flash(e)
    return render_template('form.html')
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash('Please login first')
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    search = request.args.get('search')
    cursor=conn.cursor()
    if search:
        query = "SELECT * FROM leads WHERE name LIKE %s ORDER BY id DESC"
        cursor.execute(query, ('%' + search + '%',))
    else:
        cursor.execute('select * from leads order by id')
    leads=cursor.fetchall()
         # Total leads
    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]

    # New leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='new'")
    new = cursor.fetchone()[0]

    # Contacted leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='contacted'")
    contacted = cursor.fetchone()[0]

    # Converted leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='converted'")
    converted = cursor.fetchone()[0]
        
    cursor.close()

    return render_template('admin.html',leads=leads, total=total,
        new=new,
        contacted=contacted,
        converted=converted)
@app.route('/delete/<int:id>')
def delete_lead(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor=conn.cursor()
    cursor.execute('delete from leads where id=%s',(id,))
    conn.commit()
    cursor.close()
    return redirect(url_for('admin_dashboard')) 
@app.route('/edit/<int:id>',methods=['GET','POST'])
def edit_lead(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor=conn.cursor()
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        phon=request.form['phone']
        message=request.form['message']
        source=request.form['source']
        status=request.form['status']
        notes=request.form['notes']
        follow_up=request.form['follow_up']
        cursor.execute("""update leads set 
    name=%s,
    email=%s, 
    phone=%s,
    message=%s,
    source=%s,
    status=%s,
    notes=%s,
    followUpDate=%s where id=%s""",(name,email,phon,message,source,status,notes,follow_up,id))
        conn.commit()
        cursor.close()
        return redirect(url_for('admin_dashboard'))
    cursor.execute('select * from leads where id=%s',(id,))
    lead=cursor.fetchone()
    cursor.close()
    return render_template('edit.html',lead=lead)
@app.route('/logout',methods=['GET','POST'])
def logout():
    if request.method=='POST':
        email = request.form['email']
        if 'admin' in session:
           session.pop('admin')
           return redirect(url_for('admin_login'))
        else:
           flash('First login to Logout')
           return redirect(url_for('admin_login'))
    return render_template('logout.html')
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)