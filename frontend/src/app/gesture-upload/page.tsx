/* eslint-disable @typescript-eslint/no-explicit-any */
 
'use client';

import { useEffect, useRef, useState } from 'react';
import { Camera, FileText, CheckCircle, XCircle, Loader2, Hand, RotateCw, Printer } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5001';

interface GestureResponse {
  status: string;
  gesture: string;
  state: string;
  current_file?: string;
  total_files?: number;
  selected_file?: string;
  uploaded_file?: string;
  processing_result?: any;
  error?: string;
}

export default function GestureUploadPage() {
  // Camera and video refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // State management
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [gestureData, setGestureData] = useState<GestureResponse>({
    status: 'Initializing...',
    gesture: 'none',
    state: 'IDLE',
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  // Start camera
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsCameraActive(true);
        setError('');
      }
    } catch (err) {
      console.error('Camera error:', err);
      setError('Failed to access camera. Please grant camera permissions.');
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  // Capture frame and send to backend
  const captureAndSendFrame = async () => {
    if (!videoRef.current || !canvasRef.current || !isCameraActive) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx || video.readyState !== video.HAVE_ENOUGH_DATA) return;

    // Draw video frame to canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);

    try {
      setIsProcessing(true);

      const response = await fetch(`${API_BASE_URL}/api/gesture/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ image: imageData }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: GestureResponse = await response.json();
      setGestureData(data);

      // Check if upload completed
      if (data.uploaded_file && data.processing_result) {
        setUploadResult(data.processing_result);
      }

      setError('');
    } catch (err) {
      console.error('Gesture detection error:', err);
      setError('Failed to detect gesture. Check if backend is running on port 5001.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Reset gesture session
  const resetSession = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/gesture/reset`, {
        method: 'POST',
        credentials: 'include',
      });
      setGestureData({
        status: 'Session reset',
        gesture: 'none',
        state: 'IDLE',
      });
      setUploadResult(null);
      setError('');
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  // Print upload results
  const handlePrint = () => {
    if (!uploadResult) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const printContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Upload Results - ${new Date().toLocaleDateString()}</title>
          <style>
            body {
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
              max-width: 800px;
              margin: 40px auto;
              padding: 20px;
              color: #333;
            }
            h1 {
              color: #5da8bd;
              border-bottom: 3px solid #BBDCE5;
              padding-bottom: 10px;
            }
            .header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 30px;
            }
            .date {
              color: #6b8288;
              font-size: 14px;
            }
            .module {
              background: #ECEEDF;
              border-left: 4px solid #5da8bd;
              padding: 20px;
              margin-bottom: 20px;
              border-radius: 8px;
            }
            .module-title {
              font-size: 18px;
              font-weight: bold;
              color: #6b8288;
              margin-bottom: 10px;
            }
            .module-content {
              color: #555;
              line-height: 1.6;
            }
            .footer {
              margin-top: 40px;
              padding-top: 20px;
              border-top: 2px solid #D9C4B0;
              text-align: center;
              color: #6b8288;
              font-size: 12px;
            }
            @media print {
              body { margin: 20px; }
              .module { page-break-inside: avoid; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>📚 Syllabus Upload Results</h1>
            <div class="date">${new Date().toLocaleString()}</div>
          </div>
          
          <p><strong>Total Modules Extracted:</strong> ${uploadResult.modules?.length || 0}</p>
          
          ${uploadResult.modules?.map((module: any, idx: number) => `
            <div class="module">
              <div class="module-title">${module.title || `Module ${idx + 1}`}</div>
              <div class="module-content">${module.content || 'No content available'}</div>
            </div>
          `).join('') || '<p>No modules available</p>'}
          
          <div class="footer">
            <p>Generated by Gesture Syllabus Upload System</p>
            <p>Processed using AI-powered syllabus extraction</p>
          </div>
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

  // Continuous frame capture
  useEffect(() => {
    if (!isCameraActive) return;

    const intervalId = setInterval(() => {
      captureAndSendFrame();
    }, 500); // Send frame every 500ms

    return () => clearInterval(intervalId);
  }, [isCameraActive]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // Get state color
  const getStateColor = (state: string) => {
    switch (state) {
      case 'IDLE':
        return 'bg-gray-400';
      case 'BROWSING':
        return 'bg-[#5da8bd]';
      case 'CONFIRMING':
        return 'bg-[#BBDCE5]';
      case 'ERROR':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  // Get gesture icon
  const getGestureEmoji = (gesture: string) => {
    switch (gesture) {
      case 'thumbs_up':
        return '👍';
      case 'thumbs_down':
        return '👎';
      case 'point':
        return '👉';
      case 'none':
        return '✋';
      default:
        return '🤚';
    }
  };

  return (
    <div className="min-h-screen bg-[#ECEEDF] py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-[#5da8bd] to-[#91bcc6] rounded-2xl flex items-center justify-center shadow-lg">
              <Hand className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-[#6b8288] mb-3">
            Gesture Syllabus Upload
          </h1>
          <p className="text-gray-600 text-lg">
            Use hand gestures to browse and select files from your system
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Camera Feed */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-[#D9C4B0]/30">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-[#6b8288] flex items-center gap-3">
                <Camera className="w-6 h-6 text-[#5da8bd]" />
                Live Camera Feed
              </h2>
              {!isCameraActive ? (
                <button
                  onClick={startCamera}
                  className="px-6 py-3 bg-[#5da8bd] text-white font-semibold rounded-xl hover:bg-[#71a9b8] transition-all shadow-md hover:shadow-lg"
                >
                  Start Camera
                </button>
              ) : (
                <button
                  onClick={stopCamera}
                  className="px-6 py-3 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-all shadow-md hover:shadow-lg"
                >
                  Stop Camera
                </button>
              )}
            </div>

            <div className="relative bg-[#6b8288] rounded-xl overflow-hidden aspect-video shadow-inner">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />
              <canvas ref={canvasRef} className="hidden" />

              {!isCameraActive && (
                <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-[#6b8288] to-[#5da8bd]">
                  <div className="text-center text-white">
                    <Camera className="w-20 h-20 mx-auto mb-4 opacity-70" />
                    <p className="text-lg font-medium">Click &quot;Start Camera&quot; to begin</p>
                  </div>
                </div>
              )}

              {isProcessing && (
                <div className="absolute top-4 right-4 bg-white/90 rounded-lg p-2">
                  <Loader2 className="w-6 h-6 text-[#5da8bd] animate-spin" />
                </div>
              )}

              {/* Current State Badge */}
              {isCameraActive && (
                <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-2 shadow-md">
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${getStateColor(gestureData.state)} animate-pulse`} />
                    <span className="text-sm font-semibold text-[#6b8288]">{gestureData.state}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Gesture Instructions */}
            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-[#BBDCE5] to-[#a5cfd8] p-4 rounded-xl text-center shadow-md border border-[#91bcc6]/30">
                <div className="text-3xl mb-2">👉</div>
                <div className="font-semibold text-white text-sm">Point</div>
                <div className="text-white/80 text-xs mt-1">Start/Select</div>
              </div>
              <div className="bg-gradient-to-br from-[#5da8bd] to-[#71a9b8] p-4 rounded-xl text-center shadow-md border border-[#5da8bd]/30">
                <div className="text-3xl mb-2">👍</div>
                <div className="font-semibold text-white text-sm">Thumbs Up</div>
                <div className="text-white/80 text-xs mt-1">Next/Confirm</div>
              </div>
              <div className="bg-gradient-to-br from-[#91bcc6] to-[#BBDCE5] p-4 rounded-xl text-center shadow-md border border-[#71a9b8]/30">
                <div className="text-3xl mb-2">👎</div>
                <div className="font-semibold text-white text-sm">Thumbs Down</div>
                <div className="text-white/80 text-xs mt-1">Previous/Cancel</div>
              </div>
            </div>
          </div>

          {/* Status Panel */}
          <div className="space-y-6">
            {/* System Status */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-[#D9C4B0]/30">
              <h2 className="text-2xl font-semibold text-[#6b8288] mb-6">System Status</h2>

              <div className="space-y-5">
                <div className="bg-[#ECEEDF] rounded-xl p-4 border border-[#D9C4B0]/30">
                  <div className="text-sm text-gray-600 mb-2 font-medium">
                    Application State
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`w-4 h-4 rounded-full ${getStateColor(gestureData.state)} shadow-sm`} />
                    <span className="font-bold text-[#6b8288] text-lg">{gestureData.state}</span>
                  </div>
                </div>

                <div className="bg-[#ECEEDF] rounded-xl p-4 border border-[#D9C4B0]/30">
                  <div className="text-sm text-gray-600 mb-2 font-medium">
                    Current Gesture
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{getGestureEmoji(gestureData.gesture)}</span>
                    <span className="font-semibold text-[#6b8288] text-lg capitalize">
                      {gestureData.gesture.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <div className="bg-[#ECEEDF] rounded-xl p-4 border border-[#D9C4B0]/30">
                  <div className="text-sm text-gray-600 mb-2 font-medium">Status</div>
                  <div className="text-[#6b8288] font-medium">{gestureData.status}</div>
                </div>

                {gestureData.current_file && (
                  <div className="bg-gradient-to-br from-[#BBDCE5] to-[#a5cfd8] rounded-xl p-4 shadow-md">
                    <div className="text-sm text-white/90 mb-2 font-medium">
                      Current File
                    </div>
                    <div className="flex items-center gap-3 bg-white/20 backdrop-blur-sm p-3 rounded-lg">
                      <FileText className="w-5 h-5 text-white" />
                      <span className="text-sm font-mono text-white font-medium break-all">
                        {gestureData.current_file}
                      </span>
                    </div>
                  </div>
                )}

                {gestureData.total_files && (
                  <div className="bg-[#ECEEDF] rounded-xl p-4 border border-[#D9C4B0]/30">
                    <div className="text-sm text-gray-600 mb-1 font-medium">
                      Total Files Available
                    </div>
                    <div className="font-bold text-2xl text-[#5da8bd]">{gestureData.total_files}</div>
                  </div>
                )}
              </div>

              <button
                onClick={resetSession}
                className="w-full mt-6 px-6 py-3 bg-[#ECEEDF] text-[#6b8288] font-semibold rounded-xl hover:bg-[#D9C4B0]/50 transition-all border border-[#D9C4B0]/30 flex items-center justify-center gap-2"
              >
                <RotateCw className="w-5 h-5" />
                Reset Session
              </button>
            </div>

            {/* Upload Result */}
            {uploadResult && (
              <div className="bg-white rounded-2xl shadow-xl p-8 border border-green-200">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                      <CheckCircle className="w-7 h-7 text-green-600" />
                    </div>
                    <h2 className="text-2xl font-semibold text-green-800">Upload Successful!</h2>
                  </div>
                  <button
                    onClick={handlePrint}
                    className="flex items-center gap-2 px-4 py-2 bg-[#5da8bd] text-white font-semibold rounded-lg hover:bg-[#71a9b8] transition-all shadow-md hover:shadow-lg"
                    title="Print results"
                  >
                    <Printer className="w-5 h-5" />
                    Print
                  </button>
                </div>

                {uploadResult.modules && uploadResult.modules.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-600 mb-4 font-medium">
                      Extracted {uploadResult.modules.length} learning modules
                    </div>
                    <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
                      {uploadResult.modules.map((module: any, idx: number) => (
                        <div
                          key={idx}
                          className="bg-gradient-to-br from-[#BBDCE5] to-[#a5cfd8] p-4 rounded-xl border border-[#91bcc6]/30 shadow-sm"
                        >
                          <div className="font-semibold text-white mb-2">
                            {module.title || `Module ${idx + 1}`}
                          </div>
                          <div className="text-sm text-white/90 line-clamp-3">
                            {module.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6">
                <div className="flex items-center gap-3 text-red-800 mb-3">
                  <XCircle className="w-6 h-6" />
                  <span className="font-semibold text-lg">Error</span>
                </div>
                <p className="text-red-700">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-12 bg-white rounded-2xl shadow-xl p-8 border border-[#D9C4B0]/30">
          <h2 className="text-2xl font-semibold text-[#6b8288] mb-6">
            Tips for Better Gesture Recognition
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-start gap-4 p-5 bg-[#ECEEDF] rounded-xl border border-[#D9C4B0]/30">
              <div className="w-12 h-12 bg-gradient-to-br from-[#BBDCE5] to-[#a5cfd8] rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                <span className="text-2xl">💡</span>
              </div>
              <div>
                <div className="font-semibold text-[#6b8288] mb-1">Good Lighting</div>
                <div className="text-sm text-gray-600">
                  Ensure adequate lighting for clear hand detection
                </div>
              </div>
            </div>
            <div className="flex items-start gap-4 p-5 bg-[#ECEEDF] rounded-xl border border-[#D9C4B0]/30">
              <div className="w-12 h-12 bg-gradient-to-br from-[#5da8bd] to-[#71a9b8] rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                <span className="text-2xl">👁️</span>
              </div>
              <div>
                <div className="font-semibold text-[#6b8288] mb-1">Clear View</div>
                <div className="text-sm text-gray-600">
                  Keep hands visible within camera frame
                </div>
              </div>
            </div>
            <div className="flex items-start gap-4 p-5 bg-[#ECEEDF] rounded-xl border border-[#D9C4B0]/30">
              <div className="w-12 h-12 bg-gradient-to-br from-[#91bcc6] to-[#BBDCE5] rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                <span className="text-2xl">🎯</span>
              </div>
              <div>
                <div className="font-semibold text-[#6b8288] mb-1">Steady Movements</div>
                <div className="text-sm text-gray-600">
                  Make deliberate, steady gestures
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
