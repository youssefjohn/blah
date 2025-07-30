import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentAPI from '../services/DocumentAPI';

const DocumentUploadTest = () => {
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [applicationId, setApplicationId] = useState(1); // Test with application ID 1

  const handleUploadSuccess = (docType, fileInfo) => {
    console.log('Upload success:', docType, fileInfo);
    setUploadedFiles(prev => ({
      ...prev,
      [docType]: fileInfo
    }));
  };

  const handleUploadError = (docType, error) => {
    console.error('Upload error:', docType, error);
  };

  const handleDelete = (docType) => {
    console.log('Delete:', docType);
    setUploadedFiles(prev => {
      const newFiles = { ...prev };
      delete newFiles[docType];
      return newFiles;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
            Document Upload System Test
          </h1>
          
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h2 className="text-lg font-semibold text-blue-800 mb-2">Test Configuration</h2>
            <p className="text-blue-700">
              <strong>Application ID:</strong> {applicationId}
            </p>
            <p className="text-blue-700">
              <strong>Backend URL:</strong> http://localhost:5001
            </p>
          </div>

          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Upload Required Documents
            </h2>
            
            {[
              { key: 'id_document', label: 'ID Document', required: true },
              { key: 'income_proof', label: 'Income Proof', required: true },
              { key: 'employment_letter', label: 'Employment Letter', required: false },
              { key: 'bank_statement', label: 'Bank Statement', required: false },
              { key: 'reference_letter', label: 'Reference Letter', required: false },
              { key: 'credit_check', label: 'Credit Check', required: false }
            ].map(({ key, label, required }) => (
              <DocumentUpload
                key={key}
                applicationId={applicationId}
                documentType={key}
                label={label}
                required={required}
                uploadedFile={uploadedFiles[key]}
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
                onDelete={handleDelete}
              />
            ))}
          </div>

          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Upload Status</h3>
            <div className="space-y-2">
              {Object.entries(uploadedFiles).map(([docType, fileInfo]) => (
                <div key={docType} className="flex justify-between items-center text-sm">
                  <span className="font-medium">{DocumentAPI.getDocumentDisplayName(docType)}:</span>
                  <span className="text-green-600">✓ {fileInfo.name}</span>
                </div>
              ))}
              {Object.keys(uploadedFiles).length === 0 && (
                <p className="text-gray-500 text-sm">No documents uploaded yet</p>
              )}
            </div>
          </div>

          <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">Instructions</h3>
            <ul className="text-yellow-700 text-sm space-y-1">
              <li>• Upload test documents (PDF, JPG, PNG files only)</li>
              <li>• Maximum file size: 5MB per document</li>
              <li>• Click preview to view uploaded documents</li>
              <li>• Click download to save documents locally</li>
              <li>• Use remove to delete uploaded documents</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadTest;

