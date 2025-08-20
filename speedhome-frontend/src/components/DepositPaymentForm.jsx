import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';

// Initialize Stripe (will be loaded with publishable key from backend)
let stripePromise = null;

const DepositPaymentForm = ({ agreement, onPaymentSuccess, onPaymentError }) => {
  const [stripeKey, setStripeKey] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load Stripe publishable key from backend
    const loadStripeKey = async () => {
      try {
        const response = await fetch('/api/stripe/config', {
          credentials: 'include'
        });
        const data = await response.json();

        if (data.success) {
          setStripeKey(data.publishable_key);
          stripePromise = loadStripe(data.publishable_key);
        } else {
          console.error('Failed to load Stripe configuration');
        }
      } catch (error) {
        console.error('Error loading Stripe configuration:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStripeKey();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
        <span className="ml-2 text-gray-600">Loading payment form...</span>
      </div>
    );
  }

  if (!stripeKey) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">Payment system is currently unavailable. Please try again later.</p>
      </div>
    );
  }

  return (
    <Elements stripe={stripePromise}>
      <DepositPaymentFormContent
        agreement={agreement}
        onPaymentSuccess={onPaymentSuccess}
        onPaymentError={onPaymentError}
      />
    </Elements>
  );
};

const DepositPaymentFormContent = ({ agreement, onPaymentSuccess, onPaymentError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);
  const [paymentIntent, setPaymentIntent] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Create payment intent for deposit payment
    const createDepositPaymentIntent = async () => {
      try {
        const response = await fetch(`/api/deposit-payment/initiate/${agreement.id}`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const result = await response.json();

        if (result.success) {
          setPaymentIntent(result);
        } else {
          setError(result.error || 'Failed to initialize deposit payment');
        }
      } catch (error) {
        console.error('Error creating deposit payment intent:', error);
        setError('Failed to initialize deposit payment');
      }
    };

    createDepositPaymentIntent();
  }, [agreement.id]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements || !paymentIntent) {
      return;
    }

    setProcessing(true);
    setError(null);

    const cardElement = elements.getElement(CardElement);

    try {
      const { error, paymentIntent: confirmedPaymentIntent } = await stripe.confirmCardPayment(
        paymentIntent.client_secret,
        {
          payment_method: {
            card: cardElement,
            billing_details: {
              name: agreement.tenant_full_name,
              email: agreement.tenant_email,
            },
          },
        }
      );

      if (error) {
        setError(error.message);
        onPaymentError(error.message);
      } else if (confirmedPaymentIntent.status === 'succeeded') {
        // Complete the deposit payment on the backend
        const completeResponse = await fetch(`/api/deposit-payment/complete/${agreement.id}`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            payment_intent_id: confirmedPaymentIntent.id,
            payment_method: 'stripe'
          }),
        });

        const completeResult = await completeResponse.json();
        
        if (completeResult.success) {
          onPaymentSuccess(confirmedPaymentIntent);
        } else {
          setError(completeResult.error || 'Failed to complete deposit payment');
          onPaymentError(completeResult.error || 'Failed to complete deposit payment');
        }
      }
    } catch (error) {
      console.error('Deposit payment processing failed:', error);
      setError('Deposit payment processing failed');
      onPaymentError('Deposit payment processing failed');
    } finally {
      setProcessing(false);
    }
  };

  const cardElementOptions = {
    disableLink: true,
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Security Deposit Payment
        </h3>
        <p className="text-gray-600">
          Complete your security deposit payment to activate your tenancy agreement.
        </p>
      </div>

      {/* Payment Summary - Deposit Only */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-600">Property:</span>
          <span className="font-medium">{agreement.property_address}</span>
        </div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-600">Security Deposit:</span>
          <span className="font-medium">RM {agreement.security_deposit}</span>
        </div>
        <hr className="my-3" />
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-900">Total Deposit:</span>
          <span className="text-lg font-bold text-orange-600">
            RM {agreement.payment_required}
          </span>
        </div>
      </div>

      {/* Payment Form */}
      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Card Information
          </label>
          <div className="border border-gray-300 rounded-md p-3 bg-white">
            <CardElement options={cardElementOptions} />
          </div>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <div className="mb-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="terms"
              required
              className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
            />
            <label htmlFor="terms" className="ml-2 block text-sm text-gray-700">
              I agree to the{' '}
              <a href="#" className="text-orange-600 hover:text-orange-500">
                terms and conditions
              </a>{' '}
              and authorize this payment.
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={!stripe || processing || !paymentIntent}
          className={`w-full py-3 px-4 rounded-md text-white font-medium ${
            processing || !stripe || !paymentIntent
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-orange-600 hover:bg-orange-700 focus:ring-2 focus:ring-orange-500'
          }`}
        >
          {processing ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Processing Payment...
            </div>
          ) : (
            `Pay RM ${agreement.payment_required}`
          )}
        </button>
      </form>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          🔒 Your payment information is secure and encrypted
        </p>
      </div>
    </div>
  );
};

export default DepositPaymentForm;

