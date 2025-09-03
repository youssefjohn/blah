import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, X, Eye, Download, Loader2 } from 'lucide-react';
import DepositAPI from '../services/DepositAPI';

const EvidenceUpload = ({ 
  depositId,
  claimItemId,
  evidenceType, // 'photo' or 'document'
  label, 
  required = false, 
  uploadedFiles = [],
  onUploadSuccess = () => {},
  onUploadError = () => {},
  onDelete = () => {},
  disabled = false
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewFile, setPreviewFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    if (!files.length) return;

    // Clear previous errors
    setError(null);

    // Process each file
    for (const file of files) {
      // Validate file
      const validation = DepositAPI.validateFile(file);
      if (!validation.valid) {
        setError(validation.error);
        continue;
      }

      // Start upload
      setIsUploading(true);
      setUploadProgress(0);

      try {
        const result = await DepositAPI.uploadEvidenceFile(
          depositId,
          claimItemId,
          evidenceType,
          file,
          (progress) => setUploadProgress(progress)
        );

        if (result.success) {
          onUploadSuccess(evidenceType, {
            id: result.data.evidence_id,
            name: file.name,
            size: file.size,
            type: file.type,
            path: result.data.file_path,
            evidence_type: evidenceType
          });
          setError(null);
        } else {
          setError(result.error);
          onUploadError(evidenceType, result.error);
        }
      } catch (err) {
        const errorMessage = 'Upload failed. Please try again.';
        setError(errorMessage);
        onUploadError(evidenceType, errorMessage);
      }
    }

    setIsUploading(false);
    setUploadProgress(0);
    // Clear file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (fileId) => {
    if (!fileId || disabled) return;

    try {
      const result = await DepositAPI.deleteEvidenceFile(depositId, fileId);
      
      if (result.success) {
        onDelete(evidenceType, fileId);
        setError(null);
        setPreviewUrl(null);
        setPreviewFile(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to delete file. Please try again.');
    }
  };

  const handlePreview = (file) => {
    if (!file || !depositId) return;
    
    const previewUrl = DepositAPI.getPreviewUrl(depositId, file.id);
    setPreviewUrl(previewUrl);
    setPreviewFile(file);
  };

  const handleDownload = (file) => {
    if (!file || !depositId) return;
    
    const downloadUrl = DepositAPI.getDownloadUrl(depositId, file.id);
    window.open(downloadUrl, '_blank');
  };

  const closePreview = () => {
    setPreviewUrl(null);
    setPreviewFile(null);
  };

  const acceptedTypes = evidenceType === 'photo' ? 'image/*' : '.pdf,.jpg,.jpeg,.png';

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 transition-colors hover:border-gray-400">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <label className="font-medium text-sm">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        {uploadedFiles.length > 0 && !isUploading && (
          <CheckCircle className="h-5 w-5 text-green-500" />
        )}
        {isUploading && (
          <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="mb-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1">Uploading... {uploadProgress}%</p>
        </div>
      )}

      {/* Uploaded Files Display */}
      {uploadedFiles.length > 0 && !isUploading ? (
        <div className="space-y-3 mb-3">
          {uploadedFiles.map((file, index) => {
            const isImage = file.type && file.type.startsWith('image/');
            const isPDF = file.type === 'application/pdf';
            
            return (
              <div key={file.id || index} className="flex items-center space-x-2 text-sm text-gray-700 bg-gray-50 p-3 rounded-md">
                <FileText className="h-4 w-4 text-gray-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {file.size ? DepositAPI.formatFileSize(file.size) : 'Unknown size'}
                  </p>
                </div>
                
                {/* Action Buttons */}
                <div className="flex space-x-1">
                  {(isImage || isPDF) && (
                    <button
                      onClick={() => handlePreview(file)}
                      disabled={disabled}
                      className="p-1 text-gray-500 hover:text-blue-600 disabled:opacity-50"
                      title="Preview"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => handleDownload(file)}
                    disabled={disabled}
                    className="p-1 text-gray-500 hover:text-green-600 disabled:opacity-50"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>

                  <button
                    onClick={() => handleDelete(file.id)}
                    disabled={disabled}
                    className="p-1 text-gray-500 hover:text-red-600 disabled:opacity-50"
                    title="Remove"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : null}

      {/* Upload Area */}
      {!isUploading && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            id={`upload-${evidenceType}-${claimItemId}`}
            accept={acceptedTypes}
            multiple
            onChange={handleFileSelect}
            disabled={disabled || isUploading}
            className="hidden"
          />
          <label
            htmlFor={`upload-${evidenceType}-${claimItemId}`}
            className={`flex items-center justify-center space-x-2 cursor-pointer bg-gray-50 hover:bg-gray-100 rounded-md p-4 transition-colors ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Upload className="h-5 w-5 text-gray-500" />
            <span className="text-sm text-gray-700">
              Click to upload {label.toLowerCase()}
            </span>
          </label>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {evidenceType === 'photo' ? 'JPG, PNG files only.' : 'PDF, JPG, PNG files only.'} Max 5MB per file.
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="flex items-center space-x-2 text-red-500 text-sm mt-3 bg-red-50 p-2 rounded-md">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Preview Modal */}
      {previewUrl && previewFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">
                Preview: {previewFile.name}
              </h3>
              <button
                onClick={closePreview}
                className="h-8 w-8 p-0 flex items-center justify-center text-gray-500 hover:text-gray-700"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 p-4 overflow-auto">
              {previewFile.type && previewFile.type.startsWith('image/') ? (
                <img
                  src={previewUrl}
                  alt={`Preview of ${previewFile.name}`}
                  className="max-w-full h-auto mx-auto"
                />
              ) : previewFile.type === 'application/pdf' ? (
                <iframe
                  src={previewUrl}
                  className="w-full h-96 border rounded"
                  title={`Preview of ${previewFile.name}`}
                />
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="h-12 w-12 mx-auto mb-2" />
                  <p>Preview not available for this file type</p>
                  <button
                    onClick={() => handleDownload(previewFile)}
                    className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Download to view
                  </button>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end space-x-2 p-4 border-t">
              <button
                onClick={() => handleDownload(previewFile)}
                className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
              >
                <Download className="h-4 w-4 mr-2 inline" />
                Download
              </button>
              <button
                onClick={closePreview}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvidenceUpload;

