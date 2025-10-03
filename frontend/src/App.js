import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import EditorPage from './pages/EditorPage';
import AdminPage from './pages/AdminPage';
import ArticlesPage from './pages/ArticlesPage';
import ArticleEditorPage from './pages/ArticleEditorPage';
import ArticleViewPage from './pages/ArticleViewPage';
import AdminDashboard from './components/AdminDashboard';
import { AuthProvider } from './context/AuthContext';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="App min-h-screen bg-gray-50">
            {/* Toast Notifications */}
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
            
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Layout><HomePage /></Layout>} />
              <Route path="/login" element={<LoginPage />} />
              
              {/* Protected routes - require authentication */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Layout><DashboardPage /></Layout>
                  </ProtectedRoute>
                } 
              />

              {/* Article routes */}
              <Route 
                path="/articles" 
                element={
                  <ProtectedRoute>
                    <Layout><ArticlesPage /></Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/articles/new" 
                element={
                  <ProtectedRoute requiredRole="writer">
                    <Layout><ArticleEditorPage /></Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/articles/edit/:id" 
                element={
                  <ProtectedRoute requiredRole="writer">
                    <Layout><ArticleEditorPage /></Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/articles/:id" 
                element={
                  <ProtectedRoute>
                    <Layout><ArticleViewPage /></Layout>
                  </ProtectedRoute>
                } 
              />

              {/* Legacy editor routes for backward compatibility */}
              <Route 
                path="/editor" 
                element={
                  <ProtectedRoute requiredRole="writer">
                    <Layout><EditorPage /></Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/editor/:id" 
                element={
                  <ProtectedRoute requiredRole="writer">
                    <Layout><EditorPage /></Layout>
                  </ProtectedRoute>
                } 
              />
              
              {/* Admin-only routes */}
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute requiredRole="admin">
                    <Layout><AdminPage /></Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin/dashboard" 
                element={
                  <ProtectedRoute requiredRole="editor">
                    <AdminDashboard />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;