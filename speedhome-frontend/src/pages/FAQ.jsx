import React, { useState } from 'react';

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const faqs = [
    {
      question: "What is SPEEDHOME?",
      answer: "SPEEDHOME is a property rental platform that connects landlords and tenants directly without agent fees. We offer innovative solutions like zero deposit options, tenant screening, and insurance protection to make renting easier and more secure for everyone."
    },
    {
      question: "How does the Zero Deposit option work?",
      answer: "Our Zero Deposit option allows tenants to rent a property without paying the traditional security deposit (typically 2-3 months' rent). Instead, tenants pay a small fee for insurance coverage that protects the landlord against damages or unpaid rent. This makes moving more affordable while still providing landlords with protection."
    },
    {
      question: "Is there any commission fee for landlords?",
      answer: "No, SPEEDHOME does not charge any commission fees to landlords. You can list your property completely free of charge. We only earn through optional value-added services that landlords can choose to use."
    },
    {
      question: "How do I list my property on SPEEDHOME?",
      answer: "Listing your property is simple. Create an account, click on 'List Your Property', fill in the details about your property including photos and amenities, set your rental price, and publish your listing. Our team will verify your listing before it goes live to ensure quality."
    },
    {
      question: "How does tenant screening work?",
      answer: "We conduct comprehensive background checks on potential tenants, including employment verification, previous rental history, and credit assessment. This helps landlords find reliable tenants while making the application process smooth for qualified renters."
    },
    {
      question: "What areas does SPEEDHOME cover?",
      answer: "SPEEDHOME currently covers major cities and areas across Malaysia, including Kuala Lumpur, Selangor, Penang, Johor, and more. We're continuously expanding our coverage to serve more locations."
    },
    {
      question: "How do I schedule a property viewing?",
      answer: "When you find a property you're interested in, simply click the 'Schedule Viewing' button on the property page. Select your preferred date and time, provide your contact information, and submit your request. The landlord will be notified and can confirm the viewing appointment."
    },
    {
      question: "What types of properties can I find on SPEEDHOME?",
      answer: "SPEEDHOME offers a wide range of residential properties including apartments, condominiums, houses, studios, and rooms for rent. We cater to various budgets and preferences across different locations."
    },
    {
      question: "How is SPEEDHOME different from traditional property agents?",
      answer: "Unlike traditional agents who charge commission fees (typically 1 month's rent), SPEEDHOME connects landlords and tenants directly with no commission fees. We also offer innovative solutions like zero deposit options, digital contracts, and insurance protection that traditional agents typically don't provide."
    },
    {
      question: "Is my personal information secure with SPEEDHOME?",
      answer: "Yes, we take data privacy very seriously. All personal information is encrypted and stored securely. We comply with relevant data protection laws and never share your information with unauthorized third parties. You can review our Privacy Policy for more details."
    },
    {
      question: "What if there's a dispute between landlord and tenant?",
      answer: "SPEEDHOME offers mediation services to help resolve disputes between landlords and tenants. Our team will work with both parties to find a fair resolution. In cases where insurance is involved, our claims process is designed to be straightforward and efficient."
    },
    {
      question: "Can I get my deposit back if I use the traditional deposit option?",
      answer: "Yes, if you opt for the traditional security deposit option, your deposit is refundable at the end of your tenancy, subject to the condition of the property and fulfillment of the tenancy agreement terms."
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-16">
        <div className="text-center mb-8 sm:mb-12">
          <h1 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-2 sm:mb-4">Frequently Asked Questions</h1>
          <p className="text-lg sm:text-xl text-gray-600">Find answers to common questions about SPEEDHOME</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {faqs.map((faq, index) => (
            <div key={index} className="border-b border-gray-200 last:border-b-0">
              <button
                className="w-full text-left px-6 py-4 focus:outline-none"
                onClick={() => toggleFAQ(index)}
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">{faq.question}</h3>
                  <span className="ml-6 flex-shrink-0">
                    {openIndex === index ? (
                      <svg className="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                    ) : (
                      <svg className="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    )}
                  </span>
                </div>
              </button>
              {openIndex === index && (
                <div className="px-6 pb-4">
                  <p className="text-gray-700">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="text-center mt-8 sm:mt-12">
          <p className="text-gray-600 mb-4">Can't find what you're looking for?</p>
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg">Contact Our Support Team</button>
        </div>
      </div>
    </div>
  );
};

export default FAQ;
