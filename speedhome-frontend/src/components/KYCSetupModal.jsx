import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { CheckCircle, Clock, AlertCircle, CreditCard, Shield, Banknote } from 'lucide-react';

const KYCSetupModal = ({ isOpen, onClose, setupData, onStartKYC }) => {
  const [isStarting, setIsStarting] = useState(false);

  const handleStartKYC = async () => {
    setIsStarting(true);
    try {
      await onStartKYC();
    } finally {
      setIsStarting(false);
    }
  };

  if (!setupData || !setupData.setupRequired) {
    return null;
  }

  const steps = [
    {
      icon: <Shield className="h-5 w-5" />,
      title: "Identity Verification",
      description: "Verify your identity with official documents",
      time: "2 minutes"
    },
    {
      icon: <CreditCard className="h-5 w-5" />,
      title: "Bank Details",
      description: "Add your Malaysian bank account for deposits",
      time: "1 minute"
    },
    {
      icon: <Banknote className="h-5 w-5" />,
      title: "Start Earning",
      description: "Receive deposits securely from tenants",
      time: "Immediate"
    }
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CreditCard className="h-5 w-5 text-blue-600" />
            </div>
            Complete Your Payment Setup
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-blue-900">
                Welcome to SpeedHome! 🎉
              </CardTitle>
              <CardDescription className="text-blue-700">
                {setupData.setupMessage}
              </CardDescription>
            </CardHeader>
          </Card>

          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">Quick Setup Process:</h3>
            {steps.map((step, index) => (
              <div key={index} className="flex items-start gap-3 p-3 border rounded-lg bg-gray-50">
                <div className="p-1.5 bg-white rounded-full border">
                  {step.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{step.title}</h4>
                    <Badge variant="secondary" className="text-xs">
                      {step.time}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="border-l-4 border-green-400 bg-green-50 p-4 rounded">
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-400 mt-0.5" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">
                  Secure & Trusted
                </h3>
                <p className="text-sm text-green-700 mt-1">
                  Your information is protected by bank-level security. Setup takes just 3 minutes.
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Set Up Later
            </Button>
            <Button
              onClick={handleStartKYC}
              disabled={isStarting}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              {isStarting ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                'Start Setup'
              )}
            </Button>
          </div>

          <p className="text-xs text-gray-500 text-center">
            Complete setup now to start receiving deposits from tenants immediately
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default KYCSetupModal;