import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import ApplicationAPI from '../services/ApplicationAPI';
import DocumentUpload from './DocumentUpload';

const EnhancedApplicationForm = ({ propertyId, onClose, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    // Personal Information
    full_name: '',
    phone_number: '',
    email_address: '',
    date_of_birth: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    
    // Employment Details
    employment_status: '',
    employer_name: '',
    job_title: '',
    employment_duration: '',
    monthly_income: '',
    additional_income: '',
    
    // Financial Information
    bank_name: '',
    account_type: '',
    credit_score: '',
    monthly_expenses: '',
    current_rent: '',
    
    // Rental History
    previous_address: '',
    previous_landlord_name: '',
    previous_landlord_phone: '',
    rental_duration: '',
    reason_for_moving: '',
    
    // Preferences
    move_in_date: '',
    lease_duration_preference: '',
    number_of_occupants: '',
    pets: '',
    smoking: '',
    additional_notes: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [applicationId, setApplicationId] = useState(null);
  const [isCreatingDraft, setIsCreatingDraft] = useState(false);

  // Debug propertyId
  useEffect(() => {
    console.log('Enhanced Application Form - propertyId received:', propertyId);
    console.log('Enhanced Application Form - propertyId type:', typeof propertyId);
  }, [propertyId]);

  const steps = [
    { title: 'Personal Information', icon: '👤' },
    { title: 'Employment Details', icon: '💼' },
    { title: 'Financial Information', icon: '💰' },
    { title: 'Rental History', icon: '🏠' },
    { title: 'Preferences', icon: '⚙️' },
    { title: 'Document Upload', icon: '📄' },
    { title: 'Review & Submit', icon: '✅' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const handleFileUpload = async (documentType, file) => {
    if (!file) return;

    // Validate file type and size
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!allowedTypes.includes(file.type)) {
      setErrors(prev => ({
        ...prev,
        [documentType]: 'Please upload PDF, JPG, or PNG files only'
      }));
      return;
    }

    if (file.size > maxSize) {
      setErrors(prev => ({
        ...prev,
        [documentType]: 'File size must be less than 5MB'
      }));
      return;
    }

    // Simulate file upload (in real implementation, upload to server)
    setUploadedFiles(prev => ({
      ...prev,
      [documentType]: {
        name: file.name,
        size: file.size,
        type: file.type,
        url: URL.createObjectURL(file)
      }
    }));

    setFormData(prev => ({
      ...prev,
      documents: {
        ...prev.documents,
        [documentType]: file
      }
    }));
  };

  const validateStep = (step) => {
    const newErrors = {};

    switch (step) {
      case 0: // Personal Information
        if (!formData.full_name) newErrors.full_name = 'Full name is required';
        if (!formData.phone_number) newErrors.phone_number = 'Phone number is required';
        if (!formData.email) newErrors.email = 'Email is required';
        if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required';
        break;
      
      case 1: // Employment Details
        if (!formData.employment_status) newErrors.employment_status = 'Employment status is required';
        if (formData.employment_status === 'employed' && !formData.employer_name) {
          newErrors.employer_name = 'Employer name is required';
        }
        if (!formData.monthly_income) newErrors.monthly_income = 'Monthly income is required';
        break;
      
      case 2: // Financial Information
        if (!formData.bank_name) newErrors.bank_name = 'Bank name is required';
        break;

      case 4: // Tenant Preferences
      if (!formData.move_in_date) {
        newErrors.move_in_date = 'Move-in date is required';
      }
      break;
      
      case 5: // Document Upload
        if (!uploadedFiles.id_document) newErrors.id_document = 'ID document is required';
        if (!uploadedFiles.income_proof) newErrors.income_proof = 'Income proof is required';
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = async () => {
    if (validateStep(currentStep)) {
      // If moving to Step 6 (Document Upload), create draft application
      if (currentStep === 4 && !applicationId) { // Step 4 -> Step 5 (0-indexed, so Step 6)
        await createDraftApplication();
      }
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    }
  };

  const createDraftApplication = async () => {
    try {
      setIsCreatingDraft(true);
      console.log('Creating draft application for document uploads...');
      console.log('propertyId value:', propertyId, 'type:', typeof propertyId);
      
      const draftData = {
        propertyId: propertyId, // Fixed: backend expects 'propertyId', not 'property_id'
        status: 'draft',
        // Include current form data
        full_name: formData.full_name,
        phone_number: formData.phone_number,
        email_address: formData.email_address,
        date_of_birth: formData.date_of_birth,
        employment_status: formData.employment_status,
        employer_name: formData.employer_name,
        monthly_income: formData.monthly_income,
        // Add other essential fields as needed
      };

      console.log('Draft application data being sent:', draftData);
      const response = await ApplicationAPI.createApplication(draftData);
      console.log('Draft application response:', response);
      console.log('Response type:', typeof response);
      console.log('Response keys:', Object.keys(response || {}));
      
      if (response && response.success && response.application && response.application.id) {
        const newApplicationId = response.application.id;
        setApplicationId(newApplicationId);
        console.log('✅ Draft application created successfully with ID:', newApplicationId);
        console.log('✅ ApplicationId state will be updated to:', newApplicationId);
        
        // Force a small delay to ensure state update
        setTimeout(() => {
          console.log('✅ Current applicationId state after timeout:', newApplicationId);
        }, 100);
      } else {
        console.error('❌ Failed to create draft application - Invalid response structure');
        console.error('❌ Expected: {success: true, application: {id: number}}');
        console.error('❌ Received:', response);
        console.error('❌ Error message:', response?.error || 'Unknown error');
      }
    } catch (error) {
      console.error('❌ Exception in createDraftApplication:', error);
      console.error('❌ Error message:', error.message);
      console.error('❌ Error stack:', error.stack);
    } finally {
      setIsCreatingDraft(false);
      console.log('✅ Draft creation process completed, isCreatingDraft set to false');
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    // Validate propertyId
    if (!propertyId) {
      console.error('Enhanced Application Form - propertyId is missing:', propertyId);
      setErrors({ submit: 'Property ID is missing. Please refresh the page and try again.' });
      return;
    }

    console.log('Enhanced Application Form - Submitting with propertyId:', propertyId);
    setIsSubmitting(true);
    try {
      // Prepare form data for submission
      const applicationData = {
        propertyId: propertyId,
        ...formData,
        step_completed: 6,
        is_complete: true
      };

      let response;
      
      // If we have a draft application, update it to final status
      if (applicationId) {
        console.log('Updating draft application to final status:', applicationId);
        response = await ApplicationAPI.updateApplication(applicationId, {
          ...applicationData,
          status: 'pending' // Change from draft to pending
        });
      } else {
        // Create new application (fallback if no draft was created)
        console.log('Creating new application (no draft found)');
        response = await ApplicationAPI.createApplication(applicationData);
        
        if (response.success && response.data && response.data.id) {
          setApplicationId(response.data.id);
        }
      }

      if (response.success) {
        console.log('Enhanced Application Form - Calling onSuccess callback');
        onSuccess && onSuccess();
      } else {
        console.log('Enhanced Application Form - API response failed:', response.error);
        setErrors({ submit: response.error || 'Failed to submit application' });
      }
    } catch (error) {
      setErrors({ submit: 'An error occurred while submitting the application' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Personal Information
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="full_name">Full Name *</Label>
                <Input
                  id="full_name"
                  value={formData.full_name}
                  onChange={(e) => handleInputChange('full_name', e.target.value)}
                  className={errors.full_name ? 'border-red-500' : ''}
                />
                {errors.full_name && <p className="text-red-500 text-sm mt-1">{errors.full_name}</p>}
              </div>
              
              <div>
                <Label htmlFor="phone_number">Phone Number *</Label>
                <Input
                  id="phone_number"
                  value={formData.phone_number}
                  onChange={(e) => handleInputChange('phone_number', e.target.value)}
                  className={errors.phone_number ? 'border-red-500' : ''}
                />
                {errors.phone_number && <p className="text-red-500 text-sm mt-1">{errors.phone_number}</p>}
              </div>
              
              <div>
                <Label htmlFor="email">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className={errors.email ? 'border-red-500' : ''}
                />
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              </div>
              
              <div>
                <Label htmlFor="date_of_birth">Date of Birth *</Label>
                <Input
                  id="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                  className={errors.date_of_birth ? 'border-red-500' : ''}
                />
                {errors.date_of_birth && <p className="text-red-500 text-sm mt-1">{errors.date_of_birth}</p>}
              </div>
              
              <div>
                <Label htmlFor="emergency_contact_name">Emergency Contact Name</Label>
                <Input
                  id="emergency_contact_name"
                  value={formData.emergency_contact_name}
                  onChange={(e) => handleInputChange('emergency_contact_name', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="emergency_contact_phone">Emergency Contact Phone</Label>
                <Input
                  id="emergency_contact_phone"
                  value={formData.emergency_contact_phone}
                  onChange={(e) => handleInputChange('emergency_contact_phone', e.target.value)}
                />
              </div>
            </div>
          </div>
        );

      case 1: // Employment Details
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="employment_status">Employment Status *</Label>
                <Select value={formData.employment_status} onValueChange={(value) => handleInputChange('employment_status', value)}>
                  <SelectTrigger className={errors.employment_status ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select employment status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="employed">Employed</SelectItem>
                    <SelectItem value="self-employed">Self-Employed</SelectItem>
                    <SelectItem value="unemployed">Unemployed</SelectItem>
                    <SelectItem value="student">Student</SelectItem>
                    <SelectItem value="retired">Retired</SelectItem>
                  </SelectContent>
                </Select>
                {errors.employment_status && <p className="text-red-500 text-sm mt-1">{errors.employment_status}</p>}
              </div>
              
              {(formData.employment_status === 'employed' || formData.employment_status === 'self-employed') && (
                <>
                  <div>
                    <Label htmlFor="employer_name">Employer/Company Name *</Label>
                    <Input
                      id="employer_name"
                      value={formData.employer_name}
                      onChange={(e) => handleInputChange('employer_name', e.target.value)}
                      className={errors.employer_name ? 'border-red-500' : ''}
                    />
                    {errors.employer_name && <p className="text-red-500 text-sm mt-1">{errors.employer_name}</p>}
                  </div>
                  
                  <div>
                    <Label htmlFor="job_title">Job Title</Label>
                    <Input
                      id="job_title"
                      value={formData.job_title}
                      onChange={(e) => handleInputChange('job_title', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="employment_duration">Employment Duration</Label>
                    <Input
                      id="employment_duration"
                      placeholder="e.g., 2 years"
                      value={formData.employment_duration}
                      onChange={(e) => handleInputChange('employment_duration', e.target.value)}
                    />
                  </div>
                </>
              )}
              
              <div>
                <Label htmlFor="monthly_income">Monthly Income (RM) *</Label>
                <Input
                  id="monthly_income"
                  type="number"
                  value={formData.monthly_income}
                  onChange={(e) => handleInputChange('monthly_income', e.target.value)}
                  className={errors.monthly_income ? 'border-red-500' : ''}
                />
                {errors.monthly_income && <p className="text-red-500 text-sm mt-1">{errors.monthly_income}</p>}
              </div>
              
              <div>
                <Label htmlFor="additional_income">Additional Income (RM)</Label>
                <Input
                  id="additional_income"
                  type="number"
                  value={formData.additional_income}
                  onChange={(e) => handleInputChange('additional_income', e.target.value)}
                />
              </div>
              
              {formData.additional_income && (
                <div>
                  <Label htmlFor="additional_income_source">Additional Income Source</Label>
                  <Input
                    id="additional_income_source"
                    value={formData.additional_income_source}
                    onChange={(e) => handleInputChange('additional_income_source', e.target.value)}
                  />
                </div>
              )}
            </div>
          </div>
        );

      case 2: // Financial Information
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="bank_name">Bank Name *</Label>
                <Input
                  id="bank_name"
                  value={formData.bank_name}
                  onChange={(e) => handleInputChange('bank_name', e.target.value)}
                  className={errors.bank_name ? 'border-red-500' : ''}
                />
                {errors.bank_name && <p className="text-red-500 text-sm mt-1">{errors.bank_name}</p>}
              </div>
              
              <div>
                <Label htmlFor="account_number">Account Number (Last 4 digits)</Label>
                <Input
                  id="account_number"
                  value={formData.account_number}
                  onChange={(e) => handleInputChange('account_number', e.target.value)}
                  placeholder="****1234"
                />
              </div>
              
              <div>
                <Label htmlFor="credit_score">Credit Score (if known)</Label>
                <Input
                  id="credit_score"
                  type="number"
                  min="300"
                  max="850"
                  value={formData.credit_score}
                  onChange={(e) => handleInputChange('credit_score', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="monthly_expenses">Monthly Expenses (RM)</Label>
                <Input
                  id="monthly_expenses"
                  type="number"
                  value={formData.monthly_expenses}
                  onChange={(e) => handleInputChange('monthly_expenses', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="current_rent">Current Rent (RM)</Label>
                <Input
                  id="current_rent"
                  type="number"
                  value={formData.current_rent}
                  onChange={(e) => handleInputChange('current_rent', e.target.value)}
                />
              </div>
            </div>
          </div>
        );

      case 3: // Rental History
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="previous_address">Previous Address</Label>
              <Textarea
                id="previous_address"
                value={formData.previous_address}
                onChange={(e) => handleInputChange('previous_address', e.target.value)}
                placeholder="Enter your previous rental address"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="previous_landlord_name">Previous Landlord Name</Label>
                <Input
                  id="previous_landlord_name"
                  value={formData.previous_landlord_name}
                  onChange={(e) => handleInputChange('previous_landlord_name', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="previous_landlord_phone">Previous Landlord Phone</Label>
                <Input
                  id="previous_landlord_phone"
                  value={formData.previous_landlord_phone}
                  onChange={(e) => handleInputChange('previous_landlord_phone', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="rental_duration">How long did you rent there?</Label>
                <Input
                  id="rental_duration"
                  value={formData.rental_duration}
                  onChange={(e) => handleInputChange('rental_duration', e.target.value)}
                  placeholder="e.g., 2 years"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="reason_for_moving">Reason for Moving</Label>
              <Textarea
                id="reason_for_moving"
                value={formData.reason_for_moving}
                onChange={(e) => handleInputChange('reason_for_moving', e.target.value)}
                placeholder="Please explain why you're moving"
              />
            </div>
          </div>
        );

      case 4: // Preferences
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                  <Label htmlFor="move_in_date">Preferred Move-in Date *</Label>
                  <Input
                    id="move_in_date"
                    type="date"
                    value={formData.move_in_date}
                    onChange={(e) => handleInputChange('move_in_date', e.target.value)}
                    className={errors.move_in_date ? 'border-red-500' : ''}
                  />
                  {errors.move_in_date && <p className="text-red-500 text-sm mt-1">{errors.move_in_date}</p>}
              </div>
              
              <div>
                <Label htmlFor="lease_duration_preference">Lease Duration Preference</Label>
                <Select value={formData.lease_duration_preference} onValueChange={(value) => handleInputChange('lease_duration_preference', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select lease duration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="6-months">6 Months</SelectItem>
                    <SelectItem value="1-year">1 Year</SelectItem>
                    <SelectItem value="2-years">2 Years</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="number_of_occupants">Number of Occupants</Label>
                <Input
                  id="number_of_occupants"
                  type="number"
                  min="1"
                  value={formData.number_of_occupants}
                  onChange={(e) => handleInputChange('number_of_occupants', parseInt(e.target.value))}
                />
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="pets"
                  checked={formData.pets}
                  onCheckedChange={(checked) => handleInputChange('pets', checked)}
                />
                <Label htmlFor="pets">I have pets</Label>
              </div>
              
              {formData.pets && (
                <div>
                  <Label htmlFor="pet_details">Pet Details</Label>
                  <Textarea
                    id="pet_details"
                    value={formData.pet_details}
                    onChange={(e) => handleInputChange('pet_details', e.target.value)}
                    placeholder="Please describe your pets (type, breed, size, etc.)"
                  />
                </div>
              )}
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="smoking"
                  checked={formData.smoking}
                  onCheckedChange={(checked) => handleInputChange('smoking', checked)}
                />
                <Label htmlFor="smoking">I am a smoker</Label>
              </div>
            </div>
            
            <div>
              <Label htmlFor="additional_notes">Additional Notes</Label>
              <Textarea
                id="additional_notes"
                value={formData.additional_notes}
                onChange={(e) => handleInputChange('additional_notes', e.target.value)}
                placeholder="Any additional information you'd like to share"
              />
            </div>
          </div>
        );

      case 5: // Document Upload
        return (
          <div className="space-y-6">
            <div className="text-sm text-gray-600 mb-4">
              Please upload the required documents. Accepted formats: PDF, JPG, PNG (max 5MB each)
            </div>

            {isCreatingDraft && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4 text-center">
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <p className="text-sm text-blue-800">Preparing document upload...</p>
                </div>
              </div>
            )}
            
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
                onUploadSuccess={(docType, fileInfo) => {
                  setUploadedFiles(prev => ({
                    ...prev,
                    [docType]: fileInfo
                  }));
                  setErrors(prev => {
                    const newErrors = { ...prev };
                    delete newErrors[docType];
                    return newErrors;
                  });
                }}
                onUploadError={(docType, error) => {
                  setErrors(prev => ({
                    ...prev,
                    [docType]: error
                  }));
                }}
                onDelete={(docType) => {
                  setUploadedFiles(prev => {
                    const newFiles = { ...prev };
                    delete newFiles[docType];
                    return newFiles;
                  });
                }}
                disabled={isCreatingDraft || !applicationId} // Disable while creating draft or if no applicationId
              />
            ))}
            
            {!applicationId && !isCreatingDraft && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <p className="text-sm text-yellow-800">
                  Document uploads will be enabled once you reach this step from the previous steps.
                </p>
              </div>
            )}

            {applicationId && (
              <div className="bg-green-50 border border-green-200 rounded-md p-3">
                <p className="text-sm text-green-800">
                  ✓ Document uploads are now enabled. You can upload your documents and they will be saved with your application.
                </p>
              </div>
            )}
          </div>
        );

      case 6: // Review & Submit
        return (
          <div className="space-y-6">
            <div className="text-lg font-semibold mb-4">Review Your Application</div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Personal Information</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-1">
                  <p><strong>Name:</strong> {formData.full_name}</p>
                  <p><strong>Email:</strong> {formData.email}</p>
                  <p><strong>Phone:</strong> {formData.phone_number}</p>
                  <p><strong>Date of Birth:</strong> {formData.date_of_birth}</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Employment</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-1">
                  <p><strong>Status:</strong> {formData.employment_status}</p>
                  <p><strong>Monthly Income:</strong> RM {formData.monthly_income}</p>
                  {formData.employer_name && <p><strong>Employer:</strong> {formData.employer_name}</p>}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Preferences</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-1">
                  <p><strong>Move-in Date:</strong> {formData.move_in_date || 'Not specified'}</p>
                  <p><strong>Lease Duration:</strong> {formData.lease_duration_preference || 'Not specified'}</p>
                  <p><strong>Occupants:</strong> {formData.number_of_occupants}</p>
                  <p><strong>Pets:</strong> {formData.pets ? 'Yes' : 'No'}</p>
                  <p><strong>Smoking:</strong> {formData.smoking ? 'Yes' : 'No'}</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Documents Uploaded</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-1">
                  {Object.entries(uploadedFiles).map(([key, file]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>{file.name}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
            
            {errors.submit && (
              <div className="flex items-center space-x-2 text-red-500 bg-red-50 p-3 rounded-md">
                <AlertCircle className="h-4 w-4" />
                <span>{errors.submit}</span>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <Card className="border-0 shadow-none">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-2xl">Enhanced Application Form</CardTitle>
              <button 
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Step {currentStep + 1} of {steps.length}</span>
                <span>{Math.round(progress)}% Complete</span>
              </div>
              <Progress value={progress} className="w-full" />
            </div>
            
            <div className="flex flex-wrap gap-2 mt-4">
              {steps.map((step, index) => (
                <div
                  key={index}
                  className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${
                    index === currentStep
                      ? 'bg-blue-100 text-blue-800'
                      : index < currentStep
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  <span>{step.icon}</span>
                  <span>{step.title}</span>
                </div>
              ))}
            </div>
          </CardHeader>
          
          <CardContent>
            <div className="min-h-[400px]">
              {renderStepContent()}
            </div>
            
            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 0}
              >
                Previous
              </Button>
              
              <div className="space-x-2">
                <Button variant="outline" onClick={onClose}>
                  Cancel
                </Button>
                
                {currentStep === steps.length - 1 ? (
                  <Button
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Application'}
                  </Button>
                ) : (
                  <Button
                    onClick={nextStep}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Next
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EnhancedApplicationForm;

