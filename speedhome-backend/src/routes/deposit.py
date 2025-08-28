@deposit_bp.route('/deposits/<int:deposit_id>/landlord-respond', methods=['POST'])
@jwt_required()
def landlord_respond_to_disputes(deposit_id):
    """Handle landlord's response to tenant disputes"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"DEBUG: Landlord response for deposit {deposit_id} from user {current_user_id}")
        print(f"DEBUG: Response data: {data}")
        
        # Get the deposit transaction
        deposit = DepositTransaction.query.get_or_404(deposit_id)
        
        # Verify landlord owns this deposit
        if deposit.landlord_id != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        # Process each response
        responses = data.get('responses', [])
        
        for response in responses:
            claim_id = response.get('claim_id')
            landlord_response = response.get('response')  # 'accept_counter', 'reject_counter', 'escalate'
            landlord_notes = response.get('landlord_notes', '')
            
            print(f"DEBUG: Processing claim {claim_id} with response {landlord_response}")
            
            # Get the claim
            claim = DepositClaim.query.get(claim_id)
            if not claim or claim.deposit_transaction_id != deposit_id:
                continue
            
            # Update claim based on landlord response
            if landlord_response == 'accept_counter':
                # Landlord accepts tenant's counter-offer
                if claim.tenant_counter_amount:
                    claim.approved_amount = claim.tenant_counter_amount
                    claim.status = DepositClaimStatus.RESOLVED
                    claim.resolution_notes = f"Landlord accepted tenant's counter-offer of RM {claim.tenant_counter_amount}. {landlord_notes}".strip()
                else:
                    # Tenant fully rejected, landlord accepts (no deduction)
                    claim.approved_amount = 0
                    claim.status = DepositClaimStatus.RESOLVED
                    claim.resolution_notes = f"Landlord accepted tenant's rejection. No deduction applied. {landlord_notes}".strip()
                    
            elif landlord_response == 'reject_counter':
                # Landlord rejects tenant's response, maintains original claim
                claim.status = DepositClaimStatus.DISPUTED
                claim.resolution_notes = f"Landlord rejected tenant's response. Maintaining original claim of RM {claim.claimed_amount}. {landlord_notes}".strip()
                
            elif landlord_response == 'escalate':
                # Escalate to mediation
                claim.status = DepositClaimStatus.MEDIATION
                claim.resolution_notes = f"Dispute escalated to mediation. {landlord_notes}".strip()
            
            claim.resolved_by = current_user_id
            claim.resolved_at = datetime.utcnow()
            claim.updated_at = datetime.utcnow()
            
            print(f"DEBUG: Updated claim {claim_id} status to {claim.status}")
        
        # Update deposit transaction status based on claim resolutions
        all_claims = DepositClaim.query.filter_by(deposit_transaction_id=deposit_id).all()
        
        resolved_count = sum(1 for claim in all_claims if claim.status in [DepositClaimStatus.RESOLVED, DepositClaimStatus.ACCEPTED])
        mediation_count = sum(1 for claim in all_claims if claim.status == DepositClaimStatus.MEDIATION)
        disputed_count = sum(1 for claim in all_claims if claim.status == DepositClaimStatus.DISPUTED)
        
        if mediation_count > 0:
            deposit.status = 'MEDIATION'
        elif disputed_count > 0:
            deposit.status = 'DISPUTED'
        elif resolved_count == len(all_claims):
            deposit.status = 'RESOLVED'
        
        deposit.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"DEBUG: Deposit status updated to {deposit.status}")
        
        return jsonify({
            'message': 'Landlord response submitted successfully',
            'deposit_status': deposit.status,
            'resolved_claims': resolved_count,
            'mediation_claims': mediation_count,
            'disputed_claims': disputed_count
        }), 200
        
    except Exception as e:
        print(f"ERROR: Error processing landlord response: {e}")
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500


