import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { articleAPI } from '../services/api';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

const ArticleViewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [article, setArticle] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadArticle();
  }, [id]);

  const loadArticle = async () => {
    try {
      setIsLoading(true);
      const response = await articleAPI.getArticle(id);
      setArticle(response.data);
    } catch (error) {
      toast.error('Failed to load article');
      console.error('Load article error:', error);
      navigate('/articles');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    navigate(`/articles/edit/${article.id}`);
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${article.title}"?`)) {
      return;
    }

    try {
      await articleAPI.deleteArticle(article.id);
      toast.success('Article deleted successfully');
      navigate('/articles');
    } catch (error) {
      toast.error('Failed to delete article');
      console.error('Delete article error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-4">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-6 bg-gray-200 rounded mb-6 w-1/3"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Article not found</h2>
          <button
            onClick={() => navigate('/articles')}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Articles
          </button>
        </div>
      </div>
    );
  }

  const canEdit = user?.id === article.author_id || user?.role === 'admin';
  const getStatusBadge = (status) => {
    const baseClasses = "px-3 py-1 rounded-full text-sm font-medium";
    switch (status) {
      case 'published':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'draft':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex justify-between items-start">
            <div>
              <button
                onClick={() => navigate('/articles')}
                className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
              >
                ← Back to Articles
              </button>
              
              <div className="flex items-center gap-3 mb-2">
                <span className={getStatusBadge(article.status)}>
                  {article.status}
                </span>
                {article.version > 1 && (
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    Version {article.version}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>By {article.author_name || 'Unknown Author'}</span>
                <span>•</span>
                <span>
                  {format(new Date(article.created_at), 'MMMM dd, yyyy')}
                </span>
                {article.updated_at && article.updated_at !== article.created_at && (
                  <>
                    <span>•</span>
                    <span>Updated {format(new Date(article.updated_at), 'MMMM dd, yyyy')}</span>
                  </>
                )}
              </div>
            </div>

            {canEdit && (
              <div className="flex gap-2">
                <button
                  onClick={handleEdit}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <article className="bg-white rounded-lg shadow-sm p-8">
          {/* Title */}
          <h1 className="text-4xl font-bold text-gray-900 mb-6 leading-tight">
            {article.title}
          </h1>

          {/* Article Meta */}
          <div className="border-b pb-6 mb-8">
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              {article.word_count && (
                <span>{article.word_count} words</span>
              )}
              {article.read_time && (
                <span>• {article.read_time} min read</span>
              )}
              <span>• {article.views || 0} views</span>
            </div>
          </div>

          {/* Content */}
          <div 
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />

          {/* Article Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="mt-8 pt-6 border-t">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 cursor-pointer"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </article>

        {/* Article Actions */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              <p>Published on {format(new Date(article.created_at), 'MMMM dd, yyyy')}</p>
              {article.updated_at && article.updated_at !== article.created_at && (
                <p>Last updated on {format(new Date(article.updated_at), 'MMMM dd, yyyy')}</p>
              )}
            </div>

            <div className="flex gap-4">
              <button className="text-gray-600 hover:text-gray-800">
                📤 Share
              </button>
              <button className="text-gray-600 hover:text-gray-800">
                📋 Copy Link
              </button>
              <button className="text-gray-600 hover:text-gray-800">
                🖨️ Print
              </button>
            </div>
          </div>
        </div>

        {/* Related Articles */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Articles</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Placeholder for related articles */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-600 text-sm">
                Related articles will be shown here based on tags and content similarity.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">More from this Author</h3>
              <p className="text-gray-600 text-sm">
                More articles by {article.author_name} will be displayed here.
              </p>
            </div>
          </div>
        </div>

        {/* Version History */}
        {article.version > 1 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-3">Version History</h3>
            <p className="text-blue-800 mb-4">
              This article has been updated {article.version - 1} time{article.version > 2 ? 's' : ''} 
              since its original publication.
            </p>
            <button className="text-blue-600 hover:text-blue-800 font-medium">
              View Full Version History →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArticleViewPage;