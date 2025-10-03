import React from 'react';
import { useAuth } from '../context/AuthContext';

const AdminPage = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Manage users, content, and system settings.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-blue-600 text-xl">👥</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-semibold text-gray-900">1,234</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">📝</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Articles</p>
              <p className="text-2xl font-semibold text-gray-900">5,678</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-purple-600 text-xl">🤖</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">AI Requests</p>
              <p className="text-2xl font-semibold text-gray-900">12,345</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Fact Checks</p>
              <p className="text-2xl font-semibold text-gray-900">2,468</p>
            </div>
          </div>
        </div>
      </div>

      {/* Management Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* User Management */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">User Management</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <button className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">Manage Users</h3>
                    <p className="text-sm text-gray-600">View, edit, and manage user accounts</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </button>

              <button className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">Role Assignments</h3>
                    <p className="text-sm text-gray-600">Assign writer, editor, and admin roles</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </button>

              <button className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">Activity Logs</h3>
                    <p className="text-sm text-gray-600">Monitor user activity and sessions</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Content Management */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Content Management</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <button className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">Article Review</h3>
                    <p className="text-sm text-gray-600">Review and approve pending articles</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </button>

              <button className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">Content Analytics</h3>
                    <p className="text-sm text-gray-600">View performance metrics and insights</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </button>

              <button className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">AI Usage Stats</h3>
                    <p className="text-sm text-gray-600">Monitor AI service usage and costs</p>
                  </div>
                  <span className="text-gray-400">→</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* System Settings */}
      <div className="mt-8 bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">System Settings</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left">
              <h3 className="font-medium text-gray-900 mb-1">API Configuration</h3>
              <p className="text-sm text-gray-600">Manage AI service APIs and keys</p>
            </button>

            <button className="p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left">
              <h3 className="font-medium text-gray-900 mb-1">OAuth Settings</h3>
              <p className="text-sm text-gray-600">Configure Google and GitHub OAuth</p>
            </button>

            <button className="p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left">
              <h3 className="font-medium text-gray-900 mb-1">Fact-Check Sources</h3>
              <p className="text-sm text-gray-600">Manage trusted news sources</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;