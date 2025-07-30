import React, { useState } from 'react';
import { Eye, Download, X } from 'lucide-react';
import DocumentAPI from '../services/DocumentAPI';

const ApplicationDetailsModal = ({ application, onClose, onApprove, onReject }) => {
  const [previewDocument, setPreviewDocument] = useState(null);
  
  if (!application) return null;

  const formatCurrency = (amount) => {
    if (!amount) return 'Not specified';
    return `RM ${parseFloat(amount).toLocaleString()}`;
  };

  const handleDocumentPreview = (documentType) => {
    if (!application.id) return;
    
    const previewUrl = DocumentAPI.getPreviewUrl(application.id, documentType);
    setPreviewDocument({
      type: documentType,
      url: previewUrl,
      name: DocumentAPI.getDocumentDisplayName(documentType)
    });
  };

  const handleDocumentDownload = (documentType) => {
    if (!application.id) return;
    
    const downloadUrl = DocumentAPI.getDownloadUrl(application.id, documentType);
    window.open(downloadUrl, '_blank');
  };

  const closePreview = () => {
    setPreviewDocument(null);
  };

  const renderDocumentRow = (documentType, label, path) => {
    const hasDocument = !!path;
    
    return (
      <div key={documentType} className="flex justify-between items-center py-2">
        <span className="text-gray-600">{label}:</span>
        <div className="flex items-center space-x-2">
          <span className={`font-medium ${hasDocument ? 'text-green-600' : 'text-red-600'}`}>
            {hasDocument ? '✓ Uploaded' : '✗ Not uploaded'}
          </span>
          {hasDocument && (
            <div className="flex space-x-1">
              <button
                onClick={() => handleDocumentPreview(documentType)}
                className="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded"
                title="Preview document"
              >
                <Eye className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleDocumentDownload(documentType)}
                className="p-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded"
                title="Download document"
              >
                <Download className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString();
  };

  const formatBoolean = (value) => {
    if (value === null || value === undefined) return 'Not specified';
    return value ? 'Yes' : 'No';
  };

  const calculateAge = (dateOfBirth) => {
    if (!dateOfBirth) return 'Not specified';
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return `${age} years old`;
  };

  const getRentToIncomeRatio = () => {
    if (application.rent_to_income_ratio) {
      return `${application.rent_to_income_ratio}%`;
    }
    return 'Not calculated';
  };

  const getFinancialHealthColor = () => {
    if (!application.rent_to_income_ratio) return 'text-gray-600';
    const ratio = application.rent_to_income_ratio;
    if (ratio <= 30) return 'text-green-600';
    if (ratio <= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getFinancialHealthText = () => {
    if (!application.rent_to_income_ratio) return 'Unable to assess';
    const ratio = application.rent_to_income_ratio;
    if (ratio <= 30) return 'Excellent';
    if (ratio <= 40) return 'Good';
    return 'High Risk';
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] shadow-2xl">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">Enhanced Application Details</h3>
              <p className="text-sm text-gray-500 mt-1">For property: {application.property?.title || 'N/A'}</p>
              <p className="text-xs text-gray-400">Applied on: {formatDate(application.created_at)}</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">
              ×
            </button>
          </div>

          {/* Content - Scrollable */}
          <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
            
            {/* Personal Information Section */}
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  {application.full_name ? application.full_name.charAt(0).toUpperCase() : 'T'}
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-bold text-gray-800">{application.full_name || 'Not provided'}</h4>
                  <p className="text-sm text-gray-600">{application.email || 'Not provided'}</p>
                  <p className="text-sm text-gray-600">{application.phone_number || 'Not provided'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">Age</p>
                  <p className="font-semibold text-gray-700">{calculateAge(application.date_of_birth)}</p>
                </div>
              </div>
              
              {application.emergency_contact_name && (
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <h5 className="font-semibold text-gray-700 mb-2">Emergency Contact</h5>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Name:</span>
                      <span className="ml-2 font-medium">{application.emergency_contact_name}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Phone:</span>
                      <span className="ml-2 font-medium">{application.emergency_contact_phone || 'Not provided'}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Employment & Financial Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Employment Information */}
              <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Employment Details
                </h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className="font-medium capitalize">{application.employment_status || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Employer:</span>
                    <span className="font-medium">{application.employer_name || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Job Title:</span>
                    <span className="font-medium">{application.job_title || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium">{application.employment_duration || 'Not specified'}</span>
                  </div>
                </div>
              </div>

              {/* Financial Information */}
              <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                  Financial Profile
                </h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Income:</span>
                    <span className="font-medium">{formatCurrency(application.monthly_income)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Additional Income:</span>
                    <span className="font-medium">{formatCurrency(application.additional_income)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Expenses:</span>
                    <span className="font-medium">{formatCurrency(application.monthly_expenses)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Rent:</span>
                    <span className="font-medium">{formatCurrency(application.current_rent)}</span>
                  </div>
                  <div className="pt-2 border-t border-yellow-200">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Rent-to-Income Ratio:</span>
                      <span className={`font-bold ${getFinancialHealthColor()}`}>
                        {getRentToIncomeRatio()}
                      </span>
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-gray-600">Financial Health:</span>
                      <span className={`font-semibold ${getFinancialHealthColor()}`}>
                        {getFinancialHealthText()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Banking Information */}
            {(application.bank_name || application.credit_score) && (
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  Banking & Credit Information
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 block">Bank:</span>
                    <span className="font-medium">{application.bank_name || 'Not provided'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 block">Account Number:</span>
                    <span className="font-medium">{application.account_number ? `****${application.account_number.slice(-4)}` : 'Not provided'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 block">Credit Score:</span>
                    <span className="font-medium">{application.credit_score || 'Not provided'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Rental History */}
            {application.previous_address && (
              <div className="bg-indigo-50 p-6 rounded-lg border border-indigo-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <span className="w-2 h-2 bg-indigo-500 rounded-full mr-2"></span>
                  Rental History
                </h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="text-gray-600 block">Previous Address:</span>
                    <span className="font-medium">{application.previous_address}</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-600 block">Previous Landlord:</span>
                      <span className="font-medium">{application.previous_landlord_name || 'Not provided'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600 block">Landlord Phone:</span>
                      <span className="font-medium">{application.previous_landlord_phone || 'Not provided'}</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-600 block">Rental Duration:</span>
                      <span className="font-medium">{application.rental_duration || 'Not provided'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600 block">Reason for Moving:</span>
                      <span className="font-medium">{application.reason_for_moving || 'Not provided'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Preferences & Requirements */}
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <span className="w-2 h-2 bg-gray-500 rounded-full mr-2"></span>
                Tenant Preferences
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 block">Preferred Move-in Date:</span>
                  <span className="font-medium">{formatDate(application.move_in_date)}</span>
                </div>
                <div>
                  <span className="text-gray-600 block">Lease Duration Preference:</span>
                  <span className="font-medium">{application.lease_duration_preference || 'Not specified'}</span>
                </div>
                <div>
                  <span className="text-gray-600 block">Number of Occupants:</span>
                  <span className="font-medium">{application.number_of_occupants || 'Not specified'}</span>
                </div>
                <div>
                  <span className="text-gray-600 block">Pets:</span>
                  <span className="font-medium">{formatBoolean(application.pets)}</span>
                </div>
                <div>
                  <span className="text-gray-600 block">Smoking:</span>
                  <span className="font-medium">{formatBoolean(application.smoking)}</span>
                </div>
              </div>
              
              {application.pet_details && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <span className="text-gray-600 block">Pet Details:</span>
                  <span className="font-medium">{application.pet_details}</span>
                </div>
              )}
              
              {application.additional_notes && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <span className="text-gray-600 block">Additional Notes:</span>
                  <span className="font-medium">{application.additional_notes}</span>
                </div>
              )}
            </div>

            {/* Documents Section */}
              <div className="bg-orange-50 p-6 rounded-lg border border-orange-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
                  Document Status
                </h4>
                <div className="space-y-2 text-sm">
                  {renderDocumentRow('id_document', 'ID Document', application.id_document_path)}
                  {renderDocumentRow('income_proof', 'Income Proof', application.income_proof_path)}
                  {renderDocumentRow('employment_letter', 'Employment Letter', application.employment_letter_path)}
                  {renderDocumentRow('bank_statement', 'Bank Statement', application.bank_statement_path)}
                  {renderDocumentRow('reference_letter', 'Reference Letter', application.reference_letter_path)}
                  {renderDocumentRow('credit_check', 'Credit Check', application.credit_check_path)}
                </div>
              </div>

            {/* Application Status */}
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Application Status
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 block">Current Status:</span>
                  <span className={`font-bold capitalize px-2 py-1 rounded text-xs ${
                    application.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    application.status === 'approved' ? 'bg-green-100 text-green-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {application.status}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 block">Application Completed:</span>
                  <span className="font-medium">{formatBoolean(application.is_complete)}</span>
                </div>
                <div>
                  <span className="text-gray-600 block">Steps Completed:</span>
                  <span className="font-medium">{application.step_completed || 0}/7</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4 pt-6 border-t mt-6">
            <button 
              onClick={onClose} 
              className="px-6 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            {application.status === 'pending' && (
              <>
                <button 
                  onClick={() => onReject(application.id)} 
                  className="px-6 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors"
                >
                  Reject Application
                </button>
                <button 
                  onClick={() => onApprove(application.id)} 
                  className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Approve Application
                </button>
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Document Preview Modal */}
      {previewDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full flex flex-col">
            {/* Preview Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">
                Preview: {previewDocument.name}
              </h3>
              <button
                onClick={closePreview}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Preview Content */}
            <div className="flex-1 p-4 overflow-auto">
              {previewDocument.type && (previewDocument.type.includes('image') || 
                application[`${previewDocument.type}_path`]?.toLowerCase().includes('.jpg') ||
                application[`${previewDocument.type}_path`]?.toLowerCase().includes('.jpeg') ||
                application[`${previewDocument.type}_path`]?.toLowerCase().includes('.png')) ? (
                <img
                  src={previewDocument.url}
                  alt={`Preview of ${previewDocument.name}`}
                  className="max-w-full h-auto mx-auto"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
              ) : (
                <iframe
                  src={previewDocument.url}
                  className="w-full h-96 border rounded"
                  title={`Preview of ${previewDocument.name}`}
                />
              )}
              
              {/* Fallback for failed image loads */}
              <div className="text-center text-gray-500 py-8 hidden">
                <p>Preview not available</p>
                <button
                  onClick={() => handleDocumentDownload(previewDocument.type)}
                  className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Download to view
                </button>
              </div>
            </div>

            {/* Preview Footer */}
            <div className="flex justify-end space-x-2 p-4 border-t">
              <button
                onClick={() => handleDocumentDownload(previewDocument.type)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Download</span>
              </button>
              <button
                onClick={closePreview}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
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

export default ApplicationDetailsModal;

