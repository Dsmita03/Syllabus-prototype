import FileUpload from '@/components/FileUpload';
import { BookOpen, Zap, Target, Sparkles, ArrowRight, Star, Brain, Layers, Rocket } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 overflow-hidden relative">
      {/* Advanced Background Art */}
      <div className="absolute inset-0">
        {/* Animated Gradient Orbs */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-purple-400/30 to-indigo-400/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-r from-indigo-400/30 to-purple-400/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-gradient-to-r from-blue-300/20 to-cyan-300/20 rounded-full blur-2xl animate-pulse delay-500"></div>
        
        {/* Floating Geometric Shapes */}
        <div className="absolute top-32 right-1/4 w-8 h-8 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg rotate-45 animate-bounce opacity-20"></div>
        <div className="absolute bottom-40 left-1/4 w-6 h-6 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-full animate-pulse opacity-30"></div>
        <div className="absolute top-3/4 right-1/3 w-4 h-4 bg-gradient-to-r from-blue-500 to-cyan-500 transform rotate-12 animate-spin-slow opacity-20"></div>
        
        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 opacity-5">
          <div className="w-full h-full" style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, rgb(139 92 246) 1px, transparent 0)`,
            backgroundSize: '40px 40px'
          }}></div>
        </div>
      </div>

      {/* Floating Navigation */}
      <header className="relative z-10 py-8 px-4">
        <div className="container mx-auto">
          <nav className="flex items-center justify-between bg-white/70 backdrop-blur-xl rounded-2xl px-6 py-4 shadow-lg border border-white/20">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-6 h-6 text-white animate-pulse" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-ping"></div>
              </div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  EduModule
                </span>
                <div className="text-xs text-purple-500 font-medium">AI-Powered Learning</div>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-purple-600 transition-all duration-300 font-medium relative group">
                Features
                <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-600 to-indigo-600 group-hover:w-full transition-all duration-300"></div>
              </a>
              <a href="#how-it-works" className="text-gray-700 hover:text-purple-600 transition-all duration-300 font-medium relative group">
                How it Works
                <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-600 to-indigo-600 group-hover:w-full transition-all duration-300"></div>
              </a>
              <button className="group bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-2xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <span className="relative flex items-center">
                  Get Started
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
                </span>
              </button>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section with Advanced Animations */}
      <main className="relative z-10 py-16 px-4">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-20">
            {/* Animated Badge */}
            <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 rounded-full text-sm font-medium mb-8 animate-fade-in border border-purple-200 shadow-lg">
              <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full animate-pulse mr-3"></div>
              <Star className="w-4 h-4 mr-2 animate-spin-slow" />
              Revolutionary AI-Powered Educational Tool
              <Sparkles className="w-4 h-4 ml-2 animate-pulse" />
            </div>
            
            {/* Animated Main Heading */}
            <h1 className="text-6xl md:text-8xl font-extrabold text-gray-900 mb-10 leading-tight">
              <div className="animate-slide-up">
                Transform Your{' '}
                <div className="relative inline-block">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 animate-gradient-x">
                    Syllabus
                  </span>
                  <div className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full animate-pulse"></div>
                </div>
              </div>
              <div className="animate-slide-up delay-300">
                Into Smart{' '}
                <div className="relative inline-block">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 animate-gradient-x">
                    Modules
                  </span>
                  <div className="absolute top-0 -right-8 text-2xl animate-bounce">✨</div>
                </div>
              </div>
            </h1>
            
            {/* Enhanced Description */}
            <p className="text-2xl md:text-3xl text-gray-600 max-w-5xl mx-auto mb-12 leading-relaxed animate-slide-up delay-500">
              Upload any syllabus and watch our{' '}
              <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 animate-pulse">
                Advanced AI
              </span>{' '}
              instantly break it down into organized learning modules with automatically generated questions.
            </p>

            {/* Animated Feature Badges */}
            <div className="flex flex-wrap items-center justify-center gap-8 mb-20">
              {[
                { icon: Zap, text: 'Lightning Fast Processing', color: 'from-yellow-400 to-orange-500' },
                { icon: Brain, text: 'Smart AI Analysis', color: 'from-green-400 to-emerald-500' },
                { icon: Layers, text: 'Structured Modules', color: 'from-blue-400 to-cyan-500' },
                { icon: Rocket, text: 'Instant Results', color: 'from-purple-400 to-pink-500' }
              ].map((feature, index) => (
                <div key={index} className={`group flex items-center px-8 py-4 bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/40 hover:shadow-2xl transition-all duration-500 transform hover:scale-110 animate-fade-in delay-[${700 + index * 200}ms]`}>
                  <div className={`w-6 h-6 mr-4 text-white p-1 rounded-lg bg-gradient-to-r ${feature.color} group-hover:animate-pulse`}>
                    <feature.icon className="w-full h-full" />
                  </div>
                  <span className="font-semibold text-gray-700 group-hover:text-gray-900 transition-colors duration-300">
                    {feature.text}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Enhanced File Upload with Floating Animation */}
          <div className="animate-float">
            <FileUpload />
          </div>

          {/* Features Section with Advanced Cards */}
          <section id="features" className="mt-40">
            <div className="text-center mb-24">
              <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 rounded-full text-sm font-medium mb-8 animate-bounce">
                <Sparkles className="w-5 h-5 mr-2 animate-spin-slow" />
                Powerful Features
              </div>
              <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
                Everything You Need for{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 animate-gradient-x">
                  Better Learning
                </span>
              </h2>
              <p className="text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
                Powerful features designed to enhance your educational experience and streamline learning
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-10">
              {[
                {
                  icon: BookOpen,
                  title: 'Smart Module Division',
                  description: 'Our advanced AI analyzes your syllabus content and intelligently divides it into logical, digestible learning modules for optimal comprehension.',
                  gradient: 'from-purple-500 to-indigo-600',
                  bgGradient: 'from-purple-50 to-indigo-50',
                  delay: '0ms'
                },
                {
                  icon: Target,
                  title: 'Multi-Level Questions',
                  description: 'Generate questions at easy, medium, and hard difficulty levels including multiple choice, short answer, and comprehensive essay questions.',
                  gradient: 'from-indigo-500 to-purple-600',
                  bgGradient: 'from-indigo-50 to-purple-50',
                  delay: '200ms'
                },
                {
                  icon: Zap,
                  title: 'Instant Processing',
                  description: 'Lightning-fast AI-powered analysis that processes your documents in seconds, not hours. Get comprehensive results instantly.',
                  gradient: 'from-blue-500 to-indigo-600',
                  bgGradient: 'from-blue-50 to-indigo-50',
                  delay: '400ms'
                }
              ].map((feature, index) => (
                <div key={index} className={`group bg-white/90 backdrop-blur-sm rounded-3xl p-10 border border-white/60 shadow-2xl hover:shadow-3xl transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 animate-slide-up delay-[${feature.delay}] relative overflow-hidden`}>
                  {/* Animated Background Pattern */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div className={`absolute inset-0 bg-gradient-to-br ${feature.bgGradient} animate-pulse`}></div>
                  </div>
                  
                  <div className="relative z-10">
                    <div className={`w-20 h-20 bg-gradient-to-r ${feature.gradient} rounded-3xl flex items-center justify-center mb-8 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-lg`}>
                      <feature.icon className="w-10 h-10 text-white group-hover:animate-pulse" />
                    </div>
                    <h3 className="text-3xl font-bold mb-6 text-gray-900 group-hover:text-purple-900 transition-colors duration-300">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed text-lg mb-6 group-hover:text-gray-700 transition-colors duration-300">
                      {feature.description}
                    </p>
                    <div className="flex items-center text-purple-600 font-semibold group-hover:text-purple-700 transition-colors duration-300">
                      Learn more 
                      <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-2 transition-transform duration-300" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* How It Works with Interactive Steps */}
          <section id="how-it-works" className="mt-40">
            <div className="text-center mb-24">
              <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
                How It{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 animate-gradient-x">
                  Works
                </span>
              </h2>
              <p className="text-2xl text-gray-600 max-w-4xl mx-auto">
                Simple 3-step process to transform your syllabus into interactive learning modules
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-12 relative">
              {/* Connection Lines */}
              <div className="hidden md:block absolute top-1/2 left-1/3 right-1/3 h-0.5 bg-gradient-to-r from-purple-300 to-indigo-300 animate-pulse"></div>
              
              {[
                {
                  step: '01',
                  title: 'Upload Syllabus',
                  description: 'Simply drag and drop your PDF or text syllabus file into our secure upload area',
                  icon: '📄',
                  color: 'from-purple-400 to-indigo-500'
                },
                {
                  step: '02', 
                  title: 'AI Processing',
                  description: 'Our advanced AI analyzes and intelligently divides content into logical learning modules',
                  icon: '🤖',
                  color: 'from-indigo-400 to-blue-500'
                },
                {
                  step: '03',
                  title: 'Get Results',
                  description: 'Receive beautifully organized modules with automatically generated questions at multiple difficulty levels',
                  icon: '✨',
                  color: 'from-blue-400 to-purple-500'
                }
              ].map((item, index) => (
                <div key={index} className={`text-center group animate-slide-up delay-[${index * 300}ms] relative`}>
                  <div className="relative mb-8">
                    <div className={`w-28 h-28 bg-gradient-to-r ${item.color} rounded-full flex items-center justify-center mx-auto text-5xl shadow-2xl group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 relative z-10`}>
                      {item.icon}
                    </div>
                    <div className="absolute top-4 left-4 right-4 bottom-4 bg-white/20 rounded-full animate-ping"></div>
                  </div>
                  <div className={`text-sm font-bold bg-gradient-to-r ${item.color} bg-clip-text text-transparent mb-4 tracking-widest`}>
                    STEP {item.step}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6 group-hover:text-purple-900 transition-colors duration-300">
                    {item.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed text-lg group-hover:text-gray-700 transition-colors duration-300">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Enhanced CTA Section */}
          <section className="mt-40 text-center">
            <div className="relative bg-gradient-to-r from-purple-600 to-indigo-600 rounded-3xl p-16 text-white overflow-hidden shadow-2xl">
              {/* Animated Background */}
              <div className="absolute inset-0">
                <div className="absolute top-10 left-10 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
                <div className="absolute bottom-10 right-10 w-40 h-40 bg-white/10 rounded-full blur-xl animate-pulse delay-1000"></div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-white/5 rounded-full blur-lg animate-spin-slow"></div>
              </div>
              
              <div className="relative z-10">
                <h2 className="text-4xl md:text-5xl font-bold mb-8 animate-bounce">
                  Ready to Transform Your Learning?
                </h2>
                <p className="text-2xl mb-10 opacity-90 leading-relaxed">
                  Join thousands of educators and students using EduModule to revolutionize education
                </p>
                <button className="group bg-white text-purple-600 px-12 py-5 rounded-3xl font-bold text-xl hover:bg-gray-100 transition-all duration-300 transform hover:scale-110 shadow-2xl relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-indigo-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <span className="relative flex items-center">
                    Get Started for Free
                    <Rocket className="w-6 h-6 ml-3 group-hover:translate-x-2 group-hover:-translate-y-1 transition-transform duration-300" />
                  </span>
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
