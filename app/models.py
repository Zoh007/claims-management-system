from app import db
from datetime import datetime

class Claim(db.Model):
    """Claim model for storing insurance claim data with robustness features"""
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(50), unique=True, nullable=False)
    patient_name = db.Column(db.String(200), nullable=False)
    billed_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    insurer_name = db.Column(db.String(100), nullable=False)
    discharge_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    details = db.relationship('ClaimDetail', backref='claim', lazy=True, cascade='all, delete-orphan')
    flags = db.relationship('Flag', backref='claim', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='claim', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Claim {self.claim_id} - {self.patient_name}>'

class ClaimDetail(db.Model):
    """Claim detail model for storing additional claim information with robustness features"""
    __tablename__ = 'claim_details'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    cpt_codes = db.Column(db.Text)  # Store as JSON string or comma-separated
    denial_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClaimDetail {self.id} for Claim {self.claim_id}>'

class Flag(db.Model):
    """Flag model for marking claims for review with robustness features"""
    __tablename__ = 'flags'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)  # Simple user identification
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Flag {self.id} for Claim {self.claim_id}>'

class Note(db.Model):
    """Note model for storing user annotations with robustness features"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.id} for Claim {self.claim_id}>'
