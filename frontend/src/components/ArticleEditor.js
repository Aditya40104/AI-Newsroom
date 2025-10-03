import React, { useCallback, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import Highlight from '@tiptap/extension-highlight';
import CharacterCount from '@tiptap/extension-character-count';
import { toast } from 'react-hot-toast';
import axios from 'axios';

const ArticleEditor = ({ 
  initialContent = '', 
  initialTitle = '', 
  onSave, 
  onPublish, 
  articleId = null,
  isLoading = false 
}) => {
  const [title, setTitle] = useState(initialTitle);
  const [isSaving, setIsSaving] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showHeadlineModal, setShowHeadlineModal] = useState(false);
  const [showFactCheckModal, setShowFactCheckModal] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [factCheckLoading, setFactCheckLoading] = useState(false);
  const [aiTopic, setAiTopic] = useState('');
  const [aiKeywords, setAiKeywords] = useState('');
  const [aiTone, setAiTone] = useState('professional');
  const [aiLength, setAiLength] = useState('medium');
  const [suggestedHeadlines, setSuggestedHeadlines] = useState([]);
  const [factCheckResults, setFactCheckResults] = useState(null);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Image.configure({
        inline: true,
        HTMLAttributes: {
          class: 'rounded-lg max-w-full h-auto',
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 hover:text-blue-800 underline',
        },
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Underline,
      Highlight.configure({
        multicolor: true,
      }),
      CharacterCount.configure({
        limit: 10000,
      }),
    ],
    content: initialContent,
    editorProps: {
      attributes: {
        class: 'prose prose-lg max-w-none focus:outline-none min-h-[400px] p-4 border rounded-lg',
      },
    },
  });

  const addImage = useCallback(() => {
    const url = window.prompt('Enter image URL:');
    if (url) {
      editor.chain().focus().setImage({ src: url }).run();
    }
  }, [editor]);

  const addLink = useCallback(() => {
    const previousUrl = editor.getAttributes('link').href;
    const url = window.prompt('Enter URL:', previousUrl);

    if (url === null) {
      return;
    }

    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }

    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  }, [editor]);

  const handleSaveDraft = async () => {
    if (!title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    setIsSaving(true);
    try {
      const content = editor.getHTML();
      await onSave({
        id: articleId,
        title: title.trim(),
        content,
        status: 'draft'
      });
      toast.success('Draft saved successfully!');
    } catch (error) {
      toast.error('Failed to save draft');
      console.error('Save error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    if (!editor.getText().trim()) {
      toast.error('Please add some content');
      return;
    }

    setIsSaving(true);
    try {
      const content = editor.getHTML();
      await onPublish({
        id: articleId,
        title: title.trim(),
        content,
        status: 'published'
      });
      toast.success('Article published successfully!');
    } catch (error) {
      toast.error('Failed to publish article');
      console.error('Publish error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // AI Functions
  const generateArticle = async () => {
    if (!aiTopic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    setAiLoading(true);
    try {
      const keywords = aiKeywords ? aiKeywords.split(',').map(k => k.trim()).filter(k => k) : [];
      
      const response = await axios.post('http://127.0.0.1:8000/api/ai/generate_article', {
        topic: aiTopic,
        keywords: keywords,
        tone: aiTone,
        length: aiLength
      });

      const { 
        title: generatedTitle, 
        content: generatedContent, 
        suggested_images = [] 
      } = response.data;
      
      // Set the generated title and content
      setTitle(generatedTitle);
      editor.commands.setContent(generatedContent);
      
      // Auto-insert first image if available
      if (suggested_images.length > 0) {
        const firstImage = suggested_images[0];
        const imageHtml = `<div class="article-image">
          <img src="${firstImage.url}" alt="${firstImage.alt_description}" style="width: 100%; max-width: 600px; height: auto; border-radius: 8px; margin: 16px 0;" />
          <p style="font-size: 14px; color: #666; font-style: italic; margin: 8px 0;">${firstImage.caption}</p>
        </div>`;
        
        // Insert image after first paragraph
        const currentContent = editor.getHTML();
        const paragraphs = currentContent.split('</p>');
        if (paragraphs.length > 1) {
          const updatedContent = paragraphs[0] + '</p>' + imageHtml + paragraphs.slice(1).join('</p>');
          editor.commands.setContent(updatedContent);
        } else {
          editor.commands.setContent(currentContent + imageHtml);
        }
        
        toast.success(`Article with ${suggested_images.length} images generated!`);
      } else {
        toast.success('Article generated successfully!');
      }
      
      setShowAIModal(false);
      setAiTopic('');
      setAiKeywords('');
    } catch (error) {
      toast.error('Failed to generate article');
      console.error('AI Generation error:', error);
    } finally {
      setAiLoading(false);
    }
  };

  const rewriteContent = async (style = 'improve') => {
    const currentContent = editor.getText();
    
    if (!currentContent.trim()) {
      toast.error('Please add some content to rewrite');
      return;
    }

    setAiLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/ai/rewrite_content', {
        content: currentContent,
        style: style
      });

      editor.commands.setContent(response.data.rewritten_content);
      toast.success('Content rewritten successfully!');
    } catch (error) {
      toast.error('Failed to rewrite content');
      console.error('AI Rewrite error:', error);
    } finally {
      setAiLoading(false);
    }
  };

  const generateHeadlines = async () => {
    const currentContent = editor.getText();
    
    if (!currentContent.trim()) {
      toast.error('Please add some content first');
      return;
    }

    setAiLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/ai/generate_headlines', {
        content: currentContent,
        count: 5
      });

      setSuggestedHeadlines(response.data.headlines);
      setShowHeadlineModal(true);
    } catch (error) {
      toast.error('Failed to generate headlines');
      console.error('AI Headlines error:', error);
    } finally {
      setAiLoading(false);
    }
  };

  const selectHeadline = (headline) => {
    setTitle(headline);
    setShowHeadlineModal(false);
    setSuggestedHeadlines([]);
    toast.success('Headline selected!');
  };

  // Fact-checking function
  const factCheckContent = async () => {
    const currentContent = editor.getText();
    
    if (!currentContent.trim()) {
      toast.error('Please add some content to fact-check');
      return;
    }

    setFactCheckLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/fact-check/fact_check', {
        content: currentContent
      });

      setFactCheckResults(response.data);
      setShowFactCheckModal(true);
      
      if (response.data.overall_score >= 80) {
        toast.success(`Great! Credibility score: ${response.data.overall_score}%`);
      } else if (response.data.overall_score >= 60) {
        toast.warning(`Good credibility score: ${response.data.overall_score}%`);
      } else {
        toast.error(`Low credibility score: ${response.data.overall_score}%`);
      }
      
    } catch (error) {
      toast.error('Failed to fact-check content');
      console.error('Fact-check error:', error);
    } finally {
      setFactCheckLoading(false);
    }
  };

  if (!editor) {
    return <div className="text-center py-8">Loading editor...</div>;
  }

  const characterCount = editor.storage.characterCount.characters();
  const wordCount = editor.storage.characterCount.words();

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white">
      {/* Title Input */}
      <div className="mb-6">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter article title..."
          className="w-full text-3xl font-bold border-none outline-none placeholder-gray-400 focus:ring-0"
          disabled={isLoading}
        />
      </div>

      {/* Editor Toolbar */}
      <div className="border-b pb-4 mb-4">
        {/* AI Tools Section */}
        <div className="flex flex-wrap gap-2 mb-3 pb-3 border-b border-gray-200">
          <button
            onClick={() => setShowAIModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            disabled={aiLoading}
            type="button"
          >
            🤖 AI Generate Article
          </button>

          <button
            onClick={() => rewriteContent('improve')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            disabled={aiLoading}
            type="button"
          >
            ✨ AI Improve
          </button>

          <button
            onClick={() => rewriteContent('formal')}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            disabled={aiLoading}
            type="button"
          >
            📝 Formal Style
          </button>

          <button
            onClick={() => rewriteContent('casual')}
            className="px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
            disabled={aiLoading}
            type="button"
          >
            💬 Casual Style
          </button>

          <button
            onClick={generateHeadlines}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            disabled={aiLoading}
            type="button"
          >
            📰 AI Headlines
          </button>

          <button
            onClick={factCheckContent}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            disabled={factCheckLoading}
            type="button"
          >
            🔍 Fact Check
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {/* Text Formatting */}
          <button
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('bold') ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            <strong>B</strong>
          </button>
          
          <button
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('italic') ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            <em>I</em>
          </button>

          <button
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('underline') ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            <u>U</u>
          </button>

          <button
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('highlight') ? 'bg-yellow-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            ⚡
          </button>

          {/* Headings */}
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('heading', { level: 1 }) ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            H1
          </button>

          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('heading', { level: 2 }) ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            H2
          </button>

          {/* Lists */}
          <button
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('bulletList') ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            • List
          </button>

          <button
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('orderedList') ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            1. List
          </button>

          {/* Alignment */}
          <button
            onClick={() => editor.chain().focus().setTextAlign('left').run()}
            className={`px-3 py-1 rounded ${
              editor.isActive({ textAlign: 'left' }) ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            ⬅️
          </button>

          <button
            onClick={() => editor.chain().focus().setTextAlign('center').run()}
            className={`px-3 py-1 rounded ${
              editor.isActive({ textAlign: 'center' }) ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            ↔️
          </button>

          <button
            onClick={() => editor.chain().focus().setTextAlign('right').run()}
            className={`px-3 py-1 rounded ${
              editor.isActive({ textAlign: 'right' }) ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            ➡️
          </button>

          {/* Media */}
          <button
            onClick={addImage}
            className="px-3 py-1 rounded hover:bg-gray-100"
            type="button"
          >
            🖼️ Image
          </button>

          <button
            onClick={addLink}
            className={`px-3 py-1 rounded ${
              editor.isActive('link') ? 'bg-blue-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            🔗 Link
          </button>

          {/* Quote */}
          <button
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            className={`px-3 py-1 rounded ${
              editor.isActive('blockquote') ? 'bg-gray-200' : 'hover:bg-gray-100'
            }`}
            type="button"
          >
            💬 Quote
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="mb-6">
        <EditorContent 
          editor={editor} 
          className="min-h-[400px] focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-opacity-50 rounded-lg"
        />
      </div>

      {/* Status and Stats */}
      <div className="flex justify-between items-center text-sm text-gray-600 mb-6">
        <div className="flex gap-4">
          <span>{wordCount} words</span>
          <span>{characterCount} characters</span>
          {characterCount > 9000 && (
            <span className="text-red-600">
              Character limit approaching ({10000 - characterCount} remaining)
            </span>
          )}
        </div>
        <div>
          {articleId && (
            <span className="text-gray-500">
              {articleId ? 'Editing existing article' : 'New article'}
            </span>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={handleSaveDraft}
          disabled={isSaving || isLoading}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? 'Saving...' : 'Save Draft'}
        </button>
        
        <button
          onClick={handlePublish}
          disabled={isSaving || isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? 'Publishing...' : 'Publish'}
        </button>
      </div>

      {/* AI Article Generation Modal */}
      {showAIModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Generate Article with AI</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Topic *</label>
                <input
                  type="text"
                  value={aiTopic}
                  onChange={(e) => setAiTopic(e.target.value)}
                  placeholder="Enter article topic..."
                  className="w-full p-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Keywords (comma-separated)</label>
                <input
                  type="text"
                  value={aiKeywords}
                  onChange={(e) => setAiKeywords(e.target.value)}
                  placeholder="technology, innovation, trends..."
                  className="w-full p-2 border rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Tone</label>
                  <select
                    value={aiTone}
                    onChange={(e) => setAiTone(e.target.value)}
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Length</label>
                  <select
                    value={aiLength}
                    onChange={(e) => setAiLength(e.target.value)}
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="short">Short</option>
                    <option value="medium">Medium</option>
                    <option value="long">Long</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAIModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={aiLoading}
              >
                Cancel
              </button>
              <button
                onClick={generateArticle}
                disabled={aiLoading}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                {aiLoading ? 'Generating...' : 'Generate Article'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Headlines Suggestion Modal */}
      {showHeadlineModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Suggested Headlines</h3>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {suggestedHeadlines.map((headline, index) => (
                <button
                  key={index}
                  onClick={() => selectHeadline(headline)}
                  className="w-full p-3 text-left border rounded-lg hover:bg-gray-50 hover:border-blue-500"
                >
                  {headline}
                </button>
              ))}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowHeadlineModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Fact Check Results Modal */}
      {showFactCheckModal && factCheckResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Fact Check Results</h3>
            
            {/* Overall Score */}
            <div className="mb-6 p-4 rounded-lg border">
              <div className="flex items-center justify-between">
                <span className="text-lg font-semibold">Credibility Score:</span>
                <div className={`text-2xl font-bold ${
                  factCheckResults.overall_score >= 80 ? 'text-green-600' :
                  factCheckResults.overall_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {factCheckResults.overall_score}%
                </div>
              </div>
              <div className={`w-full bg-gray-200 rounded-full h-2 mt-2`}>
                <div 
                  className={`h-2 rounded-full ${
                    factCheckResults.overall_score >= 80 ? 'bg-green-600' :
                    factCheckResults.overall_score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                  }`}
                  style={{width: `${factCheckResults.overall_score}%`}}
                ></div>
              </div>
            </div>

            {/* Flagged Claims */}
            {factCheckResults.flagged_claims.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-3 text-red-600">⚠️ Flagged Claims</h4>
                <div className="space-y-3">
                  {factCheckResults.flagged_claims.map((claim, index) => (
                    <div key={index} className="p-4 border border-red-200 rounded-lg bg-red-50">
                      <p className="font-medium mb-2">"{claim.text}"</p>
                      <div className="text-sm text-gray-600">
                        <p><strong>Issues:</strong> {claim.issues.join(', ')}</p>
                        <p><strong>Confidence:</strong> {claim.confidence}%</p>
                        <p><strong>Suggestion:</strong> {claim.suggestion}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Named Entities */}
            {factCheckResults.entities.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-3">🏷️ Named Entities Found</h4>
                <div className="flex flex-wrap gap-2">
                  {factCheckResults.entities.map((entity, index) => (
                    <span 
                      key={index} 
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      title={entity.description}
                    >
                      {entity.text} ({entity.label})
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Credible Sources */}
            {factCheckResults.credible_sources.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-3 text-green-600">✅ Credible Sources</h4>
                <div className="space-y-3">
                  {factCheckResults.credible_sources.map((source, index) => (
                    <div key={index} className="p-4 border border-green-200 rounded-lg bg-green-50">
                      <h5 className="font-medium text-green-800">
                        <a href={source.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {source.title}
                        </a>
                      </h5>
                      <p className="text-sm text-gray-600 mt-1">{source.snippet}</p>
                      <p className="text-xs text-gray-500 mt-2">Source: {source.source}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowFactCheckModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticleEditor;