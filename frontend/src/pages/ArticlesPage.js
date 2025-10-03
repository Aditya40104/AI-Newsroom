import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ArticleList from '../components/ArticleList';
import { articleAPI } from '../services/api';
import toast from 'react-hot-toast';

const ArticlesPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [articles, setArticles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, draft, published, mine
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadArticles();
  }, [filter]);

  const loadArticles = async () => {
    try {
      setIsLoading(true);
      const params = {};
      
      if (filter === 'draft') params.status = 'draft';
      if (filter === 'published') params.status = 'published';
      if (filter === 'mine') params.author_id = user.id;
      if (searchQuery) params.search = searchQuery;

      const response = await articleAPI.getArticles(params);
      setArticles(response.data || []);
    } catch (error) {
      toast.error('Failed to load articles');
      console.error('Load articles error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (article) => {
    navigate(`/articles/edit/${article.id}`);
  };

  const handleView = (article) => {
    navigate(`/articles/${article.id}`);
  };

  const handleDelete = async (article) => {
    if (!window.confirm(`Are you sure you want to delete "${article.title}"?`)) {
      return;
    }

    try {
      await articleAPI.deleteArticle(article.id);
      setArticles(articles.filter(a => a.id !== article.id));
      toast.success('Article deleted successfully');
    } catch (error) {
      toast.error('Failed to delete article');
      console.error('Delete article error:', error);
    }
  };

  const handlePublish = async (article) => {
    try {
      const response = await fetch(`http://localhost:8000/api/articles/${article.id}/publish`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to publish article');
      }

      const updatedArticle = await response.json();
      setArticles(articles.map(a => a.id === article.id ? updatedArticle : a));
      toast.success('Article published successfully!');
    } catch (error) {
      toast.error('Failed to publish article');
      console.error('Publish error:', error);
    }
  };

  const handleUnpublish = async (article) => {
    try {
      const response = await fetch(`http://localhost:8000/api/articles/${article.id}/unpublish`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to unpublish article');
      }

      const updatedArticle = await response.json();
      setArticles(articles.map(a => a.id === article.id ? updatedArticle : a));
      toast.success('Article unpublished successfully!');
    } catch (error) {
      toast.error('Failed to unpublish article');
      console.error('Unpublish error:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadArticles();
  };

  const filteredArticles = articles.filter(article => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return article.title.toLowerCase().includes(query) ||
           article.content.toLowerCase().includes(query) ||
           (article.author_name && article.author_name.toLowerCase().includes(query));
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Articles</h1>
              <p className="text-gray-600 mt-1">Manage and create your articles</p>
            </div>
            
            <button
              onClick={() => navigate('/articles/new')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2"
            >
              <span>+</span>
              New Article
            </button>
          </div>

          {/* Filters and Search */}
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            {/* Filter Tabs */}
            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
              {[
                { key: 'all', label: 'All Articles' },
                { key: 'published', label: 'Published' },
                { key: 'draft', label: 'Drafts' },
                { key: 'mine', label: 'My Articles' }
              ].map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filter === key
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Search */}
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search articles..."
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Search
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-600">
                {articles.filter(a => a.status === 'published').length} Published
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-gray-600">
                {articles.filter(a => a.status === 'draft').length} Drafts
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-gray-600">
                {articles.filter(a => a.author_id === user?.id).length} Your Articles
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Articles List */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <ArticleList
          articles={filteredArticles}
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
          onPublish={handlePublish}
          onUnpublish={handleUnpublish}
          isLoading={isLoading}
          currentUser={user}
        />
      </div>

      {/* Empty State */}
      {!isLoading && filteredArticles.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-4">
            {searchQuery ? 'No articles found matching your search' : 'No articles yet'}
          </div>
          {!searchQuery && (
            <button
              onClick={() => navigate('/articles/new')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium"
            >
              Write Your First Article
            </button>
          )}
        </div>
      )}

      {/* Quick Stats Footer */}
      <div className="bg-white border-t mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div>
              Showing {filteredArticles.length} of {articles.length} articles
            </div>
            <div className="flex gap-4">
              <span>Total Words: {articles.reduce((sum, a) => sum + (a.word_count || 0), 0)}</span>
              <span>Authors: {new Set(articles.map(a => a.author_id)).size}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticlesPage;