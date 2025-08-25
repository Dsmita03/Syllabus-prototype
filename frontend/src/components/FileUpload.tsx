'use client';

import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle, Zap } from 'lucide-react';

export default function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string>('');
  const router = useRouter();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5001/api/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (result.success) {
        router.push(`/processing?fileId=${result.file_id}`);
      } else {
        setError(result.error || 'Upload failed');
      }
    } catch (error) {
      setError('Network error. Make sure the backend server is running.');
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  }, [router]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    maxSize: 16 * 1024 * 1024, // 16MB
  });

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Section Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your{' '}
          <span className="text-[#BBDCE5]">Syllabus</span>
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Simply drag and drop your syllabus file and let our AI transform it into organized learning modules
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/60 p-8 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-4 left-4 w-8 h-8 bg-[#BBDCE5] rounded-full"></div>
          <div className="absolute top-8 right-8 w-4 h-4 bg-[#D9C4B0] rounded-full"></div>
          <div className="absolute bottom-4 left-8 w-6 h-6 bg-[#CFAB8D] rounded-full"></div>
        </div>

        <div
          {...getRootProps()}
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 transform
            ${isDragActive 
              ? 'border-[#BBDCE5] bg-[#BBDCE5]/10 scale-105' 
              : 'border-[#D9C4B0]/50 hover:border-[#BBDCE5] hover:bg-[#BBDCE5]/5'
            }
            ${uploading ? 'opacity-50 pointer-events-none' : 'hover:scale-102'}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-6">
            {uploading ? (
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] rounded-full flex items-center justify-center mx-auto animate-pulse shadow-lg">
                  <Upload className="w-10 h-10 text-white animate-bounce" />
                </div>
                <div className="absolute inset-0 w-20 h-20 mx-auto border-4 border-[#BBDCE5]/30 border-t-[#BBDCE5] rounded-full animate-spin"></div>
              </div>
            ) : (
              <div className="relative group">
                <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto shadow-lg transition-all duration-300 transform group-hover:scale-110
                  ${isDragActive 
                    ? 'bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] text-white' 
                    : 'bg-[#ECEEDF] text-[#BBDCE5] group-hover:bg-gradient-to-r group-hover:from-[#BBDCE5] group-hover:to-[#D9C4B0] group-hover:text-white'
                  }`}>
                  <FileText className="w-10 h-10" />
                </div>
                {/* Floating Animation Elements */}
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#BBDCE5] rounded-full opacity-30 animate-ping"></div>
                <div className="absolute -bottom-2 -left-2 w-4 h-4 bg-[#CFAB8D] rounded-full opacity-40 animate-pulse"></div>
              </div>
            )}
            
            {uploading ? (
              <div className="space-y-4">
                <p className="text-xl font-semibold text-gray-700">
                  Processing your syllabus...
                </p>
                <p className="text-[#BBDCE5] font-medium">
                  Our AI is analyzing your content
                </p>
                
                {/* Animated Progress Bar */}
                <div className="w-full max-w-xs mx-auto">
                  <div className="w-full bg-[#ECEEDF] rounded-full h-3 overflow-hidden shadow-inner">
                    <div className="h-full bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] rounded-full animate-pulse transition-all duration-1000 w-3/4"></div>
                  </div>
                </div>

                {/* Processing Steps */}
                <div className="flex justify-center space-x-8 mt-6">
                  {[
                    { icon: Upload, label: 'Uploading', active: true },
                    { icon: Zap, label: 'Processing', active: true },
                    { icon: CheckCircle, label: 'Complete', active: false }
                  ].map((step, index) => (
                    <div key={index} className="flex flex-col items-center space-y-2">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300
                        ${step.active ? 'bg-[#BBDCE5] text-white' : 'bg-[#ECEEDF] text-gray-400'}
                      `}>
                        <step.icon className="w-4 h-4" />
                      </div>
                      <span className={`text-xs font-medium ${step.active ? 'text-[#BBDCE5]' : 'text-gray-400'}`}>
                        {step.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-2xl font-semibold text-gray-800">
                  {isDragActive ? (
                    <span className="text-[#BBDCE5]">Drop your syllabus here!</span>
                  ) : (
                    'Drag & Drop Your Syllabus'
                  )}
                </p>
                <p className="text-gray-600 text-lg">
                  or{' '}
                  <span className="text-[#BBDCE5] font-semibold hover:text-[#a5cfd8] cursor-pointer">
                    click to browse
                  </span>{' '}
                  your files
                </p>
                
                {/* File Type Indicators */}
                <div className="flex justify-center space-x-6 mt-6">
                  {[
                    { type: 'PDF', color: 'bg-red-100 text-red-600 border-red-200' },
                    { type: 'TXT', color: 'bg-blue-100 text-blue-600 border-blue-200' }
                  ].map((fileType) => (
                    <div key={fileType.type} className={`px-4 py-2 rounded-lg border ${fileType.color} text-sm font-medium`}>
                      {fileType.type}
                    </div>
                  ))}
                </div>

                <p className="text-sm text-gray-500 mt-4">
                  Maximum file size: 16MB • Supported formats: PDF, TXT
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center shadow-sm">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mr-4">
              <AlertCircle className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p className="text-red-800 font-medium">Upload Failed</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
