import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-gray-600 mt-2">
          Manage your articles and collaborate with your team.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Link
          to="/editor"
          className="bg-primary-600 hover:bg-primary-700 text-white p-6 rounded-lg transition-colors group"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">✍️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium">New Article</h3>
              <p className="text-primary-100 text-sm">Start writing with AI assistance</p>
            </div>
          </div>
        </Link>

        <div className="bg-white border border-gray-200 hover:bg-gray-50 p-6 rounded-lg transition-colors">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-gray-900">Analytics</h3>
              <p className="text-gray-600 text-sm">View your article performance</p>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 hover:bg-gray-50 p-6 rounded-lg transition-colors">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">🤖</span>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-gray-900">AI Tools</h3>
              <p className="text-gray-600 text-sm">Research and fact-checking</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Articles */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Articles</h2>
        </div>
        <div className="p-6">
          <div className="text-center py-12">
            <span className="text-4xl mb-4 block">📝</span>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No articles yet</h3>
            <p className="text-gray-600 mb-4">
              Start creating your first article with AI assistance.
            </p>
            <Link
              to="/editor"
              className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Create Article
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;