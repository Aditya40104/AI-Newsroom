import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const EditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState({
    title: '',
    content: '',
    summary: '',
    tags: [],
    category: ''
  });
  const [saving, setSaving] = useState(false);

  const handleTitleChange = (e) => {
    setArticle(prev => ({
      ...prev,
      title: e.target.value
    }));
  };

  const handleContentChange = (e) => {
    setArticle(prev => ({
      ...prev,
      content: e.target.value
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    // TODO: Implement save functionality
    setTimeout(() => {
      setSaving(false);
    }, 1000);
  };

  const handlePublish = async () => {
    // TODO: Implement publish functionality
    alert('Publishing feature will be implemented in the next step!');
  };

  const generateWithAI = () => {
    // TODO: Implement AI generation
    alert('AI generation will be implemented in the AI integration step!');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-xl font-semibold text-gray-900">
            {id ? 'Edit Article' : 'New Article'}
          </h1>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Draft'}
          </button>
          <button
            onClick={generateWithAI}
            className="px-4 py-2 text-sm font-medium text-purple-700 bg-purple-100 hover:bg-purple-200 rounded-md transition-colors"
          >
            🤖 AI Assist
          </button>
          <button
            onClick={handlePublish}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
          >
            Publish
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Editor */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            {/* Title */}
            <div className="p-6 border-b border-gray-200">
              <input
                type="text"
                placeholder="Enter your article title..."
                value={article.title}
                onChange={handleTitleChange}
                className="w-full text-2xl font-bold text-gray-900 placeholder-gray-400 border-none outline-none resize-none"
              />
            </div>

            {/* Content Editor */}
            <div className="p-6">
              <div className="mb-4">
                <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
                  <button className="hover:text-gray-700 font-semibold">B</button>
                  <button className="hover:text-gray-700 italic">I</button>
                  <button className="hover:text-gray-700 underline">U</button>
                  <span className="text-gray-300">|</span>
                  <button className="hover:text-gray-700">Link</button>
                  <button className="hover:text-gray-700">Image</button>
                  <button className="hover:text-gray-700">Quote</button>
                </div>
              </div>
              
              <textarea
                placeholder="Start writing your article... Use the AI Assist button for help with content generation, research, and fact-checking."
                value={article.content}
                onChange={handleContentChange}
                className="w-full h-96 text-gray-900 placeholder-gray-400 border-none outline-none resize-none text-lg leading-relaxed"
              />
            </div>
          </div>

          {/* AI Suggestions Panel (placeholder) */}
          <div className="mt-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200 p-6">
            <div className="flex items-center mb-4">
              <span className="text-purple-600 text-xl mr-2">🤖</span>
              <h3 className="text-lg font-medium text-gray-900">AI Writing Assistant</h3>
            </div>
            <div className="text-gray-600 mb-4">
              <p>Your AI writing assistant is ready to help with:</p>
              <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
                <li>Content generation and expansion</li>
                <li>Research and fact verification</li>
                <li>Citation and source management</li>
                <li>Style and tone improvements</li>
              </ul>
            </div>
            <button
              onClick={generateWithAI}
              className="text-purple-700 hover:text-purple-800 text-sm font-medium"
            >
              Get AI suggestions →
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Article Settings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Article Settings</h3>
            
            <div className="space-y-4">
              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={article.category}
                  onChange={(e) => setArticle(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm"
                >
                  <option value="">Select category</option>
                  <option value="news">News</option>
                  <option value="politics">Politics</option>
                  <option value="technology">Technology</option>
                  <option value="sports">Sports</option>
                  <option value="business">Business</option>
                </select>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags
                </label>
                <input
                  type="text"
                  placeholder="Add tags (comma separated)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>

              {/* Summary */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Summary
                </label>
                <textarea
                  placeholder="Brief article summary..."
                  value={article.summary}
                  onChange={(e) => setArticle(prev => ({ ...prev, summary: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>
            </div>
          </div>

          {/* Fact-Checking */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Fact-Check Status</h3>
            <div className="text-center py-4">
              <div className="text-yellow-500 text-2xl mb-2">⚠️</div>
              <p className="text-sm text-gray-600">
                Fact-checking will be available once you save your article.
              </p>
            </div>
          </div>

          {/* Version History */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Version History</h3>
            <div className="text-center py-4">
              <div className="text-gray-400 text-2xl mb-2">📝</div>
              <p className="text-sm text-gray-600">
                No versions saved yet.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditorPage;