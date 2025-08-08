import { BookOpen } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="relative z-10 bg-white/80 backdrop-blur-lg border-b border-white/20">
      <div className="container mx-auto px-4 py-4">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                EduModule
              </span>
              <div className="text-xs text-purple-600 font-medium">AI-Powered Learning</div>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a 
              href="#features" 
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Features
            </a>
            <a 
              href="#how-it-works" 
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              How it Works
            </a>
            <button className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-2 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
              Get Started
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
}
