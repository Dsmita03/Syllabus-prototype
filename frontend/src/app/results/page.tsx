'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import ModuleCard from '@/components/ModuleCard';
import QuestionList from '@/components/QuestionList';
import { 
  Download, 
  Printer, 
  Home, 
  BookOpen, 
  HelpCircle,
  Sparkles,
  ArrowLeft,
  FileText,
  Grid3X3,
  List,
  Clock,
} from 'lucide-react';

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
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center space-y-8">
          <div className="relative">
            <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl flex items-center justify-center mx-auto shadow-2xl">
              <BookOpen className="w-12 h-12 text-white animate-pulse" />
            </div>
            <div className="absolute -top-1 -right-1 w-8 h-8 bg-emerald-400 rounded-full animate-bounce flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
          </div>
          <div className="space-y-4">
            <h2 className="text-4xl font-bold text-slate-900">Loading Your Modules</h2>
            <p className="text-blue-600 text-xl font-medium">Preparing your learning content...</p>
            <div className="flex items-center justify-center space-x-2 mt-6">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce delay-100"></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-red-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-2xl p-10 max-w-lg w-full text-center border border-red-100">
          <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mb-8 mx-auto">
            <span className="text-4xl">⚠️</span>
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Something Went Wrong</h2>
          <p className="text-slate-600 text-lg mb-8 leading-relaxed">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-2xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <ArrowLeft className="w-5 h-5 mr-3" />
            Start Over
          </button>
        </div>
      </div>
    );
  }

  const currentModule = modules.find(m => m.id === selectedModule);
  const totalQuestions = modules.reduce((acc, module) => acc + (module.questions?.length || 0), 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Professional Header */}
      <header className="bg-white/95 backdrop-blur-xl border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            {/* Brand Section */}
            <div className="flex items-center space-x-5">
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-slate-900">
                    Learning Modules
                  </h1>
                  <div className="flex items-center space-x-4 text-sm text-slate-500 mt-1">
                    <span className="flex items-center">
                      <span className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></span>
                      {modules.length} modules
                    </span>
                    <span>•</span>
                    <span className="flex items-center">
                      <HelpCircle className="w-4 h-4 mr-1" />
                      {totalQuestions} questions
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Action Section */}
            <div className="flex items-center space-x-4">
              {/* View Toggle */}
              <div className="flex items-center bg-slate-100 rounded-xl p-1 border border-slate-200">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-all duration-200 ${
                    viewMode === 'list' 
                      ? 'bg-white shadow-sm text-blue-600 border border-slate-200' 
                      : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="List View"
                >
                  <List className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-all duration-200 ${
                    viewMode === 'grid' 
                      ? 'bg-white shadow-sm text-blue-600 border border-slate-200' 
                      : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Grid View"
                >
                  <Grid3X3 className="w-4 h-4" />
                </button>
              </div>

              {/* Navigation Buttons */}
              <button
                onClick={() => router.push('/')}
                className="flex items-center px-4 py-2.5 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-200 border border-slate-200 hover:border-blue-200"
              >
                <Home className="w-4 h-4 mr-2" />
                New Upload
              </button>
              
              <button
                onClick={() => window.print()}
                className="flex items-center px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-all duration-200 border border-slate-200"
              >
                <Printer className="w-4 h-4 mr-2" />
                Print
              </button>
              
              <button className="flex items-center px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 transform hover:scale-105 shadow-lg">
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-12 gap-8">
          {/* Modules Sidebar */}
          <aside className="lg:col-span-4">
            <div className="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden sticky top-24">
              {/* Sidebar Header */}
              <div className="px-6 py-5 bg-gradient-to-r from-slate-50 to-blue-50 border-b border-slate-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-slate-900">Course Modules</h2>
                  <div className="flex items-center space-x-3">
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-semibold rounded-full">
                      {modules.length}
                    </span>
                  </div>
                </div>
                <p className="text-slate-500 text-sm mt-1">Select a module to explore</p>
              </div>
              
              {/* Module List */}
              <div className="p-4">
                <div className="space-y-3 max-h-[calc(100vh-16rem)] overflow-y-auto">
                  {modules.map((module, index) => (
                    <div key={module.id} className="w-full">
                      <ModuleCard
                        module={module}
                        isSelected={selectedModule === module.id}
                        onClick={() => setSelectedModule(module.id)}
                        index={index}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content Area */}
          <section className="lg:col-span-8">
            {currentModule ? (
              <div className="space-y-8">
                {/* Module Header Card */}
                <div className="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
                  <div className="p-8">
                    <div className="flex items-start space-x-6">
                      <div className="flex-shrink-0">
                        <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                          <FileText className="w-10 h-10 text-white" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-4xl font-bold text-slate-900 mb-3 leading-tight">
                          {currentModule.title}
                        </h3>
                        <div className="flex flex-wrap items-center gap-4 text-sm">
                          <span className="flex items-center px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg font-medium">
                            <FileText className="w-4 h-4 mr-2" />
                            Module Content
                          </span>
                          <span className="flex items-center px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg font-medium">
                            <HelpCircle className="w-4 h-4 mr-2" />
                            {currentModule.questions?.length || 0} Questions
                          </span>
                          <span className="flex items-center px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg font-medium">
                            <Clock className="w-4 h-4 mr-2" />
                            {Math.ceil(currentModule.content.split(' ').length / 200)} min read
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Module Content */}
                <div className="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
                  <div className="px-8 py-6 bg-gradient-to-r from-slate-50 to-blue-50 border-b border-slate-200">
                    <h4 className="text-2xl font-bold text-slate-900">Module Content</h4>
                    <p className="text-slate-600 mt-1">Comprehensive learning material for this module</p>
                  </div>
                  <div className="p-8">
                    <div className="prose prose-slate prose-lg max-w-none">
                      <div className="text-slate-700 leading-relaxed text-lg bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-2xl border border-blue-100">
                        {currentModule.content}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Questions Section */}
                {currentModule.questions && currentModule.questions.length > 0 && (
                  <div className="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
                    <div className="px-8 py-6 bg-gradient-to-r from-slate-50 to-indigo-50 border-b border-slate-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                            <HelpCircle className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h4 className="text-2xl font-bold text-slate-900">Practice Questions</h4>
                            <p className="text-slate-600">Test your understanding of this module</p>
                          </div>
                        </div>
                        <span className="px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 font-bold rounded-xl">
                          {currentModule.questions.length} Questions
                        </span>
                      </div>
                    </div>
                    <div className="p-8">
                      <QuestionList questions={currentModule.questions} />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-3xl shadow-lg border border-slate-200 p-16 text-center">
                <div className="w-32 h-32 bg-gradient-to-br from-slate-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-8">
                  <BookOpen className="w-16 h-16 text-slate-400" />
                </div>
                <h3 className="text-3xl font-bold text-slate-900 mb-4">
                  Select a Module to Begin
                </h3>
                <p className="text-slate-500 text-lg leading-relaxed max-w-md mx-auto">
                  Choose any module from the sidebar to explore its content and practice questions
                </p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
