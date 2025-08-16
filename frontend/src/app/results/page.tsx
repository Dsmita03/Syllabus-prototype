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
  Target,
  Trophy,
  Play,
  CheckCircle,
  Star,
  Bookmark,
  Share2,
  Brain,
  Lightbulb,
  TrendingUp,
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center space-y-8">
          <div className="relative">
            <div className="w-32 h-32 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl flex items-center justify-center mx-auto shadow-2xl animate-pulse">
              <Brain className="w-16 h-16 text-white" />
            </div>
            <div className="absolute -top-2 -right-2 w-10 h-10 bg-emerald-400 rounded-full animate-bounce flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="absolute -bottom-2 -left-2 w-8 h-8 bg-purple-400 rounded-full animate-bounce delay-150 flex items-center justify-center">
              <Lightbulb className="w-4 h-4 text-white" />
            </div>
          </div>
          <div className="space-y-4">
            <h2 className="text-5xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-indigo-800 bg-clip-text text-transparent">
              Crafting Your Learning Journey
            </h2>
            <p className="text-blue-600 text-xl font-medium">Transforming your content into engaging modules...</p>
            <div className="flex items-center justify-center space-x-3 mt-8">
              <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full animate-bounce"></div>
              <div className="w-4 h-4 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-bounce delay-100"></div>
              <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-red-50 to-pink-50 flex items-center justify-center p-6">
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-12 max-w-lg w-full text-center border border-red-100">
          <div className="w-28 h-28 bg-gradient-to-br from-red-100 to-pink-100 rounded-full flex items-center justify-center mb-8 mx-auto">
            <span className="text-5xl">⚠️</span>
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Oops! Something Went Wrong</h2>
          <p className="text-slate-600 text-lg mb-8 leading-relaxed">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white font-semibold rounded-2xl hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
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
  const completedCount = completedModules.size;
  const progressPercentage = modules.length > 0 ? (completedCount / modules.length) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Enhanced Header with Progress */}
      <header className="bg-white/95 backdrop-blur-xl border-b border-slate-200/50 sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-4">
            {/* Brand Section */}
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl">
                  <Brain className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-indigo-800 bg-clip-text text-transparent">
                     EduModule
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
                    <span>•</span>
                    <span className="flex items-center">
                      <Trophy className="w-4 h-4 mr-1" />
                      {completedCount} completed
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Action Section */}
            <div className="flex items-center space-x-4">
              {/* View Toggle */}
              <div className="flex items-center bg-slate-100/80 backdrop-blur-sm rounded-xl p-1 border border-slate-200/50">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2.5 rounded-lg transition-all duration-200 ${
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
                  className={`p-2.5 rounded-lg transition-all duration-200 ${
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
              
              <button className="flex items-center px-6 py-2.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white font-medium rounded-xl hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg">
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 transition-all duration-500 ease-out rounded-full relative"
              style={{ width: `${progressPercentage}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
            </div>
          </div>
          <div className="flex items-center justify-between mt-2 text-sm text-slate-600">
            <span>Progress: {completedCount} of {modules.length} modules completed</span>
            <span className="font-semibold">{Math.round(progressPercentage)}%</span>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-12 gap-8">
          {/* Enhanced Modules Sidebar */}
          <aside className="lg:col-span-4">
            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/50 overflow-hidden sticky top-32">
              {/* Sidebar Header */}
              <div className="px-6 py-6 bg-gradient-to-r from-slate-50 via-blue-50 to-indigo-50 border-b border-slate-200/50">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-2xl font-bold text-slate-900">Course Modules</h2>
                  <div className="flex items-center space-x-3">
                    <span className="px-4 py-2 bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 text-sm font-semibold rounded-full border border-blue-200">
                      {modules.length}
                    </span>
                  </div>
                </div>
                <p className="text-slate-600 text-sm">Select a module to explore and learn</p>
                
                {/* Quick Stats */}
                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div className="bg-white/60 rounded-xl p-3 text-center border border-slate-200/50">
                    <div className="text-2xl font-bold text-blue-600">{completedCount}</div>
                    <div className="text-xs text-slate-600">Completed</div>
                  </div>
                  <div className="bg-white/60 rounded-xl p-3 text-center border border-slate-200/50">
                    <div className="text-2xl font-bold text-indigo-600">{totalQuestions}</div>
                    <div className="text-xs text-slate-600">Questions</div>
                  </div>
                </div>
              </div>
              
              {/* Module List */}
              <div className="p-4">
                <div className="space-y-3 max-h-[calc(100vh-20rem)] overflow-y-auto">
                  {modules.map((module, index) => (
                    <div key={module.id} className="w-full">
                      <ModuleCard
                        module={module}
                        isSelected={selectedModule === module.id}
                        onClick={() => setSelectedModule(module.id)}
                        index={index}
                        isCompleted={completedModules.has(module.id)}
                        isBookmarked={bookmarkedModules.has(module.id)}
                        onBookmark={() => toggleBookmark(module.id)}
                        onComplete={() => markAsCompleted(module.id)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          {/* Enhanced Main Content Area */}
          <section className="lg:col-span-8">
            {currentModule ? (
              <div className="space-y-8">
                {/* Enhanced Module Header Card */}
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/50 overflow-hidden">
                  <div className="p-8">
                    <div className="flex items-start space-x-6">
                      <div className="flex-shrink-0">
                        <div className="w-24 h-24 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl">
                          <FileText className="w-12 h-12 text-white" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-3">
                          <h3 className="text-4xl font-bold text-slate-900 leading-tight">
                            {currentModule.title}
                          </h3>
                          {completedModules.has(currentModule.id) && (
                            <div className="flex items-center px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg font-medium">
                              <CheckCircle className="w-4 h-4 mr-2" />
                              Completed
                            </div>
                          )}
                        </div>
                        <div className="flex flex-wrap items-center gap-4 text-sm mb-4">
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
                        
                        {/* Action Buttons */}
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => markAsCompleted(currentModule.id)}
                            className={`flex items-center px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                              completedModules.has(currentModule.id)
                                ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                                : 'bg-slate-100 text-slate-700 hover:bg-emerald-100 hover:text-emerald-700 border border-slate-200 hover:border-emerald-200'
                            }`}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            {completedModules.has(currentModule.id) ? 'Completed' : 'Mark Complete'}
                          </button>
                          
                          <button
                            onClick={() => toggleBookmark(currentModule.id)}
                            className={`flex items-center px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                              bookmarkedModules.has(currentModule.id)
                                ? 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                                : 'bg-slate-100 text-slate-700 hover:bg-yellow-100 hover:text-yellow-700 border border-slate-200 hover:border-yellow-200'
                            }`}
                          >
                            <Bookmark className="w-4 h-4 mr-2" />
                            {bookmarkedModules.has(currentModule.id) ? 'Bookmarked' : 'Bookmark'}
                          </button>
                          
                          <button className="flex items-center px-4 py-2 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-all duration-200 border border-slate-200">
                            <Share2 className="w-4 h-4 mr-2" />
                            Share
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Enhanced Module Content */}
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/50 overflow-hidden">
                  <div className="px-8 py-6 bg-gradient-to-r from-slate-50 via-blue-50 to-indigo-50 border-b border-slate-200/50">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h4 className="text-2xl font-bold text-slate-900">Module Content</h4>
                        <p className="text-slate-600">Comprehensive learning material for this module</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-8">
                    <div className="prose prose-slate prose-lg max-w-none">
                      <div className="text-slate-700 leading-relaxed text-lg bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 p-8 rounded-2xl border border-blue-100/50 shadow-inner">
                        {currentModule.content}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Enhanced Questions Section */}
                {currentModule.questions && currentModule.questions.length > 0 && (
                  <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/50 overflow-hidden">
                    <div className="px-8 py-6 bg-gradient-to-r from-slate-50 via-indigo-50 to-purple-50 border-b border-slate-200/50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                            <Target className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h4 className="text-2xl font-bold text-slate-900">Practice Questions</h4>
                            <p className="text-slate-600">Test your understanding of this module</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 font-bold rounded-xl border border-indigo-200">
                            {currentModule.questions.length} Questions
                          </span>
                          <button className="flex items-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200">
                            <Play className="w-4 h-4 mr-2" />
                            Start Quiz
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="p-8">
                      <QuestionList questions={currentModule.questions} />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/50 p-16 text-center">
                <div className="w-36 h-36 bg-gradient-to-br from-slate-100 via-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-8">
                  <BookOpen className="w-20 h-20 text-slate-400" />
                </div>
                <h3 className="text-4xl font-bold text-slate-900 mb-4">
                  Ready to Start Learning?
                </h3>
                <p className="text-slate-500 text-lg leading-relaxed max-w-md mx-auto mb-8">
                  Choose any module from the sidebar to explore its content and practice questions
                </p>
                <div className="flex items-center justify-center space-x-4 text-slate-400">
                  <TrendingUp className="w-5 h-5" />
                  <span className="text-sm">Track your progress</span>
                  <Star className="w-5 h-5" />
                  <span className="text-sm">Earn achievements</span>
                  <Brain className="w-5 h-5" />
                  <span className="text-sm">Build knowledge</span>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
