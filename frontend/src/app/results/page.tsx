'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import ModuleCard from '@/components/ModuleCard';
import { Printer, Home, BookOpen, HelpCircle, FileText, Clock,Play, CheckCircle, Bookmark, Brain, ArrowLeft } from 'lucide-react';

interface Module {
  id: string;
  title: string;
  content: string;
  questions: Array<{
    id: string;
    question: string;
    type: 'multiple-choice' | 'short-answer' | 'essay';
    difficulty: 'easy' | 'medium' | 'hard';
    options?: string[];
  }>;
}

export default function ResultsPage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [completedModules, setCompletedModules] = useState<Set<string>>(new Set());
  const [bookmarkedModules, setBookmarkedModules] = useState<Set<string>>(new Set());
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get('sessionId');

  useEffect(() => {
    const fetchResults = async () => {
      if (!sessionId) {
        router.push('/');
        return;
      }

      try {
        const response = await fetch(`http://localhost:5001/api/results?session_id=${sessionId}`);
        const data = await response.json();
        
        if (data.success && data.modules) {
          setModules(data.modules);
          setSelectedModule(data.modules[0]?.id || '');
        } else {
          setError(data.error || 'Failed to load results');
        }
      } catch (error) {
        console.error('Failed to fetch results:', error);
        setError('Network error. Please check if the backend server is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId, router]);

  const toggleBookmark = (moduleId: string) => {
    setBookmarkedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  const markAsCompleted = (moduleId: string) => {
    setCompletedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#ECEEDF] via-white to-[#BBDCE5]/30 flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="w-20 h-20 bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] rounded-2xl flex items-center justify-center mx-auto animate-pulse">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Loading Modules</h2>
            <p className="text-[#BBDCE5] font-medium">Preparing your content...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#ECEEDF] via-white to-[#BBDCE5]/30 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center border border-[#D9C4B0]/30">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4 mx-auto">
            <span className="text-2xl">⚠️</span>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Something went wrong</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="flex items-center justify-center w-full px-6 py-3 bg-[#BBDCE5] text-white font-semibold rounded-lg hover:bg-[#a5cfd8] transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Try Again
          </button>
        </div>
      </div>
    );
  }
  const currentModule = modules.find(m => m.id === selectedModule);
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#ECEEDF] via-white to-[#BBDCE5]/30">
      {/* Top Action Bar */}
      <div className="bg-white/80 backdrop-blur-xl border-b border-[#D9C4B0]/30 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
             <div className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center shadow-md">
              <span className="text-xl font-bold text-gray-800">E</span>
            </div>
              <h1 className="text-lg font-semibold text-gray-800 tracking-wide">EduModule</h1>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push('/')}
                className="flex items-center px-4 py-2 text-gray-600 hover:text-[#6b8288] rounded-lg transition-colors border border-[#D9C4B0]/30 hover:border-[#71a9b8]"
              >
                <Home className="w-4 h-4 mr-2" />
                New Upload 
              </button>
              <button
                onClick={() => window.print()}
                className="flex items-center px-4 py-2 bg-[#5da8bd] text-white rounded-lg hover:bg-[#91bcc6] transition-colors"
              >
                <Printer className="w-4 h-4 mr-2" />
                Print
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-12 gap-8">
          {/* Left Sidebar - Module List */}
          <aside className="lg:col-span-5">
            <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 sticky top-24">
              {/* Module List Header */}
              <div className="p-6 border-b border-[#D9C4B0]/30 bg-gradient-to-r from-[#ECEEDF]/50 to-[#BBDCE5]/20">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-xl font-bold text-gray-900">Modules</h2>
                  <span className="px-3 py-1 bg-[#BBDCE5] text-white text-sm font-semibold rounded-full">
                    {modules.length}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">Select a module to view content</p>
              </div>

              {/* Module Cards */}
              <div className="p-4 space-y-3 max-h-[calc(100vh-8rem)] overflow-y-auto">
                {modules.map((module, index) => (
                  <ModuleCard
                    key={module.id}
                    module={module}
                    isSelected={selectedModule === module.id}
                    onClick={() => setSelectedModule(module.id)}
                    index={index}
                    isCompleted={completedModules.has(module.id)}
                    isBookmarked={bookmarkedModules.has(module.id)}
                    onBookmark={() => toggleBookmark(module.id)}
                    onComplete={() => markAsCompleted(module.id)}
                  />
                ))}
              </div>
            </div>
          </aside>

          {/* Right Content Area */}
          <section className="lg:col-span-7">
            {currentModule ? (
              <div className="space-y-6">
                {/* Module Header */}
                <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 p-8">
                  <div className="flex items-start space-x-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-[#4f8493] to-[#b8a18c] rounded-xl flex items-center justify-center">
                      <FileText className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <h3 className="text-3xl font-bold text-gray-900">{currentModule.title}</h3>
                        {completedModules.has(currentModule.id) && (
                          <span className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Completed
                          </span>
                        )}
                      </div>
                      
                      {/* Module Meta Info */}
                      <div className="flex items-center space-x-4 text-sm mb-4">
                        {currentModule.questions && currentModule.questions.length > 0 && (
                          <span className="flex items-center px-3 py-1 bg-[#BBDCE5]/20 text-[#BBDCE5] rounded-full font-medium border border-[#BBDCE5]/30">
                            <HelpCircle className="w-4 h-4 mr-1" />
                            {currentModule.questions.length} Questions
                          </span>
                        )}
                        <span className="flex items-center px-3 py-1 bg-[#D9C4B0]/20 text-[#CFAB8D] rounded-full font-medium border border-[#D9C4B0]/30">
                          <Clock className="w-4 h-4 mr-1" />
                          {Math.ceil(currentModule.content.split(' ').length / 200)} min read
                        </span>
                      </div>
          
                      <div className="flex items-center space-x-3">
                        {currentModule.questions && currentModule.questions.length > 0 && (
                          <button
                            onClick={() => router.push(`/quiz?moduleId=${currentModule.id}`)}
                            className="flex items-center px-4 py-2 bg-[#BBDCE5] text-white rounded-lg hover:bg-[#a5cfd8] transition-colors font-medium"
                          >
                            <Play className="w-4 h-4 mr-2" />
                            Start Quiz
                          </button>
                        )}
                        <button
                          onClick={() => markAsCompleted(currentModule.id)}
                          className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors border ${
                            completedModules.has(currentModule.id)
                              ? 'bg-green-100 text-green-700 border-green-200'
                              : 'bg-[#ECEEDF] text-gray-700 hover:bg-green-100 hover:text-green-700 border-[#D9C4B0]/30 hover:border-green-200'
                          }`}
                        >
                          <CheckCircle className="w-4 h-4 mr-2" />
                          {completedModules.has(currentModule.id) ? 'Completed' : 'Mark Complete'}
                        </button>
                        
                        <button
                          onClick={() => toggleBookmark(currentModule.id)}
                          className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors border ${
                            bookmarkedModules.has(currentModule.id)
                              ? 'bg-yellow-100 text-yellow-700 border-yellow-200'
                              : 'bg-[#ECEEDF] text-gray-700 hover:bg-yellow-100 hover:text-yellow-700 border-[#D9C4B0]/30 hover:border-yellow-200'
                          }`}
                        >
                          <Bookmark className="w-4 h-4 mr-2" />
                          Bookmark
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Module Content */}
                <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30">
                  <div className="flex items-center space-x-3 p-6 border-b border-[#D9C4B0]/30 bg-gradient-to-r from-[#ECEEDF]/50 to-[#BBDCE5]/20">
                    <div className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center">
                      <BookOpen className="w-5 h-5 text-white" />
                    </div>
                    <h4 className="text-xl font-bold text-gray-900">Module Content</h4>
                  </div>
                  <div className="p-6">
                    <div className="bg-gradient-to-r from-[#ECEEDF]/60 to-[#BBDCE5]/20 rounded-xl p-6 border border-[#BBDCE5]/30">
                      <p className="text-gray-700 leading-relaxed text-lg">{currentModule.content}</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 p-16 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-[#ECEEDF] to-[#BBDCE5]/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <BookOpen className="w-10 h-10 text-[#CFAB8D]" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Select a Module</h3>
                <p className="text-gray-600">Choose a module from the left sidebar to view its content and questions</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}