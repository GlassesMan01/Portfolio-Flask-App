from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from fpdf import FPDF

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///portfolio.db"
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)

class FirstApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    profiles = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"{self.id} - {self.first_name}"

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        bio = request.form['bio']
        skills = request.form['skills']
        profiles = request.form['profiles']

        profile_picture = request.files['profile_picture']
        filename = secure_filename(profile_picture.filename)
        profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Check if the email already exists
        existing_entry = FirstApp.query.filter_by(email=email).first()
        
        if existing_entry:
            # Update the existing entry
            existing_entry.first_name = first_name
            existing_entry.last_name = last_name
            existing_entry.phone = phone
            existing_entry.bio = bio
            existing_entry.skills = skills
            existing_entry.profiles = profiles
            existing_entry.profile_picture = filename
            db.session.commit()
            flash(f"Portfolio for {first_name} {last_name} has been updated!", 'success')
            return redirect(url_for('portfolio', portfolio_id=existing_entry.id))
        else:
            # Create a new entry
            portfolio_entry = FirstApp(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                bio=bio,
                skills=skills,
                profiles=profiles,
                profile_picture=filename
            )
            db.session.add(portfolio_entry)
            db.session.commit()
            flash(f"New portfolio for {first_name} {last_name} has been created!", 'success')
            return redirect(url_for('portfolio', portfolio_id=portfolio_entry.id))

    return render_template('form.html')

@app.route('/portfolio/<int:portfolio_id>')
def portfolio(portfolio_id):
    portfolio_entry = FirstApp.query.get_or_404(portfolio_id)
    return render_template('portfolio.html', portfolio=portfolio_entry)

@app.route('/download/<int:portfolio_id>')
def download(portfolio_id):
    portfolio_entry = FirstApp.query.get_or_404(portfolio_id)

    pdf = FPDF()
    pdf.add_page()

    # Add content to the PDF
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt=f"{portfolio_entry.first_name} {portfolio_entry.last_name}'s Portfolio", ln=True, align='C')

    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, txt=f"Email: {portfolio_entry.email}", ln=True)
    pdf.cell(200, 10, txt=f"Phone: {portfolio_entry.phone}", ln=True)
    pdf.cell(200, 10, txt=f"Bio: {portfolio_entry.bio}", ln=True)
    pdf.cell(200, 10, txt=f"Skills: {portfolio_entry.skills}", ln=True)
    pdf.cell(200, 10, txt=f"Profiles: {portfolio_entry.profiles}", ln=True)

    # Generate the PDF as a binary string (output to a string)
    pdf_output = BytesIO()
    pdf_content = pdf.output(dest='S').encode('latin1')  # Convert to bytes with encoding

    # Write the PDF content into BytesIO
    pdf_output.write(pdf_content)
    pdf_output.seek(0)  # Move cursor back to the start of the file

    # Send the file as a download, providing a download name
    return send_file(pdf_output, download_name=f'{portfolio_entry.first_name}_portfolio.pdf', as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
