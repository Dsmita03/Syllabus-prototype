import { HelpCircle,FileText, Target, Clock, Star, ChevronRight } from 'lucide-react';

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
        return <Target className="w-5 h-5" />;
      case 'essay':
        return <FileText className="w-5 h-5" />;
      default:
        return <HelpCircle className="w-5 h-5" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-green-700 bg-green-100 border-green-200';
      case 'medium':
        return 'text-orange-700 bg-orange-100 border-orange-200';
      case 'hard':
        return 'text-red-700 bg-red-100 border-red-200';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-200';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'multiple-choice':
        return 'text-[#BBDCE5] bg-[#BBDCE5]/20 border-[#BBDCE5]/30';
      case 'essay':
        return 'text-[#D9C4B0] bg-[#D9C4B0]/20 border-[#D9C4B0]/30';
      default:
        return 'text-[#CFAB8D] bg-[#CFAB8D]/20 border-[#CFAB8D]/30';
    }
  };

  const getTypeDisplayName = (type: string) => {
    switch (type) {
      case 'multiple-choice':
        return 'Multiple Choice';
      case 'short-answer':
        return 'Short Answer';
      case 'essay':
        return 'Essay';
      default:
        return type;
    }
  };

  return (
    <div className="space-y-6">
      {questions.map((question, index) => (
        <div 
          key={question.id} 
          className="bg-white/90 backdrop-blur-sm rounded-2xl border border-[#D9C4B0]/20 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group"
        >
          {/* Question Header */}
          <div className="bg-gradient-to-r from-[#ECEEDF] to-[#BBDCE5]/20 px-6 py-4 border-b border-[#D9C4B0]/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  {index + 1}
                </div>
                <div className="flex items-center space-x-3">
                  <div className="text-[#BBDCE5]">
                    {getQuestionIcon(question.type)}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">Question {index + 1}</h3>
                    <p className="text-sm text-gray-600">Practice Assessment</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <span className={`px-4 py-2 rounded-full text-sm font-semibold border ${getDifficultyColor(question.difficulty)}`}>
                  {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                </span>
                <span className={`px-4 py-2 rounded-full text-sm font-semibold border ${getTypeColor(question.type)}`}>
                  {getTypeDisplayName(question.type)}
                </span>
              </div>
            </div>
          </div>
          
          {/* Question Content */}
          <div className="p-6">
            {/* Question Text */}
            <div className="mb-6">
              <div className="bg-gradient-to-r from-[#ECEEDF]/30 to-[#BBDCE5]/10 rounded-xl p-6 border border-[#D9C4B0]/20">
                <p className="text-gray-800 text-lg leading-relaxed font-medium">
                  {question.question}
                </p>
              </div>
            </div>
            
            {/* Multiple Choice Options */}
            {question.options && question.options.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2 text-gray-700 mb-4">
                  <Target className="w-5 h-5 text-[#BBDCE5]" />
                  <span className="font-semibold">Choose the correct answer:</span>
                </div>
                
                <div className="grid gap-3">
                  {question.options.map((option, optionIndex) => (
                    <div 
                      key={optionIndex} 
                      className="group/option flex items-center space-x-4 p-4 bg-white rounded-xl border border-[#D9C4B0]/30 hover:border-[#BBDCE5] hover:bg-[#BBDCE5]/5 transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md"
                    >
                      {/* Option Letter */}
                      <div className="w-10 h-10 rounded-full border-2 border-[#D9C4B0]/50 group-hover/option:border-[#BBDCE5] group-hover/option:bg-[#BBDCE5]/10 flex items-center justify-center flex-shrink-0 transition-all duration-200">
                        <span className="text-lg font-bold text-[#BBDCE5] group-hover/option:text-[#BBDCE5]">
                          {String.fromCharCode(65 + optionIndex)}
                        </span>
                      </div>
                      
                      {/* Option Text */}
                      <span className="text-gray-700 group-hover/option:text-gray-900 font-medium text-lg flex-1">
                        {option}
                      </span>
                      
                      {/* Hover Arrow */}
                      <ChevronRight className="w-5 h-5 text-[#D9C4B0] group-hover/option:text-[#BBDCE5] opacity-0 group-hover/option:opacity-100 transition-all duration-200 transform group-hover/option:translate-x-1" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Short Answer / Essay Prompt */}
            {question.type !== 'multiple-choice' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2 text-gray-700 mb-4">
                  <FileText className="w-5 h-5 text-[#D9C4B0]" />
                  <span className="font-semibold">
                    {question.type === 'essay' ? 'Write your essay response:' : 'Provide your answer:'}
                  </span>
                </div>
                
                <div className="bg-[#ECEEDF]/20 rounded-xl p-4 border-2 border-dashed border-[#D9C4B0]/30">
                  <p className="text-gray-600 text-center py-8">
                    {question.type === 'essay' 
                      ? 'Click to start writing your detailed essay response...' 
                      : 'Click to enter your short answer...'
                    }
                  </p>
                </div>
              </div>
            )}

            {/* Question Footer */}
            <div className="flex items-center justify-between pt-6 border-t border-[#D9C4B0]/20 mt-6">
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-[#BBDCE5]" />
                  <span className="font-medium">
                    {question.type === 'essay' ? '10-15 min' : question.type === 'short-answer' ? '3-5 min' : '2-3 min'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Star className="w-4 h-4 text-[#CFAB8D]" />
                  <span className="font-medium">Practice Question</span>
                </div>
              </div>
              
              <button className="px-6 py-3 bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] text-white font-semibold rounded-xl hover:from-[#a5cfd8] hover:to-[#c7b5a0] transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center space-x-2">
                <span>
                  {question.type === 'multiple-choice' ? 'Submit Answer' : 'Start Writing'}
                </span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}

      {/* Questions Summary */}
      {questions.length > 0 && (
        <div className="bg-gradient-to-r from-[#ECEEDF] to-[#BBDCE5]/20 rounded-2xl p-6 border border-[#D9C4B0]/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-[#BBDCE5] to-[#D9C4B0] rounded-xl flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h4 className="font-bold text-gray-900 text-lg">Assessment Complete</h4>
                <p className="text-gray-600">{questions.length} questions ready for practice</p>
              </div>
            </div>
            
            <button className="px-8 py-3 bg-white text-[#BBDCE5] font-bold rounded-xl hover:bg-[#BBDCE5] hover:text-white transition-all duration-200 shadow-lg border-2 border-[#BBDCE5]">
              Start Quiz Mode
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
