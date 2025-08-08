#!/usr/bin/env python3
"""
Claims Management System - Main Application Entry Point
Built with robustness features and burger-themed enhancements
"""

from app import create_app, db
from app.models import Claim, ClaimDetail, Flag, Note
from datetime import datetime
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Shell context for robustness in development"""
    return {
        'db': db,
        'Claim': Claim,
        'ClaimDetail': ClaimDetail,
        'Flag': Flag,
        'Note': Note
    }

@app.cli.command()
def init_db():
    """Initialize the database with robustness features"""
    db.create_all()
    print("Database initialized with burger-themed robustness!")

@app.cli.command()
def load_sample_data():
    """Load sample data for testing robustness features"""
    # Check if data already exists
    if Claim.query.first():
        print("Sample data already exists. Skipping...")
        return
    
    # Sample claims data
    sample_claims = [
        {
            'claim_id': '30001',
            'patient_name': 'Virginia Rhodes',
            'billed_amount': 639787.37,
            'paid_amount': 16001.57,
            'status': 'Denied',
            'insurer_name': 'United Healthcare',
            'discharge_date': datetime.strptime('2022-12-19', '%Y-%m-%d').date()
        },
        {
            'claim_id': '30002',
            'patient_name': 'Maria Chen',
            'billed_amount': 3400.00,
            'paid_amount': 0.00,
            'status': 'Denied',
            'insurer_name': 'Aetna',
            'discharge_date': datetime.strptime('2023-07-16', '%Y-%m-%d').date()
        },
        {
            'claim_id': '30003',
            'patient_name': 'Ravi Kumar',
            'billed_amount': 5725.00,
            'paid_amount': 2000.00,
            'status': 'Under Review',
            'insurer_name': 'Cigna',
            'discharge_date': datetime.strptime('2023-06-30', '%Y-%m-%d').date()
        },
        {
            'claim_id': '30004',
            'patient_name': 'Sarah Johnson',
            'billed_amount': 2200.00,
            'paid_amount': 2200.00,
            'status': 'Paid',
            'insurer_name': 'Blue Cross Blue Shield',
            'discharge_date': datetime.strptime('2023-07-02', '%Y-%m-%d').date()
        },
        {
            'claim_id': '30005',
            'patient_name': 'Laura Martínez',
            'billed_amount': 4000.00,
            'paid_amount': 0.00,
            'status': 'Denied',
            'insurer_name': 'Humana',
            'discharge_date': datetime.strptime('2023-07-19', '%Y-%m-%d').date()
        }
    ]
    
    # Add claims
    for claim_data in sample_claims:
        claim = Claim(**claim_data)
        db.session.add(claim)
    
    # Add sample details
    sample_details = [
        {
            'claim_id': 1,  # This will be set after claims are created
            'cpt_codes': '99204, 82947, 99406',
            'denial_reason': 'Policy terminated before service date'
        }
    ]
    
    db.session.commit()
    
    # Add details after claims are created
    claim = Claim.query.filter_by(claim_id='30001').first()
    if claim:
        detail = ClaimDetail(
            claim_id=claim.id,
            cpt_codes='99204, 82947, 99406',
            denial_reason='Policy terminated before service date'
        )
        db.session.add(detail)
    
    db.session.commit()
    print("Sample data loaded successfully with burger-themed robustness!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
