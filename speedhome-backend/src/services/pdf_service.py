"""
PDF Generation Service for Tenancy Agreements
Handles creation of draft and final PDFs with watermarks
"""

import os
import logging
from datetime import datetime
from flask import current_app, render_template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import tempfile

logger = logging.getLogger(__name__)

class PDFService:
    """Service for generating tenancy agreement PDFs"""
    
    def __init__(self):
        self.font_config = FontConfiguration()
        
    def generate_agreement_pdf(self, agreement, is_draft=True, output_path=None):
        """
        Generate a PDF for a tenancy agreement
        
        Args:
            agreement: TenancyAgreement model instance
            is_draft: Whether to include draft watermark
            output_path: Optional custom output path
            
        Returns:
            str: Path to generated PDF file
        """
        try:
            # Render HTML template
            html_content = render_template(
                'tenancy_agreement.html',
                agreement=agreement,
                is_draft=is_draft
            )
            
            # Generate filename if not provided
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                draft_suffix = '_draft' if is_draft else '_final'
                filename = f"agreement_{agreement.id}{draft_suffix}_{timestamp}.pdf"
                
                # Create documents directory if it doesn't exist
                docs_dir = os.path.join(current_app.root_path, 'documents', 'agreements')
                os.makedirs(docs_dir, exist_ok=True)
                
                output_path = os.path.join(docs_dir, filename)
            
            # Generate PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(
                font_config=self.font_config,
                optimize_images=True
            )
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"Generated {'draft' if is_draft else 'final'} PDF for agreement {agreement.id}: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF for agreement {agreement.id}: {str(e)}")
            raise
    
    def generate_draft_pdf(self, agreement, output_path=None):
        """Generate a draft PDF with watermark"""
        return self.generate_agreement_pdf(agreement, is_draft=True, output_path=output_path)
    
    def generate_final_pdf(self, agreement, output_path=None):
        """Generate a final PDF without watermark"""
        return self.generate_agreement_pdf(agreement, is_draft=False, output_path=output_path)
    
    def update_agreement_pdfs(self, agreement):
        """
        Update both draft and final PDFs for an agreement
        
        Args:
            agreement: TenancyAgreement model instance
            
        Returns:
            dict: Paths to generated PDFs
        """
        try:
            # Generate draft PDF
            draft_path = self.generate_draft_pdf(agreement)
            
            # Generate final PDF if agreement is completed
            final_path = None
            if agreement.status == 'active':
                final_path = self.generate_final_pdf(agreement)
            
            return {
                'draft_pdf_path': draft_path,
                'final_pdf_path': final_path
            }
            
        except Exception as e:
            logger.error(f"Error updating PDFs for agreement {agreement.id}: {str(e)}")
            raise
    
    def get_pdf_download_url(self, agreement, pdf_type='draft'):
        """
        Get download URL for agreement PDF
        
        Args:
            agreement: TenancyAgreement model instance
            pdf_type: 'draft' or 'final'
            
        Returns:
            str: Download URL
        """
        if pdf_type == 'draft' and agreement.draft_pdf_path:
            return f"/api/tenancy-agreements/{agreement.id}/download/draft"
        elif pdf_type == 'final' and agreement.final_pdf_path:
            return f"/api/tenancy-agreements/{agreement.id}/download/final"
        else:
            return None
    
    def cleanup_old_pdfs(self, agreement):
        """Remove old PDF files for an agreement"""
        try:
            if agreement.draft_pdf_path and os.path.exists(agreement.draft_pdf_path):
                os.remove(agreement.draft_pdf_path)
                logger.info(f"Removed old draft PDF: {agreement.draft_pdf_path}")
            
            if agreement.final_pdf_path and os.path.exists(agreement.final_pdf_path):
                os.remove(agreement.final_pdf_path)
                logger.info(f"Removed old final PDF: {agreement.final_pdf_path}")
                
        except Exception as e:
            logger.warning(f"Error cleaning up old PDFs for agreement {agreement.id}: {str(e)}")

# Global instance
pdf_service = PDFService()

