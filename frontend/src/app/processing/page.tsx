'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle, ArrowLeft, FileText, Brain, Target } from 'lucide-react';

export default function ProcessingPage() {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Initializing...');
  const [error, setError] = useState<string>('');
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const router = useRouter();
  const searchParams = useSearchParams();
  const fileId = searchParams.get('fileId');

  const processingSteps = [
    { 
      progress: 33, 
      status: 'Reading document...', 
      delay: 1000, 
      icon: FileText,
    },
    { 
      progress: 67, 
      status: 'Analyzing content...', 
      delay: 1500, 
      icon: Brain,
    },
    { 
      progress: 100, 
      status: 'Creating modules...', 
      delay: 1000, 
      icon: Target,
    },
  ];

  useEffect(() => {
    if (!fileId) {
      router.push('/');
      return;
    }

    const processFile = async () => {
      try {
        // Process through steps
        for (let i = 0; i < processingSteps.length; i++) {
          const step = processingSteps[i];
          setCurrentStep(i);
          await new Promise(resolve => setTimeout(resolve, step.delay));
          setProgress(step.progress);
          setStatus(step.status);
          setCompletedSteps(prev => [...prev, i]);
        }

        // Call backend API
        const response = await fetch('http://localhost:5001/api/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_id: fileId }),
        });

        const result = await response.json();
        
        if (result.success) {
          setStatus('Complete! Redirecting...');
          await new Promise(resolve => setTimeout(resolve, 1000));
          router.push(`/results?sessionId=${result.session_id}`);
        } else {
          setError(result.error || 'Processing failed');
        }
      } catch (error) {
        console.error('Processing failed:', error);
        setError('Network error. Make sure the backend server is running on port 5001.');
      }
    };

    processFile();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileId, router]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#ECEEDF] via-white to-[#BBDCE5]/30 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center border border-[#D9C4B0]/30">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6 mx-auto">
            <span className="text-2xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Something went wrong</h2>
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

  const currentStepData = processingSteps[currentStep] || processingSteps[processingSteps.length - 1];
  const StepIcon = currentStepData?.icon || FileText;
  const isComplete = progress === 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#ECEEDF] via-white to-[#BBDCE5]/30 flex items-center justify-center p-6">
      <div className="max-w-lg w-full">
        <div className="bg-white rounded-2xl shadow-lg border border-[#D9C4B0]/30 p-8">
          
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-[#BBDCE5] rounded-xl flex items-center justify-center mx-auto mb-4">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Your Syllabus</h1>
            <p className="text-gray-600">Creating smart learning modules</p>
          </div>

          {/* Progress Circle */}
          <div className="text-center mb-8">
            <div className="relative inline-block">
              {isComplete ? (
                <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center animate-bounce">
                  <CheckCircle className="w-12 h-12 text-white" />
                </div>
              ) : (
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      stroke="#ECEEDF"
                      strokeWidth="8"
                      fill="none"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      stroke="#BBDCE5"
                      strokeWidth="8"
                      fill="none"
                      strokeLinecap="round"
                      strokeDasharray={`${2 * Math.PI * 40}`}
                      strokeDashoffset={`${2 * Math.PI * 40 * (1 - progress / 100)}`}
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <StepIcon className="w-8 h-8 text-[#BBDCE5]" />
                  </div>
                </div>
              )}
            </div>
            <div className="mt-4">
              <p className="text-lg font-semibold text-gray-900">{progress}%</p>
              <p className="text-[#BBDCE5] font-medium">{status}</p>
            </div>
          </div>

          {/* Steps List */}
          <div className="space-y-3">
            {processingSteps.map((step, index) => {
              const StepIcon = step.icon;
              const isCompleted = completedSteps.includes(index);
              const isCurrent = currentStep === index;
              
              return (
                <div 
                  key={index}
                  className={`flex items-center p-3 rounded-lg transition-all duration-300 ${
                    isCompleted 
                      ? 'bg-green-50 text-green-700' 
                      : isCurrent 
                        ? 'bg-[#BBDCE5]/10 text-[#BBDCE5]' 
                        : 'bg-[#ECEEDF]/50 text-gray-500'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                    isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isCurrent 
                        ? 'bg-[#BBDCE5] text-white' 
                        : 'bg-[#D9C4B0]/50 text-gray-600'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <StepIcon className="w-4 h-4" />
                    )}
                  </div>
                  <span className="font-medium">{step.status}</span>
                </div>
              );
            })}
          </div>

          {/* Tip */}
          <div className="mt-8 p-4 bg-gradient-to-r from-[#ECEEDF]/50 to-[#BBDCE5]/20 rounded-lg border border-[#D9C4B0]/30">
            <p className="text-sm text-gray-700">
              <span className="font-semibold text-[#BBDCE5]">💡 Tip:</span> Our AI analyzes your content structure to create focused study modules.
            </p>
          </div>

          {/* Complete Button */}
          {isComplete && (
            <div className="mt-6 text-center">
              <button
                onClick={() => router.push('/')}
                className="inline-flex items-center px-6 py-3 bg-[#BBDCE5] text-white font-semibold rounded-lg hover:bg-[#a5cfd8] transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}