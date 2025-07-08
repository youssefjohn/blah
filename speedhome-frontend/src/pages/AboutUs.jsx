import React from 'react';

const AboutUs = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-16">
        <div className="text-center mb-8 sm:mb-12">
          <h1 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-2 sm:mb-4">About SPEEDHOME</h1>
          <p className="text-lg sm:text-xl text-gray-600">Revolutionizing the property rental experience in Malaysia</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6 sm:p-8 mb-8">
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900">Our Mission</h2>
          <p className="text-gray-700 mb-6 leading-relaxed">
            At SPEEDHOME, our mission is to create a transparent, efficient, and secure property rental marketplace that benefits both landlords and tenants. We're committed to eliminating unnecessary costs, reducing friction in the rental process, and providing innovative solutions that address the real challenges faced by property owners and renters in Malaysia.
          </p>
          
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900">Our Story</h2>
          <p className="text-gray-700 mb-6 leading-relaxed">
            Founded in 2015, SPEEDHOME began with a simple observation: the traditional property rental process was filled with inefficiencies, high costs, and unnecessary complications. Our founders experienced these challenges firsthand and decided to create a solution that would transform the rental landscape in Malaysia.
          </p>
          <p className="text-gray-700 mb-6 leading-relaxed">
            What started as a small startup has now grown into one of Malaysia's leading property rental platforms, connecting thousands of landlords and tenants every month. Our journey has been driven by continuous innovation and a deep understanding of the local property market.
          </p>
          
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900">What Makes Us Different</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Zero Deposit Option</h3>
              <p className="text-gray-700">
                We pioneered the zero deposit rental model in Malaysia, allowing tenants to move in without paying hefty security deposits while still protecting landlords' interests.
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Zero Commission</h3>
              <p className="text-gray-700">
                Unlike traditional agencies, we don't charge landlords any commission, making it more affordable to list and rent out properties.
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Tenant Screening</h3>
              <p className="text-gray-700">
                Our comprehensive tenant screening process helps landlords find reliable tenants while making the application process smooth for qualified renters.
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 text-gray-900">Insurance Protection</h3>
              <p className="text-gray-700">
                We offer innovative insurance solutions that protect both landlords and tenants throughout the rental period.
              </p>
            </div>
          </div>
          
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900">Our Team</h2>
          <p className="text-gray-700 mb-6 leading-relaxed">
            SPEEDHOME is powered by a diverse team of professionals passionate about real estate, technology, and customer service. Our team combines local market expertise with technological innovation to create solutions that truly address the needs of the Malaysian rental market.
          </p>
          <p className="text-gray-700 mb-6 leading-relaxed">
            From our customer support specialists who assist users daily to our tech developers who continuously improve our platform, everyone at SPEEDHOME is committed to our mission of transforming property rentals.
          </p>
          
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900">Our Impact</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-gray-700">Properties Listed</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-blue-600 mb-2">50,000+</div>
              <div className="text-gray-700">Happy Users</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-blue-600 mb-2">RM 5M+</div>
              <div className="text-gray-700">Saved in Deposits</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-blue-600 mb-2">95%</div>
              <div className="text-gray-700">Satisfaction Rate</div>
            </div>
          </div>
          
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900">Looking Forward</h2>
          <p className="text-gray-700 leading-relaxed">
            As we continue to grow, our focus remains on innovation and improvement. We're constantly exploring new technologies and services that can make property rentals even more efficient, secure, and accessible for all Malaysians.
          </p>
          <p className="text-gray-700 leading-relaxed mt-4">
            Whether you're a landlord looking to list your property or a tenant searching for your next home, SPEEDHOME is committed to providing you with the best possible experience.
          </p>
        </div>
        
        <div className="text-center">
          <p className="text-gray-600 mb-4">Have questions about SPEEDHOME?</p>
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg">Contact Us</button>
        </div>
      </div>
    </div>
  );
};

export default AboutUs;
