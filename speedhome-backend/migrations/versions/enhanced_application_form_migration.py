"""Enhanced Application Form migration

Revision ID: enhanced_app_form
Revises: 
Create Date: 2025-07-28 15:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'enhanced_app_form'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add Enhanced Application Form fields to applications table
    op.add_column('applications', sa.Column('full_name', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('phone_number', sa.String(20), nullable=True))
    op.add_column('applications', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('applications', sa.Column('emergency_contact_name', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('emergency_contact_phone', sa.String(20), nullable=True))
    
    # Employment Information
    op.add_column('applications', sa.Column('employment_status', sa.String(100), nullable=True))
    op.add_column('applications', sa.Column('employer_name', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('job_title', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('employment_duration', sa.String(100), nullable=True))
    op.add_column('applications', sa.Column('monthly_income', sa.Numeric(10, 2), nullable=True))
    op.add_column('applications', sa.Column('additional_income', sa.Numeric(10, 2), nullable=True))
    op.add_column('applications', sa.Column('additional_income_source', sa.String(255), nullable=True))
    
    # Financial Information
    op.add_column('applications', sa.Column('bank_name', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('account_number', sa.String(50), nullable=True))
    op.add_column('applications', sa.Column('credit_score', sa.Integer(), nullable=True))
    op.add_column('applications', sa.Column('monthly_expenses', sa.Numeric(10, 2), nullable=True))
    op.add_column('applications', sa.Column('current_rent', sa.Numeric(10, 2), nullable=True))
    
    # Rental History
    op.add_column('applications', sa.Column('previous_address', sa.Text(), nullable=True))
    op.add_column('applications', sa.Column('previous_landlord_name', sa.String(255), nullable=True))
    op.add_column('applications', sa.Column('previous_landlord_phone', sa.String(20), nullable=True))
    op.add_column('applications', sa.Column('reason_for_moving', sa.Text(), nullable=True))
    op.add_column('applications', sa.Column('rental_duration', sa.String(100), nullable=True))
    
    # Preferences and Additional Info
    op.add_column('applications', sa.Column('move_in_date', sa.Date(), nullable=True))
    op.add_column('applications', sa.Column('lease_duration_preference', sa.String(100), nullable=True))
    op.add_column('applications', sa.Column('number_of_occupants', sa.Integer(), nullable=True))
    op.add_column('applications', sa.Column('pets', sa.Boolean(), nullable=True, default=False))
    op.add_column('applications', sa.Column('pet_details', sa.Text(), nullable=True))
    op.add_column('applications', sa.Column('smoking', sa.Boolean(), nullable=True, default=False))
    op.add_column('applications', sa.Column('additional_notes', sa.Text(), nullable=True))
    
    # Document Upload Fields
    op.add_column('applications', sa.Column('id_document_path', sa.String(500), nullable=True))
    op.add_column('applications', sa.Column('income_proof_path', sa.String(500), nullable=True))
    op.add_column('applications', sa.Column('employment_letter_path', sa.String(500), nullable=True))
    op.add_column('applications', sa.Column('bank_statement_path', sa.String(500), nullable=True))
    op.add_column('applications', sa.Column('reference_letter_path', sa.String(500), nullable=True))
    op.add_column('applications', sa.Column('additional_documents_path', sa.Text(), nullable=True))
    
    # Application Completion Status
    op.add_column('applications', sa.Column('step_completed', sa.Integer(), nullable=True, default=0))
    op.add_column('applications', sa.Column('is_complete', sa.Boolean(), nullable=True, default=False))


def downgrade():
    # Remove Enhanced Application Form fields
    op.drop_column('applications', 'is_complete')
    op.drop_column('applications', 'step_completed')
    op.drop_column('applications', 'additional_documents_path')
    op.drop_column('applications', 'reference_letter_path')
    op.drop_column('applications', 'bank_statement_path')
    op.drop_column('applications', 'employment_letter_path')
    op.drop_column('applications', 'income_proof_path')
    op.drop_column('applications', 'id_document_path')
    op.drop_column('applications', 'additional_notes')
    op.drop_column('applications', 'smoking')
    op.drop_column('applications', 'pet_details')
    op.drop_column('applications', 'pets')
    op.drop_column('applications', 'number_of_occupants')
    op.drop_column('applications', 'lease_duration_preference')
    op.drop_column('applications', 'move_in_date')
    op.drop_column('applications', 'rental_duration')
    op.drop_column('applications', 'reason_for_moving')
    op.drop_column('applications', 'previous_landlord_phone')
    op.drop_column('applications', 'previous_landlord_name')
    op.drop_column('applications', 'previous_address')
    op.drop_column('applications', 'current_rent')
    op.drop_column('applications', 'monthly_expenses')
    op.drop_column('applications', 'credit_score')
    op.drop_column('applications', 'account_number')
    op.drop_column('applications', 'bank_name')
    op.drop_column('applications', 'additional_income_source')
    op.drop_column('applications', 'additional_income')
    op.drop_column('applications', 'monthly_income')
    op.drop_column('applications', 'employment_duration')
    op.drop_column('applications', 'job_title')
    op.drop_column('applications', 'employer_name')
    op.drop_column('applications', 'employment_status')
    op.drop_column('applications', 'emergency_contact_phone')
    op.drop_column('applications', 'emergency_contact_name')
    op.drop_column('applications', 'date_of_birth')
    op.drop_column('applications', 'email')
    op.drop_column('applications', 'phone_number')
    op.drop_column('applications', 'full_name')

