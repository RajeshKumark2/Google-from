from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    qualification = db.Column(db.String(50))
    current_job = db.Column(db.String(100))
    field = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    total_users = User.query.count()
    fields = db.session.query(User.field, db.func.count(User.id)).group_by(User.field).all()
    job_types = db.session.query(User.job_type, db.func.count(User.id)).group_by(User.job_type).all()
    qualifications = db.session.query(User.qualification, db.func.count(User.id)).group_by(User.qualification).all()    
    return render_template('dashboard.html',
                         total_users=total_users,
                         fields=dict(fields),
                         job_types=dict(job_types),
                         qualifications=dict(qualifications))

@app.route('/profiles')
def profiles():
    users = User.query.all()
    return render_template('profiles.html', users=users)

@app.route('/profile/<int:id>')
def view_profile(id):
    user = User.query.get_or_404(id)
    return render_template('view_profile.html', user=user)

@app.route('/add', methods=['GET', 'POST'])
def add_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        qualification = request.form['qualification']
        current_job = request.form['current_job']
        field = request.form['field']
        job_type = request.form['job_type']
        
        # Check if email exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'error')
            return redirect(url_for('add_profile'))
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            qualification=qualification,
            current_job=current_job,
            field=field,
            job_type=job_type
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('User added successfully!', 'success')
        return redirect(url_for('profiles'))
    
    return render_template('add_profile.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.qualification = request.form['qualification']
        user.current_job = request.form['current_job']
        user.field = request.form['field']
        user.job_type = request.form['job_type']
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('view_profile', id=id))
    
    return render_template('edit_profile.html', user=user)

@app.route('/delete/<int:id>')
def delete_profile(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('profiles'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    field = request.args.get('field', '')
    job_type = request.args.get('job_type', '')
    
    # Start with all users
    users_query = User.query
    
    if query:
        users_query = users_query.filter(
            (User.name.contains(query)) | 
            (User.email.contains(query)) |
            (User.current_job.contains(query))
        )
    
    if field:
        users_query = users_query.filter_by(field=field)
    
    if job_type:
        users_query = users_query.filter_by(job_type=job_type)
    
    users = users_query.all()
    
    # Get unique values for filters
    fields = db.session.query(User.field).distinct().all()
    job_types = db.session.query(User.job_type).distinct().all()    
    return render_template('search.html', 
                         users=users, 
                         query=query,
                         fields=[f[0] for f in fields],
                         job_types=[j[0] for j in job_types])

@app.route('/api/users')
def api_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'qualification': user.qualification,
            'current_job': user.current_job,
            'field': user.field,
            'job_type': user.job_type
        })
    return jsonify(result)


@app.route('/layout')
def layout():
    return render_template('layout.html')

if __name__ == '__main__':
    app.run(debug=True)
