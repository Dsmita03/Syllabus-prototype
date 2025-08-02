import { BookOpen, HelpCircle, Clock } from 'lucide-react';

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

interface ModuleCardProps {
  module: Module;
  isSelected: boolean;
  onClick: () => void;
  index: number;
}

export default function ModuleCard({ module, isSelected, onClick, index }: ModuleCardProps) {
  const questionCount = module.questions?.length || 0;
  const readingTime = Math.ceil(module.content.split(' ').length / 200); // Approximate reading time

  return (
    <div
      onClick={onClick}
      className={`
        group relative overflow-hidden rounded-2xl cursor-pointer transition-all duration-300 transform
        ${isSelected
          ? 'bg-gradient-to-br from-purple-500 via-purple-600 to-indigo-600 text-white shadow-xl scale-105 ring-4 ring-purple-200'
          : 'bg-white hover:bg-purple-50 text-gray-700 shadow-md hover:shadow-lg hover:scale-[1.02]'
        }
      `}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className={`absolute top-2 right-2 w-16 h-16 rounded-full ${
          isSelected ? 'bg-white/20' : 'bg-purple-100'
        }`}></div>
        <div className={`absolute bottom-2 left-2 w-8 h-8 rounded-full ${
          isSelected ? 'bg-white/10' : 'bg-indigo-100'
        }`}></div>
      </div>

      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-start space-x-4 mb-4">
          {/* Module Number */}
          <div className={`
            w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg flex-shrink-0 transition-all duration-300
            ${isSelected 
              ? 'bg-white/20 text-white shadow-lg' 
              : 'bg-gradient-to-br from-purple-100 to-indigo-100 text-purple-700 group-hover:from-purple-200 group-hover:to-indigo-200'
            }
          `}>
            {index + 1}
          </div>

          {/* Module Info */}
          <div className="flex-1 min-w-0">
            <h3 className={`font-bold text-base mb-2 transition-colors duration-300 ${
              isSelected ? 'text-white' : 'text-gray-800 group-hover:text-purple-800'
            }`}
            style={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}>
              {module.title}
            </h3>
            
            <div className="flex items-center space-x-4 text-sm">
              <div className={`flex items-center transition-colors duration-300 ${
                isSelected ? 'text-purple-100' : 'text-gray-500 group-hover:text-purple-600'
              }`}>
                <HelpCircle className="w-4 h-4 mr-1" />
                <span>{questionCount} questions</span>
              </div>
              
              <div className={`flex items-center transition-colors duration-300 ${
                isSelected ? 'text-purple-100' : 'text-gray-500 group-hover:text-purple-600'
              }`}>
                <Clock className="w-4 h-4 mr-1" />
                <span>{readingTime} min read</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content Preview */}
        <p className={`text-sm leading-relaxed transition-colors duration-300 ${
          isSelected ? 'text-purple-100' : 'text-gray-600 group-hover:text-gray-700'
        }`}
        style={{
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {module.content.substring(0, 120)}...
        </p>

        {/* Bottom Indicator */}
        <div className="mt-4 flex items-center justify-between">
          <div className={`flex items-center text-xs font-medium ${
            isSelected ? 'text-white' : 'text-purple-600'
          }`}>
            <BookOpen className="w-3 h-3 mr-1" />
            Module {index + 1}
          </div>
          
          {isSelected && (
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
          )}
        </div>

        {/* Selection Indicator */}
        {isSelected && (
          <div className="absolute top-4 right-4">
            <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
              <div className="w-3 h-3 bg-white rounded-full"></div>
            </div>
          </div>
        )}
      </div>

      {/* Hover Effect Overlay */}
      <div className={`
        absolute inset-0 transition-opacity duration-300 
        ${isSelected 
          ? 'opacity-0' 
          : 'opacity-0 group-hover:opacity-100 bg-gradient-to-br from-purple-500/5 to-indigo-500/5'
        }
      `}></div>
    </div>
  );
}
