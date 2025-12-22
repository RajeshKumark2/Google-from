import pandas as pd
from app import app, db, User
import os

def import_csv_to_db():
    # CSV file path
    csv_file = 'data/form_responses.csv'
    
    # Read CSV file
    df = pd.read_csv(csv_file)
    
    # Rename columns if needed
    column_mapping = {
        'Name': 'name',
        'Email ID': 'email',
        'Highest Qualification': 'qualification',
        'Current Job Role/position': 'current_job',
        'Which field do you work in?': 'field',
        'What kind of job do you have?': 'job_type'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Import each row
        for index, row in df.iterrows():
            user = User(
                name=row['name'],
                email=row['email'],
                qualification=row['qualification'],
                current_job=row['current_job'],
                field=row['field'],
                job_type=row['job_type']
            )
            
            try:
                db.session.add(user)
                db.session.commit()
                print(f"Added: {row['name']}")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding {row['name']}: {e}")
        
        print("Data import completed!")

if __name__ == '__main__':
    import_csv_to_db()