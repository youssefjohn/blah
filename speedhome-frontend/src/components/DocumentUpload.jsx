import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, X, Eye, Download, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import DocumentAPI from '../services/DocumentAPI';

const DocumentUpload = ({ 
  applicationId,
  documentType, 
  label, 
  required = false, 
  uploadedFile = null,
  onUploadSuccess = () => {},
  onUploadError = () => {},
  onDelete = () => {},
  disabled = false
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Clear previous errors
    setError(null);

    // Validate file
    const validation = DocumentAPI.validateFile(file);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }

    // Start upload
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const result = await DocumentAPI.uploadDocument(
        applicationId,
        documentType,
        file,
        (progress) => setUploadProgress(progress)
      );

      if (result.success) {
        onUploadSuccess(documentType, {
          name: file.name,
          size: file.size,
          type: file.type,
          path: result.data.file_path,
          info: result.data.file_info
        });
        setError(null);
      } else {
        setError(result.error);
        onUploadError(documentType, result.error);
      }
    } catch (err) {
      const errorMessage = 'Upload failed. Please try again.';
      setError(errorMessage);
      onUploadError(documentType, errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async () => {
    if (!uploadedFile || disabled) return;

    try {
      const result = await DocumentAPI.deleteDocument(applicationId, documentType);
      
      if (result.success) {
        onDelete(documentType);
        setError(null);
        setPreviewUrl(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to delete document. Please try again.');
    }
  };

  const handlePreview = () => {
    if (!uploadedFile || !applicationId) return;
    
    const previewUrl = DocumentAPI.getPreviewUrl(applicationId, documentType);
    setPreviewUrl(previewUrl);
  };

  const handleDownload = () => {
    if (!uploadedFile || !applicationId) return;
    
    const downloadUrl = DocumentAPI.getDownloadUrl(applicationId, documentType);
    window.open(downloadUrl, '_blank');
  };

  const closePreview = () => {
    setPreviewUrl(null);
  };

  const isImage = uploadedFile && uploadedFile.type && uploadedFile.type.startsWith('image/');
  const isPDF = uploadedFile && uploadedFile.type === 'application/pdf';

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 transition-colors hover:border-gray-400">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <Label className="font-medium text-sm">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        {uploadedFile && !isUploading && (
          <CheckCircle className="h-5 w-5 text-green-500" />
        )}
        {isUploading && (
          <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="mb-3">
          <Progress value={uploadProgress} className="h-2" />
          <p className="text-xs text-gray-500 mt-1">Uploading... {uploadProgress}%</p>
        </div>
      )}

      {/* Uploaded File Display */}
      {uploadedFile && !isUploading ? (
        <div className="space-y-3">
          {/* File Info */}
          <div className="flex items-center space-x-2 text-sm text-gray-700 bg-gray-50 p-3 rounded-md">
            <FileText className="h-4 w-4 text-gray-500" />
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{uploadedFile.name}</p>
              <p className="text-xs text-gray-500">
                {DocumentAPI.formatFileSize(uploadedFile.size)}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            {(isImage || isPDF) && (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreview}
                disabled={disabled}
                className="flex items-center space-x-1"
              >
                <Eye className="h-3 w-3" />
                <span>Preview</span>
              </Button>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              disabled={disabled}
              className="flex items-center space-x-1"
            >
              <Download className="h-3 w-3" />
              <span>Download</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleDelete}
              disabled={disabled}
              className="flex items-center space-x-1 text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <X className="h-3 w-3" />
              <span>Remove</span>
            </Button>
          </div>
        </div>
      ) : !isUploading ? (
        /* Upload Area */
        <div>
          <input
            ref={fileInputRef}
            type="file"
            id={`upload-${documentType}`}
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileSelect}
            disabled={disabled || isUploading}
            className="hidden"
          />
          <Label
            htmlFor={`upload-${documentType}`}
            className={`flex items-center justify-center space-x-2 cursor-pointer bg-gray-50 hover:bg-gray-100 rounded-md p-4 transition-colors ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Upload className="h-5 w-5 text-gray-500" />
            <span className="text-sm text-gray-700">
              Click to upload {label.toLowerCase()}
            </span>
          </Label>
          <p className="text-xs text-gray-500 mt-2 text-center">
            PDF, JPG, PNG files only. Max 5MB.
          </p>
        </div>
      ) : null}

      {/* Error Display */}
      {error && (
        <div className="flex items-center space-x-2 text-red-500 text-sm mt-3 bg-red-50 p-2 rounded-md">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Preview Modal */}
      {previewUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">
                Preview: {DocumentAPI.getDocumentDisplayName(documentType)}
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={closePreview}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 p-4 overflow-auto">
              {isImage ? (
                <img
                  src={previewUrl}
                  alt={`Preview of ${uploadedFile.name}`}
                  className="max-w-full h-auto mx-auto"
                />
              ) : isPDF ? (
                <iframe
                  src={previewUrl}
                  className="w-full h-96 border rounded"
                  title={`Preview of ${uploadedFile.name}`}
                />
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="h-12 w-12 mx-auto mb-2" />
                  <p>Preview not available for this file type</p>
                  <Button
                    variant="outline"
                    onClick={handleDownload}
                    className="mt-2"
                  >
                    Download to view
                  </Button>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end space-x-2 p-4 border-t">
              <Button variant="outline" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button onClick={closePreview}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;

