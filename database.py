import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Get database connection details from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
Session = sessionmaker(bind=engine)

# Create a base class for declarative models
Base = declarative_base()

class Assessment(Base):
    __tablename__ = 'assessments'

    id = Column(Integer, primary_key=True)
    input_text = Column(Text, nullable=False)
    legal_issues = Column(Text, nullable=False)
    relevant_laws = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Assessment(id={self.id}, legal_issues={self.legal_issues})>"

# Create all tables
Base.metadata.create_all(engine)

def add_assessment(input_text, legal_issues, relevant_laws):
    session = Session()
    new_assessment = Assessment(
        input_text=input_text,
        legal_issues=','.join(legal_issues),
        relevant_laws=','.join(relevant_laws)
    )
    session.add(new_assessment)
    session.commit()
    session.close()

def get_assessment_by_input(input_text):
    session = Session()
    assessment = session.query(Assessment).filter_by(input_text=input_text).first()
    session.close()
    if assessment:
        return {
            'legal_issues': assessment.legal_issues.split(','),
            'relevant_laws': assessment.relevant_laws.split(',')
        }
    return None
