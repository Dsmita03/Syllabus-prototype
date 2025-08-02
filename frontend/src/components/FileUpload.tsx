'use client';

import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Syllabus to Modules Converter
          </h1>
          <p className="text-lg text-gray-600">
            Upload your syllabus and get AI-generated modules with questions
          </p>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-300
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
              ${uploading ? 'opacity-50 pointer-events-none' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <div className="space-y-4">
              {uploading ? (
                <div className="animate-spin mx-auto w-12 h-12 text-blue-500">
                  <Upload size={48} />
                </div>
              ) : (
                <FileText className="mx-auto w-16 h-16 text-gray-400" />
              )}
              
              {uploading ? (
                <div>
                  <p className="text-lg font-medium">Uploading your syllabus...</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
                    <div className="bg-blue-600 h-2 rounded-full animate-pulse w-3/4"></div>
                  </div>
                </div>
              ) : (
                <div>
                  <p className="text-xl font-medium text-gray-700">
                    {isDragActive ? 'Drop your syllabus here' : 'Upload your syllabus'}
                  </p>
                  <p className="text-gray-500">
                    Drag & drop a PDF or TXT file, or click to browse
                  </p>
                  <p className="text-sm text-gray-400 mt-2">
                    Maximum file size: 16MB
                  </p>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
