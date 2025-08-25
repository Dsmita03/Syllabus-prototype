import { HelpCircle, Clock, CheckCircle, Bookmark } from 'lucide-react';

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
  isCompleted?: boolean;
  isBookmarked?: boolean;
  onBookmark?: () => void;
  onComplete?: () => void;
}

export default function ModuleCard({ 
  module, 
  isSelected, 
  onClick, 
  index, 
  isCompleted = false, 
  isBookmarked = false, 
  onBookmark, 
  onComplete 
}: ModuleCardProps) {
  const questionCount = module.questions?.length || 0;
  const readingTime = Math.ceil(module.content.split(' ').length / 200);

  const handleBookmarkClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onBookmark?.();
  };

  const handleCompleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onComplete?.();
  };

  return (
    <div
      onClick={onClick}
      className={`
        group relative overflow-hidden rounded-xl cursor-pointer transition-all duration-200 border
        ${isSelected
          ? 'bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] text-gray-900 shadow-lg border-[#BBDCE5] scale-[1.03]'
          : 'bg-white hover:bg-[#BBDCE5]/10 text-gray-900 shadow-sm border-[#ECEEDF] hover:border-[#BBDCE5]/60'
        }
      `}
      style={{ minHeight: 120 }}
    >
      <div className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-3">
            <div className={`
              w-9 h-9 rounded-lg flex items-center justify-center font-bold text-base
              ${isSelected ? 'bg-[#ECEEDF] text-[#BBDCE5]' : 'bg-[#BBDCE5] text-white'}
            `}>
              {index + 1}
            </div>
            <h3 className={`font-bold text-base truncate ${isSelected ? 'text-[#CFAB8D]' : 'text-gray-900'}`}>
              {module.title}
            </h3>
          </div>

          <div className="flex items-center space-x-2">
            {isCompleted && (
              <CheckCircle className="w-4 h-4 text-green-500" />
            )}
            {isBookmarked && (
              <Bookmark className="w-3.5 h-3.5 text-[#CFAB8D]" />
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center space-x-4 mb-2">
          <div className={`flex items-center text-xs font-semibold ${isSelected ? 'text-[#BBDCE5]' : 'text-[#D9C4B0]'}`}>
            <HelpCircle className="w-4 h-4 mr-1" />
            {questionCount} Qs
          </div>
          <div className={`flex items-center text-xs font-semibold ${isSelected ? 'text-[#CFAB8D]' : 'text-[#BBDCE5]'}`}>
            <Clock className="w-4 h-4 mr-1" />
            {readingTime} min
          </div>
        </div>

        {/* Content Preview */}
        <p className={`text-xs leading-snug mb-4 ${isSelected ? 'text-[#CFAB8D]' : 'text-gray-600'}`}>
          {module.content.substring(0, 90)}...
        </p>

        {/* Bottom Row */}
        <div className="flex items-center justify-between">
          {/* Progress bar (accent) */}
          <div className="flex-1 mr-3">
            <div className={`w-full h-1 rounded-full bg-[#ECEEDF]`}>
              <div 
                className={`
                  h-full rounded-full transition-all duration-300
                  ${isCompleted ? 'bg-green-400 w-full' : 'bg-[#BBDCE5] w-1/4'}
                `}
              />
            </div>
          </div>
          {/* Actions */}
          <div className="flex space-x-1">
            {onBookmark && (
              <button
                onClick={handleBookmarkClick}
                className={`p-2 rounded-lg transition-colors border border-transparent hover:border-[#CFAB8D] ${
                  isBookmarked
                    ? 'bg-[#CFAB8D]/20 text-[#CFAB8D]'
                    : isSelected
                    ? 'text-[#CFAB8D] hover:bg-[#CFAB8D]/10'
                    : 'text-[#D9C4B0] hover:bg-[#CFAB8D]/10'
                }`}
                title={isBookmarked ? 'Remove bookmark' : 'Bookmark'}
              >
                <Bookmark className="w-4 h-4" />
              </button>
            )}
            {onComplete && (
              <button
                onClick={handleCompleteClick}
                className={`p-2 rounded-lg transition-colors border border-transparent hover:border-green-400 ${
                  isCompleted
                    ? 'bg-green-50 text-green-600'
                    : isSelected
                    ? 'text-green-600 hover:bg-green-50'
                    : 'text-gray-400 hover:text-green-600 hover:bg-green-50'
                }`}
                title={isCompleted ? 'Mark as incomplete' : 'Mark complete'}
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Gradient accent for hover */}
      {!isSelected && (
        <div className="absolute inset-0 bg-gradient-to-r from-[#BBDCE5]/10 to-[#CFAB8D]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
      )}
    </div>
  );
}
