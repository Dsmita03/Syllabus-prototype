import { HelpCircle, CheckCircle, FileText } from 'lucide-react';

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
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'hard':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold mb-6">Generated Questions ({questions.length})</h3>
      
      <div className="space-y-6">
        {questions.map((question, index) => (
          <div key={question.id} className="border-l-4 border-blue-500 pl-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-blue-600">{getQuestionIcon(question.type)}</span>
                <span className="font-medium text-gray-900">Question {index + 1}</span>
              </div>
              <div className="flex space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
                  {question.difficulty}
                </span>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                  {question.type.replace('-', ' ')}
                </span>
              </div>
            </div>
            
            <p className="text-gray-800 mb-3">{question.question}</p>
            
            {question.options && (
              <div className="ml-4 space-y-1">
                {question.options.map((option, optionIndex) => (
                  <div key={optionIndex} className="text-sm text-gray-600">
                    <span className="font-medium">{String.fromCharCode(65 + optionIndex)})</span> {option}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
