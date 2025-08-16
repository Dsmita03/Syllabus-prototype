import { HelpCircle, CheckCircle, FileText, Target, Clock, Star } from 'lucide-react';

interface Question {
  id: string;
  question: string;
  type: 'multiple-choice' | 'short-answer' | 'essay';
  difficulty: 'easy' | 'medium' | 'hard';
  options?: string[];
}

interface QuestionListProps {
  questions: Question[];
}

export default function QuestionList({ questions }: QuestionListProps) {
  const getQuestionIcon = (type: string) => {
    switch (type) {
      case 'multiple-choice':
        return <CheckCircle className="w-5 h-5" />;
      case 'essay':
        return <FileText className="w-5 h-5" />;
      default:
        return <HelpCircle className="w-5 h-5" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-emerald-600 bg-emerald-100 border-emerald-200';
      case 'medium':
        return 'text-amber-600 bg-amber-100 border-amber-200';
      case 'hard':
        return 'text-red-600 bg-red-100 border-red-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'multiple-choice':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'essay':
        return 'text-purple-600 bg-purple-100 border-purple-200';
      default:
        return 'text-indigo-600 bg-indigo-100 border-indigo-200';
    }
  };

  return (
    <div className="space-y-6">
      {questions.map((question, index) => (
        <div key={question.id} className="bg-gradient-to-r from-slate-50 to-blue-50 rounded-2xl p-6 border border-slate-200/50 shadow-sm hover:shadow-md transition-all duration-200">
          {/* Question Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                {index + 1}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-blue-600">{getQuestionIcon(question.type)}</span>
                <span className="font-semibold text-slate-900">Question {index + 1}</span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <span className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${getDifficultyColor(question.difficulty)}`}>
                {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
              </span>
              <span className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${getTypeColor(question.type)}`}>
                {question.type.replace('-', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </span>
            </div>
          </div>
          
          {/* Question Text */}
          <div className="mb-4">
            <p className="text-slate-800 text-lg leading-relaxed font-medium">{question.question}</p>
          </div>
          
          {/* Question Options */}
          {question.options && question.options.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-sm text-slate-600 mb-2">
                <Target className="w-4 h-4" />
                <span className="font-medium">Select the correct answer:</span>
              </div>
              <div className="grid gap-2">
                {question.options.map((option, optionIndex) => (
                  <div 
                    key={optionIndex} 
                    className="flex items-center space-x-3 p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 cursor-pointer group"
                  >
                    <div className="w-6 h-6 rounded-full border-2 border-slate-300 group-hover:border-blue-400 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-bold text-slate-600 group-hover:text-blue-600">
                        {String.fromCharCode(65 + optionIndex)}
                      </span>
                    </div>
                    <span className="text-slate-700 group-hover:text-slate-900 font-medium">
                      {option}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Question Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-200/50">
            <div className="flex items-center space-x-4 text-sm text-slate-500">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>2-3 min</span>
              </div>
              <div className="flex items-center space-x-1">
                <Star className="w-4 h-4" />
                <span>Practice question</span>
              </div>
            </div>
            
            <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 transform hover:scale-105">
              Check Answer
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
