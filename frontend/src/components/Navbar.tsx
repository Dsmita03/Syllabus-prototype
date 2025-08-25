export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-6 py-4">
        <nav className="flex items-center justify-between">
          {/* Logo Section */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center shadow-md">
              <span className="text-xl font-bold text-gray-800">E</span>
            </div>
            <span className="text-lg font-semibold text-gray-800 tracking-wide">
              EduModule
            </span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <a 
              href="#home" 
              className="text-gray-700 hover:text-[#BBDCE5] transition-colors font-medium"
            >
              Home
            </a>
            <a 
              href="#features" 
              className="text-gray-700 hover:text-[#BBDCE5] transition-colors font-medium"
            >
              Features
            </a>
            <a 
              href="#how-it-works" 
              className="text-gray-700 hover:text-[#BBDCE5] transition-colors font-medium"
            >
              How it Works
            </a>
          </div>
        </nav>
      </div>
    </header>
  );
}
