import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              AI-Powered
              <span className="text-primary-600"> Newsroom</span>
              <br />
              Collaboration
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
              Transform your journalism workflow with AI-assisted writing, real-time collaboration, 
              automated fact-checking, and intelligent research tools. Built for modern newsrooms.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              {!isAuthenticated ? (
                <>
                  <Link
                    to="/login"
                    className="bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 rounded-md transition-colors"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="#features"
                    className="text-sm font-semibold leading-6 text-gray-900 hover:text-primary-600 transition-colors"
                  >
                    Learn more <span aria-hidden="true">→</span>
                  </Link>
                </>
              ) : (
                <Link
                  to="/dashboard"
                  className="bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 rounded-md transition-colors"
                >
                  Go to Dashboard
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need for modern journalism
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Streamline your content creation process with AI-powered tools and collaborative features.
            </p>
          </div>

          <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* AI Writing Assistant */}
            <div className="relative p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-primary-600 font-bold text-xl">✍️</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI Writing Assistant
              </h3>
              <p className="text-gray-600">
                Generate article drafts, headlines, and content suggestions using advanced AI models like GPT-4.
              </p>
            </div>

            {/* Real-time Collaboration */}
            <div className="relative p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-primary-600 font-bold text-xl">👥</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Real-time Collaboration
              </h3>
              <p className="text-gray-600">
                Work together with your team on articles with live editing, comments, and review workflows.
              </p>
            </div>

            {/* Fact Checking */}
            <div className="relative p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-primary-600 font-bold text-xl">✅</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Automated Fact-Checking
              </h3>
              <p className="text-gray-600">
                Verify claims and sources automatically with integrated fact-checking and citation management.
              </p>
            </div>

            {/* Smart Research */}
            <div className="relative p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-primary-600 font-bold text-xl">🔍</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Smart Research Tools
              </h3>
              <p className="text-gray-600">
                AI-powered research agents gather sources, verify credibility, and organize information.
              </p>
            </div>

            {/* Image Generation */}
            <div className="relative p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-primary-600 font-bold text-xl">🎨</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI Image Generation
              </h3>
              <p className="text-gray-600">
                Create compelling visuals and illustrations for your articles with AI-generated images.
              </p>
            </div>

            {/* Editorial Workflow */}
            <div className="relative p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-primary-600 font-bold text-xl">📋</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Editorial Workflow
              </h3>
              <p className="text-gray-600">
                Manage article versions, approval processes, and publication schedules seamlessly.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to revolutionize your newsroom?
            </h2>
            <p className="mt-4 text-lg text-primary-100">
              Join the future of journalism with AI-powered collaboration tools.
            </p>
            {!isAuthenticated && (
              <div className="mt-8">
                <Link
                  to="/login"
                  className="bg-white px-6 py-3 text-sm font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white rounded-md transition-colors"
                >
                  Start Your Free Trial
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;