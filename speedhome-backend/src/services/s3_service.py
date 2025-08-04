"""
AWS S3 Service for Document Storage
Handles secure document upload, storage, and retrieval
"""

import os
import boto3
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class S3Service:
    """Service for managing documents with AWS S3"""
    
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'speedhome-documents')
        self.region = os.getenv('AWS_REGION', 'ap-southeast-1')
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Connected to S3 bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            logger.warning("AWS credentials not configured")
            self.s3_client = None
        except ClientError as e:
            logger.error(f"Failed to connect to S3: {str(e)}")
            self.s3_client = None
        except Exception as e:
            logger.error(f"S3 initialization error: {str(e)}")
            self.s3_client = None
    
    def upload_document(self, file_path, key, content_type='application/pdf'):
        """
        Upload a document to S3
        
        Args:
            file_path: Local path to the file
            key: S3 object key (path in bucket)
            content_type: MIME type of the file
            
        Returns:
            dict: Upload result
        """
        if not self.s3_client:
            return {'success': False, 'error': 'S3 not configured'}
        
        try:
            # Ensure key is secure
            key = self._sanitize_key(key)
            
            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'uploaded_at': datetime.utcnow().isoformat(),
                        'source': 'speedhome'
                    }
                }
            )
            
            logger.info(f"Uploaded document to S3: {key}")
            
            return {
                'success': True,
                'key': key,
                'url': f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def download_document(self, key, local_path):
        """
        Download a document from S3
        
        Args:
            key: S3 object key
            local_path: Local path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.download_file(self.bucket_name, key, local_path)
            logger.info(f"Downloaded document from S3: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 download error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return False
    
    def generate_presigned_url(self, key, expiration=3600, method='get_object'):
        """
        Generate a presigned URL for secure document access
        
        Args:
            key: S3 object key
            expiration: URL expiration time in seconds
            method: S3 method ('get_object' for download, 'put_object' for upload)
            
        Returns:
            str: Presigned URL or None if failed
        """
        if not self.s3_client:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                method,
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {key} (expires in {expiration}s)")
            return url
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None
    
    def delete_document(self, key):
        """
        Delete a document from S3
        
        Args:
            key: S3 object key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted document from S3: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 delete error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            return False
    
    def copy_document(self, source_key, dest_key):
        """
        Copy a document within S3
        
        Args:
            source_key: Source S3 object key
            dest_key: Destination S3 object key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.s3_client:
            return False
        
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dest_key,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Copied document in S3: {source_key} -> {dest_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 copy error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error copying in S3: {str(e)}")
            return False
    
    def list_documents(self, prefix=''):
        """
        List documents in S3 bucket
        
        Args:
            prefix: Key prefix to filter results
            
        Returns:
            list: List of document keys
        """
        if not self.s3_client:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    documents.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })
            
            return documents
            
        except ClientError as e:
            logger.error(f"S3 list error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error listing S3 documents: {str(e)}")
            return []
    
    def get_document_metadata(self, key):
        """
        Get metadata for a document
        
        Args:
            key: S3 object key
            
        Returns:
            dict: Document metadata or None if failed
        """
        if not self.s3_client:
            return None
        
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"S3 metadata error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting S3 metadata: {str(e)}")
            return None
    
    def _sanitize_key(self, key):
        """
        Sanitize S3 object key
        
        Args:
            key: Raw key string
            
        Returns:
            str: Sanitized key
        """
        # Remove leading/trailing slashes and spaces
        key = key.strip('/ ')
        
        # Replace spaces with underscores
        key = key.replace(' ', '_')
        
        # Ensure secure filename
        parts = key.split('/')
        parts[-1] = secure_filename(parts[-1])
        
        return '/'.join(parts)
    
    def generate_agreement_key(self, agreement_id, document_type='draft'):
        """
        Generate a standardized S3 key for agreement documents
        
        Args:
            agreement_id: Agreement ID
            document_type: Type of document ('draft', 'signed', 'final')
            
        Returns:
            str: S3 key
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"agreements/{agreement_id}/{document_type}_{timestamp}.pdf"
    
    def is_configured(self):
        """Check if S3 service is properly configured"""
        return self.s3_client is not None

# Global instance
s3_service = S3Service()

