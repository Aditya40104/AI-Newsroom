import React from 'react';
import { format } from 'date-fns';

const ArticleList = ({ 
  articles = [], 
  onEdit, 
  onDelete, 
  onView,
  onPublish,
  onUnpublish,
  isLoading = false,
  currentUser 
}) => {
  const getStatusBadge = (status) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'published':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'draft':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const truncateContent = (html, maxLength = 200) => {
    const textContent = html.replace(/<[^>]+>/g, '');
    return textContent.length > maxLength 
      ? `${textContent.substring(0, maxLength)}...` 
      : textContent;
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="h-6 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg mb-4">No articles found</div>
        <p className="text-gray-400">Start writing your first article!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {articles.map((article) => (
        <div key={article.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start mb-3">
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
                {article.title}
              </h2>
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                <span>By {article.author_name || 'Unknown Author'}</span>
                <span>•</span>
                <span>
                  {article.created_at 
                    ? format(new Date(article.created_at), 'MMM dd, yyyy')
                    : 'Unknown date'
                  }
                </span>
                {article.updated_at && article.updated_at !== article.created_at && (
                  <>
                    <span>•</span>
                    <span className="text-blue-600">
                      Updated {format(new Date(article.updated_at), 'MMM dd, yyyy')}
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 ml-4">
              <span className={getStatusBadge(article.status)}>
                {article.status}
              </span>
              {article.version > 1 && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                  v{article.version}
                </span>
              )}
            </div>
          </div>

          <div className="text-gray-700 mb-4 line-clamp-3">
            {truncateContent(article.content || '')}
          </div>

          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {article.word_count && (
                <span>{article.word_count} words</span>
              )}
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => onView(article)}
                className="px-3 py-1 text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View
              </button>
              
              {/* Publish/Unpublish buttons for editors and admins */}
              {(currentUser?.role === 'editor' || currentUser?.role === 'admin') && (
                <>
                  {article.status === 'draft' && onPublish && (
                    <button
                      onClick={() => onPublish(article)}
                      className="px-3 py-1 text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Publish
                    </button>
                  )}
                  
                  {article.status === 'published' && onUnpublish && (
                    <button
                      onClick={() => onUnpublish(article)}
                      className="px-3 py-1 text-orange-600 hover:text-orange-800 text-sm font-medium"
                    >
                      Unpublish
                    </button>
                  )}
                </>
              )}

              {(currentUser?.id === article.author_id || currentUser?.role === 'admin') && (
                <>
                  <button
                    onClick={() => onEdit(article)}
                    className="px-3 py-1 text-green-600 hover:text-green-800 text-sm font-medium"
                  >
                    Edit
                  </button>
                  
                  <button
                    onClick={() => onDelete(article)}
                    className="px-3 py-1 text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Article Tags/Categories */}
          {article.tags && article.tags.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ArticleList;