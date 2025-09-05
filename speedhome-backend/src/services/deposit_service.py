"""
Deposit Service - Handles automatic deposit creation and management
Integrates with the existing tenancy agreement workflow
"""

from ..models.user import db
from ..models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from ..models.tenancy_agreement import TenancyAgreement
from ..models.property import Property
from ..models.user import User
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DepositService:
    """Service for managing deposit transactions and integration with tenancy agreements"""
    
    def create_deposit_for_agreement(self, tenancy_agreement_id):
        """
        Automatically create a deposit transaction when a tenancy agreement is activated
        
        Args:
            tenancy_agreement_id (int): ID of the activated tenancy agreement
            
        Returns:
            dict: Result with success status and deposit information
        """
        try:
            # Get the tenancy agreement
            agreement = TenancyAgreement.query.get(tenancy_agreement_id)
            if not agreement:
                return {
                    'success': False,
                    'error': 'Tenancy agreement not found'
                }
            
            # Verify agreement is active
            if agreement.status != 'active':
                return {
                    'success': False,
                    'error': 'Tenancy agreement must be active to create deposit'
                }
            
            # Check if deposit already exists
            existing_deposit = DepositTransaction.query.filter_by(
                tenancy_agreement_id=tenancy_agreement_id
            ).first()
            
            if existing_deposit:
                return {
                    'success': True,
                    'deposit': existing_deposit.to_dict(),
                    'message': 'Deposit already exists'
                }
            
            # Get property and calculate deposit amounts
            property_obj = Property.query.get(agreement.property_id)
            if not property_obj:
                return {
                    'success': False,
                    'error': 'Property not found'
                }
            
            # Calculate Malaysian 2-month deposit standard
            monthly_rent = float(agreement.monthly_rent) if agreement.monthly_rent else 0.0
            
            # Standard Malaysian deposit calculation
            total_amount = monthly_rent * 2.5  # 2 months security + 0.5 month utility
            
            # Create the deposit transaction
            deposit = DepositTransaction(
                tenancy_agreement_id=tenancy_agreement_id,
                property_id=agreement.property_id,
                tenant_id=agreement.tenant_id,
                landlord_id=agreement.landlord_id,
                
                # Deposit amounts (using correct column names)
                amount=total_amount,
                calculation_base=monthly_rent,
                calculation_multiplier=2.5,
                
                # Status and dates
                status=DepositTransactionStatus.HELD_IN_ESCROW,
                created_at=datetime.utcnow(),
                
                # Escrow details
                escrow_status='held',
                escrow_held_at=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(deposit)
            db.session.flush()  # Get the ID
            
            logger.info(f"Created deposit transaction {deposit.id} for agreement {tenancy_agreement_id}")
            logger.info(f"Deposit amount: RM{total_amount} (2.5 months of RM{monthly_rent})")
            
            return {
                'success': True,
                'deposit': deposit.to_dict(),
                'message': 'Deposit transaction created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating deposit for agreement {tenancy_agreement_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create deposit: {str(e)}'
            }
    
    def get_deposit_for_agreement(self, tenancy_agreement_id):
        """
        Get the deposit transaction for a specific tenancy agreement
        
        Args:
            tenancy_agreement_id (int): ID of the tenancy agreement
            
        Returns:
            dict: Deposit information or None if not found
        """
        try:
            deposit = DepositTransaction.query.filter_by(
                tenancy_agreement_id=tenancy_agreement_id
            ).first()
            
            if deposit:
                return {
                    'success': True,
                    'deposit': deposit.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': 'No deposit found for this tenancy agreement'
                }
                
        except Exception as e:
            logger.error(f"Error getting deposit for agreement {tenancy_agreement_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get deposit: {str(e)}'
            }
    
    def calculate_deposit_amount(self, monthly_rent, property_type='apartment'):
        """
        Calculate deposit amount based on Malaysian standards
        
        Args:
            monthly_rent (float): Monthly rent amount
            property_type (str): Type of property
            
        Returns:
            dict: Calculated deposit amounts
        """
        try:
            monthly_rent = float(monthly_rent)
            
            # Malaysian standard calculations
            security_deposit = monthly_rent * 2.0  # 2 months
            utility_deposit = monthly_rent * 0.5   # 0.5 month
            
            # Property type adjustments (if needed in future)
            if property_type == 'luxury':
                security_deposit = monthly_rent * 2.5  # 2.5 months for luxury
            elif property_type == 'commercial':
                security_deposit = monthly_rent * 3.0  # 3 months for commercial
            
            total_amount = security_deposit + utility_deposit
            
            return {
                'success': True,
                'calculation': {
                    'monthly_rent': monthly_rent,
                    'security_deposit': security_deposit,
                    'utility_deposit': utility_deposit,
                    'total_amount': total_amount,
                    'currency': 'MYR',
                    'calculation_method': 'malaysian_standard_2_months'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating deposit amount: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to calculate deposit: {str(e)}'
            }

