import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  User, 
  Briefcase, 
  DollarSign, 
  Home, 
  FileText, 
  Download, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Calendar,
  Phone,
  Mail,
  MapPin
} from 'lucide-react';
import ApplicationAPI from '../services/ApplicationAPI';

const ApplicationDetailsModal = ({ application, isOpen, onClose, onStatusUpdate }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  if (!application) return null;

  const handleStatusUpdate = async (newStatus) => {
    setIsUpdating(true);
    try {
      const response = await ApplicationAPI.updateApplicationStatus(application.id, newStatus);
      if (response.success) {
        onStatusUpdate && onStatusUpdate(application.id, newStatus);
        onClose();
      }
    } catch (error) {
      console.error('Error updating application status:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRentToIncomeRatio = () => {
    if (application.rent_to_income_ratio) {
      return application.rent_to_income_ratio;
    }
    
    const monthlyIncome = parseFloat(application.monthly_income || 0);
    const additionalIncome = parseFloat(application.additional_income || 0);
    const totalIncome = monthlyIncome + additionalIncome;
    const rent = parseFloat(application.property?.rent || 0);
    
    if (totalIncome > 0 && rent > 0) {
      return ((rent / totalIncome) * 100).toFixed(2);
    }
    return null;
  };

  const getRiskLevel = () => {
    const ratio = getRentToIncomeRatio();
    if (!ratio) return { level: 'Unknown', color: 'gray' };
    
    if (ratio <= 30) return { level: 'Low Risk', color: 'green' };
    if (ratio <= 40) return { level: 'Medium Risk', color: 'yellow' };
    return { level: 'High Risk', color: 'red' };
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'Not provided';
    return `RM ${parseFloat(amount).toLocaleString()}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString();
  };

  const riskLevel = getRiskLevel();
  const rentToIncomeRatio = getRentToIncomeRatio();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-2xl">Application Details</DialogTitle>
            <Badge className={getStatusColor(application.status)}>
              {application.status?.toUpperCase()}
            </Badge>
          </div>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="employment" className="flex items-center space-x-2">
              <Briefcase className="h-4 w-4" />
              <span>Employment</span>
            </TabsTrigger>
            <TabsTrigger value="financial" className="flex items-center space-x-2">
              <DollarSign className="h-4 w-4" />
              <span>Financial</span>
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center space-x-2">
              <Home className="h-4 w-4" />
              <span>History</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Documents</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Personal Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <User className="h-5 w-5" />
                    <span>Personal Information</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-gray-500" />
                    <span className="font-medium">Name:</span>
                    <span>{application.full_name || application.tenant?.name || 'Not provided'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4 text-gray-500" />
                    <span className="font-medium">Email:</span>
                    <span>{application.email || application.tenant?.email || 'Not provided'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Phone className="h-4 w-4 text-gray-500" />
                    <span className="font-medium">Phone:</span>
                    <span>{application.phone_number || 'Not provided'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    <span className="font-medium">Date of Birth:</span>
                    <span>{formatDate(application.date_of_birth)}</span>
                  </div>
                  {application.emergency_contact_name && (
                    <div className="pt-2 border-t">
                      <p className="font-medium text-sm text-gray-600 mb-1">Emergency Contact</p>
                      <p>{application.emergency_contact_name}</p>
                      <p className="text-sm text-gray-600">{application.emergency_contact_phone}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Financial Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <DollarSign className="h-5 w-5" />
                    <span>Financial Summary</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">Monthly Income:</span>
                    <span>{formatCurrency(application.monthly_income)}</span>
                  </div>
                  {application.additional_income && (
                    <div className="flex justify-between">
                      <span className="font-medium">Additional Income:</span>
                      <span>{formatCurrency(application.additional_income)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="font-medium">Property Rent:</span>
                    <span>{formatCurrency(application.property?.rent)}</span>
                  </div>
                  <Separator />
                  {rentToIncomeRatio && (
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">Rent-to-Income Ratio:</span>
                        <span className="font-bold">{rentToIncomeRatio}%</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">Risk Level:</span>
                        <Badge className={`bg-${riskLevel.color}-100 text-${riskLevel.color}-800`}>
                          {riskLevel.level}
                        </Badge>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Application Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Home className="h-5 w-5" />
                    <span>Preferences</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">Move-in Date:</span>
                    <span>{formatDate(application.move_in_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Lease Duration:</span>
                    <span>{application.lease_duration_preference || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Occupants:</span>
                    <span>{application.number_of_occupants || 1}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Pets:</span>
                    <span>{application.pets ? 'Yes' : 'No'}</span>
                  </div>
                  {application.pets && application.pet_details && (
                    <div className="pt-2 border-t">
                      <p className="font-medium text-sm text-gray-600 mb-1">Pet Details</p>
                      <p className="text-sm">{application.pet_details}</p>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="font-medium">Smoking:</span>
                    <span>{application.smoking ? 'Yes' : 'No'}</span>
                  </div>
                </CardContent>
              </Card>

              {/* Application Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Calendar className="h-5 w-5" />
                    <span>Timeline</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">Applied:</span>
                    <span>{formatDate(application.created_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Last Updated:</span>
                    <span>{formatDate(application.updated_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Completion:</span>
                    <span>{application.is_complete ? 'Complete' : 'Incomplete'}</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            {application.additional_notes && (
              <Card>
                <CardHeader>
                  <CardTitle>Additional Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{application.additional_notes}</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="employment" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Briefcase className="h-5 w-5" />
                  <span>Employment Details</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="font-medium">Employment Status</Label>
                    <p className="text-gray-700 capitalize">{application.employment_status || 'Not provided'}</p>
                  </div>
                  
                  {application.employer_name && (
                    <div>
                      <Label className="font-medium">Employer</Label>
                      <p className="text-gray-700">{application.employer_name}</p>
                    </div>
                  )}
                  
                  {application.job_title && (
                    <div>
                      <Label className="font-medium">Job Title</Label>
                      <p className="text-gray-700">{application.job_title}</p>
                    </div>
                  )}
                  
                  {application.employment_duration && (
                    <div>
                      <Label className="font-medium">Employment Duration</Label>
                      <p className="text-gray-700">{application.employment_duration}</p>
                    </div>
                  )}
                  
                  <div>
                    <Label className="font-medium">Monthly Income</Label>
                    <p className="text-gray-700 font-semibold">{formatCurrency(application.monthly_income)}</p>
                  </div>
                  
                  {application.additional_income && (
                    <>
                      <div>
                        <Label className="font-medium">Additional Income</Label>
                        <p className="text-gray-700 font-semibold">{formatCurrency(application.additional_income)}</p>
                      </div>
                      
                      {application.additional_income_source && (
                        <div>
                          <Label className="font-medium">Additional Income Source</Label>
                          <p className="text-gray-700">{application.additional_income_source}</p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="financial" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Banking Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <Label className="font-medium">Bank Name</Label>
                    <p className="text-gray-700">{application.bank_name || 'Not provided'}</p>
                  </div>
                  
                  {application.account_number && (
                    <div>
                      <Label className="font-medium">Account Number</Label>
                      <p className="text-gray-700">****{application.account_number}</p>
                    </div>
                  )}
                  
                  {application.credit_score && (
                    <div>
                      <Label className="font-medium">Credit Score</Label>
                      <p className="text-gray-700 font-semibold">{application.credit_score}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Financial Analysis</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {rentToIncomeRatio && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">Rent-to-Income Ratio</span>
                        <span className="text-2xl font-bold">{rentToIncomeRatio}%</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {riskLevel.color === 'green' && <CheckCircle className="h-4 w-4 text-green-500" />}
                        {riskLevel.color === 'yellow' && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                        {riskLevel.color === 'red' && <XCircle className="h-4 w-4 text-red-500" />}
                        <Badge className={`bg-${riskLevel.color}-100 text-${riskLevel.color}-800`}>
                          {riskLevel.level}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mt-2">
                        {riskLevel.color === 'green' && 'Excellent financial stability. Rent is well within recommended limits.'}
                        {riskLevel.color === 'yellow' && 'Moderate risk. Rent is at the upper limit of recommended range.'}
                        {riskLevel.color === 'red' && 'High risk. Rent exceeds recommended income percentage.'}
                      </p>
                    </div>
                  )}
                  
                  {application.monthly_expenses && (
                    <div>
                      <Label className="font-medium">Monthly Expenses</Label>
                      <p className="text-gray-700">{formatCurrency(application.monthly_expenses)}</p>
                    </div>
                  )}
                  
                  {application.current_rent && (
                    <div>
                      <Label className="font-medium">Current Rent</Label>
                      <p className="text-gray-700">{formatCurrency(application.current_rent)}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Home className="h-5 w-5" />
                  <span>Rental History</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {application.previous_address && (
                  <div>
                    <Label className="font-medium">Previous Address</Label>
                    <p className="text-gray-700">{application.previous_address}</p>
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {application.previous_landlord_name && (
                    <div>
                      <Label className="font-medium">Previous Landlord</Label>
                      <p className="text-gray-700">{application.previous_landlord_name}</p>
                      {application.previous_landlord_phone && (
                        <p className="text-sm text-gray-600">{application.previous_landlord_phone}</p>
                      )}
                    </div>
                  )}
                  
                  {application.rental_duration && (
                    <div>
                      <Label className="font-medium">Rental Duration</Label>
                      <p className="text-gray-700">{application.rental_duration}</p>
                    </div>
                  )}
                </div>
                
                {application.reason_for_moving && (
                  <div>
                    <Label className="font-medium">Reason for Moving</Label>
                    <p className="text-gray-700">{application.reason_for_moving}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="h-5 w-5" />
                  <span>Uploaded Documents</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { key: 'id_document_path', label: 'ID Document', required: true },
                    { key: 'income_proof_path', label: 'Income Proof', required: true },
                    { key: 'employment_letter_path', label: 'Employment Letter', required: false },
                    { key: 'bank_statement_path', label: 'Bank Statement', required: false },
                    { key: 'reference_letter_path', label: 'Reference Letter', required: false }
                  ].map(({ key, label, required }) => (
                    <div key={key} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <FileText className="h-4 w-4" />
                          <span className="font-medium">{label}</span>
                          {required && <span className="text-red-500">*</span>}
                        </div>
                        {application[key] ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                      
                      {application[key] ? (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Document uploaded</span>
                          <Button size="sm" variant="outline">
                            <Download className="h-3 w-3 mr-1" />
                            Download
                          </Button>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">
                          {required ? 'Required document missing' : 'Not provided'}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          
          {application.status === 'pending' && (
            <>
              <Button
                variant="destructive"
                onClick={() => handleStatusUpdate('rejected')}
                disabled={isUpdating}
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
              
              <Button
                onClick={() => handleStatusUpdate('approved')}
                disabled={isUpdating}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ApplicationDetailsModal;

