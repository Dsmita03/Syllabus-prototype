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
      progress: 20, 
      status: 'Extracting text from document...', 
      delay: 1000, 
      icon: FileText,
      description: 'Reading and parsing your syllabus content'
    },
    { 
      progress: 40, 
      status: 'Analyzing content structure...', 
      delay: 1500, 
      icon: Brain,
      description: 'Understanding topics and learning objectives'
    },
    { 
      progress: 60, 
      status: 'Creating learning modules...', 
      delay: 1000, 
      icon: Target,
      description: 'Organizing content into structured modules'
    },
    { 
      progress: 80, 
      status: 'Generating AI questions...', 
      delay: 2000, 
      icon: Zap,
      description: 'Creating personalized assessment questions'
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
          setProgress(100);
          setStatus('Complete! Redirecting...');
          await new Promise(resolve => setTimeout(resolve, 1000));
          router.push(`/results?sessionId=${result.session_id}`);
        } else {
          setError(result.error || 'Processing failed');
        }
      } catch (error) {
        console.error('Processing failed:', error);
        setError('Network error.');
      }
    };

    processFile();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileId, router]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
        <div className="max-w-lg w-full bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 text-center border border-red-100">
          {/* Error Animation */}
          <div className="relative mb-8">
            <div className="w-24 h-24 bg-gradient-to-br from-red-400 to-orange-500 rounded-full flex items-center justify-center mx-auto animate-pulse shadow-lg">
              <span className="text-4xl">⚠️</span>
            </div>
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full animate-ping"></div>
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Oops! Something went wrong</h2>
          <p className="text-gray-600 mb-8 leading-relaxed text-lg">{error}</p>
          
          <div className="space-y-4">
            <button
              onClick={() => router.push('/')}
              className="w-full inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 text-white font-semibold rounded-2xl hover:from-red-600 hover:to-orange-600 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Try Again
            </button>
            
          </div>
        </div>
      </div>
    );
  }

  const currentStepData = processingSteps[currentStep] || processingSteps[processingSteps.length - 1];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 relative overflow-hidden">
      {/* Enhanced Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-purple-400/20 to-indigo-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-r from-indigo-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-r from-pink-300/10 to-blue-300/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="max-w-2xl w-full">
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-purple-100 overflow-hidden">
            
            {/* Header Section */}
            <div className="bg-gradient-to-r from-purple-500 to-indigo-600 p-8 text-white text-center">
              <h1 className="text-3xl font-bold mb-2">AI Processing Center</h1>
              <p className="text-purple-100">Transform your syllabus into smart learning modules</p>
            </div>

            {/* Main Content */}
            <div className="p-8">
              
              {/* Central Progress Circle */}
              <div className="text-center mb-8">
                <div className="relative inline-block">
                  {progress === 100 ? (
                    <div className="w-32 h-32 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center animate-bounce shadow-2xl">
                      <CheckCircle className="w-16 h-16 text-white" />
                    </div>
                  ) : (
                    <div className="relative">
                      {/* Outer Ring */}
                      <div className="w-32 h-32 rounded-full border-8 border-purple-100"></div>
                      
                      {/* Progress Ring */}
                      <svg className="absolute inset-0 w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          className="text-purple-200"
                        />
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          stroke="url(#gradient)"
                          strokeWidth="8"
                          fill="none"
                          strokeLinecap="round"
                          strokeDasharray={`${2 * Math.PI * 50}`}
                          strokeDashoffset={`${2 * Math.PI * 50 * (1 - progress / 100)}`}
                          className="transition-all duration-1000 ease-out"
                        />
                        <defs>
                          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#8B5CF6" />
                            <stop offset="100%" stopColor="#3B82F6" />
                          </linearGradient>
                        </defs>
                      </svg>
                      
                      {/* Inner Icon */}
                      <div className="absolute inset-4 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                        <currentStepData.icon className="w-12 h-12 text-white animate-pulse" />
                      </div>
                      
                      {/* Progress Percentage */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl font-bold text-white mt-16">{progress}%</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Status Text */}
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {progress === 100 ? '🎉 Processing Complete!' : 'AI is Working...'}
                </h2>
                <p className="text-lg text-purple-600 font-medium mb-2">{status}</p>
                {currentStepData?.description && progress < 100 && (
                  <p className="text-gray-600">{currentStepData.description}</p>
                )}
              </div>

              {/* Steps Progress */}
              <div className="space-y-4 mb-8">
                {processingSteps.map((step, index) => {
                  const StepIcon = step.icon;
                  const isCompleted = completedSteps.includes(index);
                  const isCurrent = currentStep === index;
                  const isUpcoming = index > currentStep;

                  return (
                    <div 
                      key={index}
                      className={`flex items-center p-4 rounded-2xl transition-all duration-500 ${
                        isCompleted 
                          ? 'bg-green-50 border-2 border-green-200' 
                          : isCurrent 
                            ? 'bg-purple-50 border-2 border-purple-200 animate-pulse' 
                            : 'bg-gray-50 border-2 border-gray-100'
                      }`}
                    >
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center mr-4 transition-all duration-300 ${
                        isCompleted 
                          ? 'bg-green-500 text-white' 
                          : isCurrent 
                            ? 'bg-purple-500 text-white animate-pulse' 
                            : 'bg-gray-300 text-gray-500'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle className="w-6 h-6" />
                        ) : (
                          <StepIcon className="w-6 h-6" />
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <h3 className={`font-semibold ${
                          isCompleted ? 'text-green-800' : isCurrent ? 'text-purple-800' : 'text-gray-600'
                        }`}>
                          {step.status}
                        </h3>
                        <p className={`text-sm ${
                          isCompleted ? 'text-green-600' : isCurrent ? 'text-purple-600' : 'text-gray-500'
                        }`}>
                          {step.description}
                        </p>
                      </div>
                      
                      {isCompleted && (
                        <div className="text-green-500 animate-fade-in">
                          <CheckCircle className="w-6 h-6" />
                        </div>
                      )}
                      
                      {isCurrent && (
                        <div className="flex items-center text-purple-500">
                          <Clock className="w-5 h-5 animate-spin" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Fun Facts or Tips */}
              {progress < 100 && (
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-2xl p-6 border border-purple-100">
                  <div className="flex items-center mb-3">
                    <Sparkles className="w-5 h-5 text-purple-500 mr-2" />
                    <h4 className="font-semibold text-purple-800">Did you know?</h4>
                  </div>
                  <p className="text-purple-700 text-sm">
                    Our AI can process documents in multiple formats and automatically detects learning objectives, 
                    key topics, and creates personalized assessment questions based on your syllabus content.
                  </p>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}