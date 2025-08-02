'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {  CheckCircle, ArrowLeft, FileText, Sparkles, Zap, Brain } from 'lucide-react';

export default function ProcessingPage() {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Initializing...');
  const [error, setError] = useState<string>('');
  const [currentStep, setCurrentStep] = useState(0);
  const router = useRouter();
  const searchParams = useSearchParams();
  const fileId = searchParams.get('fileId');

  const processingSteps = [
    { progress: 20, status: 'Extracting text from document...', delay: 1000, icon: FileText },
    { progress: 40, status: 'Analyzing content structure...', delay: 1500, icon: Brain },
    { progress: 60, status: 'Creating learning modules...', delay: 1000, icon: Sparkles },
    { progress: 80, status: 'Generating AI questions...', delay: 2000, icon: Zap },
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
        }

        // Call backend API
        const response = await fetch('http://localhost:5001/api/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_id: fileId }),
        });

        const result = await response.json();
        
        if (result.success) {
          setProgress(100);
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
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 text-center border border-purple-100">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6 mx-auto">
            <span className="text-3xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Processing Failed</h2>
          <p className="text-gray-600 mb-6 leading-relaxed">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-2xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const currentStepData = processingSteps[currentStep] || processingSteps[processingSteps.length - 1];
  const StepIcon = currentStepData?.icon || Sparkles;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-purple-300/20 to-indigo-300/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-r from-indigo-300/20 to-purple-300/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="max-w-lg w-full">
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-purple-100 p-8">
            <div className="text-center space-y-8">
              {/* Icon Section */}
              <div className="relative">
                {progress === 100 ? (
                  <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto animate-bounce shadow-lg">
                    <CheckCircle className="w-12 h-12 text-white" />
                  </div>
                ) : (
                  <div className="relative">
                    <div className="w-24 h-24 rounded-full border-4 border-purple-200 mx-auto"></div>
                    <div className="absolute inset-0 w-24 h-24 rounded-full border-4 border-transparent border-t-purple-500 border-r-indigo-500 animate-spin mx-auto"></div>
                    <div className="absolute inset-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                      <StepIcon className="w-8 h-8 text-white" />
                    </div>
                  </div>
                )}
              </div>

              {/* Title */}
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  {progress === 100 ? '🎉 Processing Complete!' : 'Processing Your Syllabus'}
                </h2>
                <p className="text-purple-600 font-medium">
                  {progress === 100 ? 'Redirecting to your modules...' : 'AI is working its magic...'}
                </p>
              </div>

              {/* Progress Section */}
              <div className="space-y-6">
                <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                  <div 
                    className="h-4 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-700 ease-out relative"
                    style={{ width: `${progress}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/30 to-transparent animate-pulse"></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <p className="text-lg font-medium text-gray-800">{status}</p>
                  <p className="text-purple-600 font-bold text-xl">{progress}% complete</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
