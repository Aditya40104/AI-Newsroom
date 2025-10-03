import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ArticleEditor from '../components/ArticleEditor';
import { articleAPI } from '../services/api';
import toast from 'react-hot-toast';

const ArticleEditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [article, setArticle] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingArticle, setIsLoadingArticle] = useState(!!id);

  // Load existing article if editing
  useEffect(() => {
    if (id) {
      loadArticle();
    }
  }, [id]);

  const loadArticle = async () => {
    try {
      setIsLoadingArticle(true);
      const response = await articleAPI.getArticle(id);
      setArticle(response.data);
    } catch (error) {
      toast.error('Failed to load article');
      console.error('Load article error:', error);
      navigate('/articles');
    } finally {
      setIsLoadingArticle(false);
    }
  };

  const handleSave = async (articleData) => {
    try {
      setIsLoading(true);
      
      if (articleData.id) {
        // Update existing article
        const response = await articleAPI.updateArticle(articleData.id, articleData);
        setArticle(response.data);
        toast.success('Article saved successfully!');
      } else {
        // Create new article
        const response = await articleAPI.createArticle(articleData);
        setArticle(response.data);
        toast.success('Article created successfully!');
        // Update URL to include the new article ID
        navigate(`/articles/edit/${response.data.id}`, { replace: true });
      }
    } catch (error) {
      toast.error('Failed to save article');
      console.error('Save article error:', error);
      throw error; // Re-throw to let editor handle the error state
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublish = async (articleData) => {
    try {
      setIsLoading(true);
      
      if (articleData.id) {
        // Update and publish existing article
        const response = await articleAPI.updateArticle(articleData.id, {
          ...articleData,
          status: 'published'
        });
        setArticle(response.data);
        toast.success('Article published successfully!');
        // Navigate to article view
        setTimeout(() => {
          navigate(`/articles/${response.data.id}`);
        }, 1500);
      } else {
        // Create and publish new article
        const response = await articleAPI.createArticle({
          ...articleData,
          status: 'published'
        });
        setArticle(response.data);
        toast.success('Article published successfully!');
        setTimeout(() => {
          navigate(`/articles/${response.data.id}`);
        }, 1500);
      }
    } catch (error) {
      toast.error('Failed to publish article');
      console.error('Publish article error:', error);
      throw error; // Re-throw to let editor handle the error state
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoadingArticle) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-4">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
            <div className="h-64 bg-gray-200 rounded mb-4"></div>
            <div className="flex gap-4">
              <div className="h-10 bg-gray-200 rounded w-24"></div>
              <div className="h-10 bg-gray-200 rounded w-24"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {article ? 'Edit Article' : 'Create New Article'}
              </h1>
              <p className="text-gray-600 mt-1">
                {article ? `Last saved: ${new Date(article.updated_at).toLocaleString()}` : 'Start writing your story'}
              </p>
            </div>
            
            <button
              onClick={() => navigate('/articles')}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
            >
              ← Back to Articles
            </button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="py-8">
        <ArticleEditor
          initialContent={article?.content || ''}
          initialTitle={article?.title || ''}
          articleId={article?.id || null}
          onSave={handleSave}
          onPublish={handlePublish}
          isLoading={isLoading}
        />
      </div>

      {/* Article Version History (if editing existing article) */}
      {article && article.version > 1 && (
        <div className="max-w-4xl mx-auto px-6 pb-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Version History</h3>
            <p className="text-blue-800 text-sm">
              This article is currently at version {article.version}. 
              Previous versions are automatically saved when you make changes.
            </p>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-2">
              View Version History →
            </button>
          </div>
        </div>
      )}

      {/* Writing Tips Sidebar */}
      <div className="fixed right-4 top-1/2 transform -translate-y-1/2 w-64 bg-white rounded-lg shadow-lg p-4 hidden xl:block">
        <h3 className="font-semibold text-gray-900 mb-3">Writing Tips</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li>• Use headings to structure your content</li>
          <li>• Add images to make your article engaging</li>
          <li>• Keep paragraphs short for better readability</li>
          <li>• Include quotes and links for credibility</li>
          <li>• Save drafts frequently as you work</li>
        </ul>
        
        <div className="mt-4 pt-3 border-t">
          <p className="text-xs text-gray-500">
            Auto-save: Every 30 seconds when typing
          </p>
        </div>
      </div>
    </div>
  );
};

export default ArticleEditorPage;