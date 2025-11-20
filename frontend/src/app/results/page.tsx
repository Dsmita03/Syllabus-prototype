/* eslint-disable @typescript-eslint/no-unused-vars */
'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import ModuleCard from '@/components/ModuleCard';
import Image from 'next/image';
import {
  Printer,
  Home,
  BookOpen,
  HelpCircle,
  FileText,
  Clock,
  Play,
  CheckCircle,
  Bookmark,
  Brain,
  ArrowLeft,
  Loader2,
  Award,
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

interface TotalOutcome {
  keyword: string;
  bloom_level: string;
  outcome: string;
  importance_score?: number;
  modules?: number[];
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
  const [totalCourseOutcomes, setTotalCourseOutcomes] = useState<TotalOutcome[]>([]);
  const [isGeneratingOutcomes, setIsGeneratingOutcomes] = useState(false);
  const [outcomeError, setOutcomeError] = useState<string>('');

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
        setError('Network error. Please check if the backend server is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId, router]);

  const handleGenerateOutcomes = async () => {
    if (!sessionId || isGeneratingOutcomes) return;

    setIsGeneratingOutcomes(true);
    setOutcomeError('');
    setTotalCourseOutcomes([]);

    try {
      const apiUrl = `http://localhost:5001/api/generate_outcomes?session_id=${sessionId}`;
      console.log('Fetching outcomes from:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      console.log('Backend response:', JSON.stringify(data, null, 2));
      console.log('Success:', data.success);

      if (response.ok && data.success) {
        if (data.course_outcomes && Array.isArray(data.course_outcomes)) {
          console.log('Course outcomes received:', data.course_outcomes.length);
          
          // Group outcomes by module
          const outcomesByModule = new Map<number, TotalOutcome[]>();
          data.course_outcomes.forEach((outcome: TotalOutcome) => {
            if (outcome.modules && outcome.modules.length > 0) {
              const moduleId = outcome.modules[0];
              if (!outcomesByModule.has(moduleId)) {
                outcomesByModule.set(moduleId, []);
              }
              outcomesByModule.get(moduleId)!.push(outcome);
            }
          });

          // Select the best outcome from each module
          const selectedOutcomes: TotalOutcome[] = [];
          const sortedModules = Array.from(outcomesByModule.keys()).sort((a, b) => a - b);
          
          for (const moduleId of sortedModules) {
            const moduleOutcomes = outcomesByModule.get(moduleId)!;
            const bestOutcome = moduleOutcomes.sort((a, b) => 
              (b.importance_score || 0) - (a.importance_score || 0)
            )[0];
            
            // Clean up the outcome text
            const cleanedOutcome = {
              ...bestOutcome,
              outcome: bestOutcome.outcome
                .replace(/^Upon completion of this course, students will be able to:\n?/i, '')
                .replace(/^- /gm, '')
                .trim()
            };
            
            selectedOutcomes.push(cleanedOutcome);
          }

          const finalOutcomes = selectedOutcomes.slice(0, 6);
          
          console.log(`Selected ${finalOutcomes.length} outcomes (1 per module)`);
          setTotalCourseOutcomes(finalOutcomes);
        } else {
          console.error(' No course_outcomes in response');
          setOutcomeError('No course outcomes received from backend.');
        }
      } else {
        console.error(' API Error:', data.error);
        setOutcomeError(data.error || 'Failed to generate course outcomes from API.');
      }
    } catch (err) {
      console.error(' Network Error:', err);
      setOutcomeError('Network error occurred while generating outcomes.');
    } finally {
      setIsGeneratingOutcomes(false);
    }
  };

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

  const handlePrint = () => {
    if (!modules || modules.length === 0) return;
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const printContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Modules Print - ${new Date().toLocaleDateString()}</title>
          <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; max-width: 900px; margin: 2rem auto; padding: 2rem; }
            h1 { color: #5da8bd; border-bottom: 3px solid #BBDCE5; padding-bottom: 10px; }
            .module { background: #ECEEDF; border-left: 4px solid #5da8bd; padding: 20px; margin-bottom: 24px; border-radius: 8px; }
            .module-title { font-size: 1.2rem; font-weight: bold; color: #6b8288; margin-bottom: 10px; }
            .module-content { color: #555; line-height: 1.65; }
            .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #D9C4B0; text-align: center; color: #6b8288; font-size: 12px; }
            @media print { .module { page-break-inside: avoid; } }
          </style>
        </head>
        <body>
          <h1>📚 Extracted Modules</h1>
          <div><strong>Date:</strong> ${new Date().toLocaleString()}</div>
          <div style="margin: 16px 0;"><strong>Total Modules:</strong> ${modules.length}</div>
          ${modules
            .map(
              (mod, idx) => `
              <div class="module">
                <div class="module-title">${mod.title || `Module ${idx + 1}`}</div>
                <div class="module-content">${mod.content || 'No content available'}</div>
              </div>
            `
            )
            .join('')}
          <div class="footer">Generated by EduModule | AI-powered Syllabus Extraction</div>
        </body>
      </html>
    `;
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 250);
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
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg overflow-hidden shadow-md flex-shrink-0 relative">
                <Image 
                  src="/logo.png" 
                  alt="EduModule Logo" 
                  width={40} 
                  height={40} 
                  className="object-contain"
                />
              </div>
              <h1 className="text-lg font-semibold text-gray-800 tracking-wide">EduModule</h1>
            </div>
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 px-4 py-2 bg-[#5da8bd] text-white font-semibold rounded-lg hover:bg-[#71a9b8] transition-colors shadow-md hover:shadow-lg"
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">New Upload</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid md:grid-cols-12 lg:grid-cols-12 gap-6 lg:gap-8">
          {/* Left Sidebar - Module List */}
          <aside className="md:col-span-5 lg:col-span-5">
            <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 sticky top-24">
              <div className="p-6 border-b border-[#D9C4B0]/30 bg-gradient-to-r from-[#ECEEDF]/50 to-[#BBDCE5]/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0">
                <div className="w-full">
                  <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xl font-bold text-gray-900">Modules</h2>
                    <span className="px-3 py-1 bg-[#BBDCE5] text-white text-sm font-semibold rounded-full">{modules.length}</span>
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <p className="text-gray-600 text-sm">Select a module to view content</p>
                    <button
                      onClick={handlePrint}
                      className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-[#5da8bd] text-white rounded-lg hover:bg-[#91bcc6] transition-colors text-sm w-fit"
                      title="Print all modules"
                    >
                      <Printer className="w-4 h-4" />
                      <span>Print All</span>
                    </button>
                  </div>
                </div>
              </div>

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
                  />
                ))}
              </div>
            </div>
          </aside>

          {/* Right Content Area */}
          <section className="md:col-span-7 lg:col-span-7">
            {currentModule ? (
              <div className="space-y-6">
                {/* Module Header */}
                <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 p-8">
                  <div className="flex items-start gap-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-[#4f8493] to-[#b8a18c] rounded-xl flex items-center justify-center">
                      <FileText className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-3xl font-bold text-gray-900">{currentModule.title}</h3>
                        {completedModules.has(currentModule.id) && (
                          <span className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                            <CheckCircle className="w-4 h-4" />
                            Completed
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-3 text-sm mb-4">
                        {currentModule.questions && currentModule.questions.length > 0 && (
                          <span className="flex items-center gap-1.5 px-3 py-1.5 bg-[#BBDCE5]/20 text-[#BBDCE5] rounded-full font-medium border border-[#BBDCE5]/30">
                            <HelpCircle className="w-4 h-4" />
                            {currentModule.questions.length} Questions
                          </span>
                        )}
                        <span className="flex items-center gap-1.5 px-3 py-1.5 bg-[#D9C4B0]/20 text-[#CFAB8D] rounded-full font-medium border border-[#D9C4B0]/30">
                          <Clock className="w-4 h-4" />
                          {Math.ceil(currentModule.content.split(' ').length / 200)} min read
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-3">
                        {currentModule.questions && currentModule.questions.length > 0 && (
                          <button
                            onClick={() => router.push(`/quiz?moduleId=${currentModule.id}`)}
                            className="flex items-center gap-2 px-4 py-2 bg-[#BBDCE5] text-white rounded-lg hover:bg-[#a5cfd8] transition-colors font-medium"
                          >
                            <Play className="w-4 h-4" />
                            Start Quiz
                          </button>
                        )}
                        <button
                          onClick={() => markAsCompleted(currentModule.id)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors border ${
                            completedModules.has(currentModule.id)
                              ? 'bg-green-100 text-green-700 border-green-200'
                              : 'bg-[#ECEEDF] text-gray-700 hover:bg-green-100 hover:text-green-700 border-[#D9C4B0]/30 hover:border-green-200'
                          }`}
                        >
                          <CheckCircle className="w-4 h-4" />
                          {completedModules.has(currentModule.id) ? 'Completed' : 'Mark Complete'}
                        </button>
                        <button
                          onClick={() => toggleBookmark(currentModule.id)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors border ${
                            bookmarkedModules.has(currentModule.id)
                              ? 'bg-yellow-100 text-yellow-700 border-yellow-200'
                              : 'bg-[#ECEEDF] text-gray-700 hover:bg-yellow-100 hover:text-yellow-700 border-[#D9C4B0]/30 hover:border-yellow-200'
                          }`}
                        >
                          <Bookmark className="w-4 h-4" />
                          Bookmark
                        </button>
                        <button
                          onClick={handleGenerateOutcomes}
                          disabled={isGeneratingOutcomes || !modules.length}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors shadow-sm ${
                            isGeneratingOutcomes
                              ? 'bg-gray-400 text-white cursor-not-allowed border-gray-400'
                              : 'bg-[#5da8bd] text-white hover:bg-[#71a9b8] border-transparent'
                          }`}
                        >
                          {isGeneratingOutcomes ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Award className="w-4 h-4" />
                          )}
                          {isGeneratingOutcomes ? 'Generating...' : 'Course Outcomes'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Module Content */}
                <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30">
                  <div className="flex items-center gap-3 p-6 border-b border-[#D9C4B0]/30 bg-gradient-to-r from-[#ECEEDF]/50 to-[#BBDCE5]/20">
                    <div className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center">
                      <BookOpen className="w-5 h-5 text-white" />
                    </div>
                    <h4 className="text-xl font-bold text-gray-900">Module Content</h4>
                  </div>
                  <div className="p-6">
                    <div className="bg-gradient-to-r from-[#ECEEDF]/60 to-[#BBDCE5]/20 rounded-xl p-6 border border-[#BBDCE5]/30">
                      <p className="text-gray-700 leading-relaxed text-lg whitespace-pre-wrap">{currentModule.content}</p>
                    </div>
                  </div>
                </div>

                {/* Course Outcomes Section - Matching Website Design */}
                {(isGeneratingOutcomes || totalCourseOutcomes.length > 0 || outcomeError) && (
                  <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 overflow-hidden">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-[#ECEEDF]/50 to-[#BBDCE5]/20 p-6 border-b border-[#D9C4B0]/30">
                      <div className="flex items-center gap-3">
                        <div className="w-11 h-11 bg-gradient-to-br from-[#5da8bd] to-[#71a9b8] rounded-xl flex items-center justify-center shadow-sm">
                          <Award className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h4 className="text-xl font-bold text-gray-900">Course Outcomes</h4>
                          <p className="text-sm text-gray-600 mt-0.5">
                            On completion of the course, the student will be able to
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                      {isGeneratingOutcomes && (
                        <div className="flex items-center justify-center py-12">
                          <Loader2 className="w-7 h-7 text-[#5da8bd] animate-spin" />
                          <span className="text-gray-700 text-base font-medium ml-3">Generating outcomes...</span>
                        </div>
                      )}

                      {outcomeError && (
                        <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200">
                          ⚠️ {outcomeError}
                        </div>
                      )}

                      {!isGeneratingOutcomes && totalCourseOutcomes.length > 0 && (
                        <div className="space-y-5">
                          {totalCourseOutcomes.map((outcome, index) => (
                            <div
                              key={index}
                              className="group bg-white border-2 border-[#BBDCE5]/30 rounded-xl p-5 hover:border-[#5da8bd]/50 hover:shadow-md transition-all duration-200"
                            >
                              <div className="flex items-start gap-4">
                                {/* CO Badge */}
                                <div className="flex-shrink-0">
                                  <div className="w-14 h-14 bg-gradient-to-br from-[#BBDCE5]/20 to-[#5da8bd]/10 border-2 border-[#5da8bd]/30 rounded-xl flex items-center justify-center group-hover:border-[#5da8bd]/50 transition-colors">
                                    <span className="text-[#5da8bd] font-bold text-base">CO-{index + 1}</span>
                                  </div>
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                  {/* Tags */}
                                  <div className="flex flex-wrap items-center gap-2 mb-3">
                                    <span className="px-3 py-1.5 bg-[#BBDCE5]/20 text-[#5da8bd] border border-[#BBDCE5] rounded-lg text-xs font-semibold">
                                      {outcome.bloom_level}
                                    </span>
                                    {/* {outcome.modules && outcome.modules.length > 0 && (
                                      <span className="px-3 py-1.5 bg-[#D9C4B0]/20 text-[#b8a18c] border border-[#D9C4B0] rounded-lg text-xs font-medium">
                                        Module {outcome.modules[0]}
                                      </span>
                                    )} */}
                                  </div>

                                  {/* Outcome Text */}
                                  <p className="text-gray-700 leading-relaxed text-[15px] whitespace-pre-wrap">
                                    {outcome.outcome}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
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
