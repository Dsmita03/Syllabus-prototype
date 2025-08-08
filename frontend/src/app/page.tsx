import FileUpload from '@/components/FileUpload';
import Navbar from '@/components/Navbar';
import { Zap, Target, ArrowRight, Upload, CheckCircle, Users, Sparkles, BookOpen } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 overflow-hidden relative">
      {/* Subtle Background Art */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-purple-400/20 to-indigo-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-r from-indigo-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Navigation Component */}
      <Navbar />

      {/* Professional Hero Section */}
      <main className="relative z-10 py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            {/* Clean Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 rounded-full text-sm font-medium mb-8 border border-purple-200 shadow-lg animate-fade-in">
              <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full animate-pulse mr-2"></div>
              <Sparkles className="w-4 h-4 mr-2" />
              AI-Powered Educational Tool
            </div>
            
            {/* Clean Main Heading */}
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8 leading-tight animate-slide-up">
              Transform Your{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 animate-gradient-x">
                Syllabus
              </span>
              <br />
              Into Smart{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 animate-gradient-x">
                Learning Modules
              </span>
            </h1>
            
            {/* Simple Description */}
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12 leading-relaxed animate-slide-up delay-300">
              Upload any syllabus and our{' '}
              <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">
                Advanced AI
              </span>{' '}
              instantly breaks it down into organized learning modules 
              with automatically generated questions for better educational outcomes.
            </p>

            {/* Clean Feature Badges */}
            <div className="flex flex-wrap items-center justify-center gap-6 mb-16">
              {[
                { icon: Zap, text: 'Fast Processing', color: 'from-yellow-400 to-orange-500' },
                { icon: CheckCircle, text: 'Accurate Analysis', color: 'from-green-400 to-emerald-500' },
                { icon: Users, text: 'Educator Approved', color: 'from-blue-400 to-cyan-500' }
              ].map((feature, index) => (
                <div key={index} className="group flex items-center px-6 py-3 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/40 hover:shadow-xl transition-all duration-300 transform hover:scale-105 animate-fade-in" style={{ animationDelay: `${500 + index * 200}ms` }}>
                  <div className={`w-5 h-5 mr-3 text-white p-1 rounded-lg bg-gradient-to-r ${feature.color} group-hover:animate-pulse`}>
                    <feature.icon className="w-full h-full" />
                  </div>
                  <span className="font-medium text-gray-700 group-hover:text-gray-900 transition-colors">{feature.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* File Upload */}
          <div className="mb-20">
            <FileUpload />
          </div>

          {/* Professional Features Section */}
          <section id="features" className="mt-24">
            <div className="text-center mb-16">
              <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 rounded-full text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4 mr-2 animate-pulse" />
                Powerful Features
              </div>
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Everything You Need for{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">
                  Better Learning
                </span>
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Everything you need to transform educational content into engaging learning experiences
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: BookOpen,
                  title: 'Smart Module Division',
                  description: 'AI analyzes your syllabus content and intelligently divides it into logical, digestible learning modules for optimal comprehension.',
                  gradient: 'from-purple-500 to-indigo-600'
                },
                {
                  icon: Target,
                  title: 'Multi-Level Questions',
                  description: 'Generate questions at easy, medium, and hard difficulty levels including multiple choice, short answer, and essay questions.',
                  gradient: 'from-indigo-500 to-purple-600'
                },
                {
                  icon: Zap,
                  title: 'Instant Processing',
                  description: 'Lightning-fast AI-powered analysis that processes your documents in seconds. Get comprehensive results instantly.',
                  gradient: 'from-blue-500 to-indigo-600'
                }
              ].map((feature, index) => (
                <div key={index} className="group bg-white/90 backdrop-blur-sm rounded-2xl p-8 border border-white/60 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 animate-slide-up" style={{ animationDelay: `${index * 200}ms` }}>
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold mb-4 text-gray-900 group-hover:text-purple-900 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed mb-4 group-hover:text-gray-700 transition-colors">
                    {feature.description}
                  </p>
                  <div className="flex items-center text-purple-600 font-medium group-hover:text-purple-700 transition-colors">
                    Learn more 
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* How It Works Section */}
          <section id="how-it-works" className="mt-24">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                How It{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">
                  Works
                </span>
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Simple 3-step process to transform your syllabus into interactive learning modules
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 relative">
              {[
                {
                  step: '1',
                  title: 'Upload Syllabus',
                  description: 'Simply drag and drop your PDF or text syllabus file into our secure upload area',
                  icon: Upload,
                  color: 'from-purple-500 to-indigo-600'
                },
                {
                  step: '2', 
                  title: 'AI Processing',
                  description: 'Our advanced AI analyzes and intelligently divides content into logical learning modules',
                  icon: Zap,
                  color: 'from-indigo-500 to-blue-600'
                },
                {
                  step: '3',
                  title: 'Get Results',
                  description: 'Receive beautifully organized modules with automatically generated questions at multiple difficulty levels',
                  icon: CheckCircle,
                  color: 'from-blue-500 to-purple-600'
                }
              ].map((item, index) => (
                <div key={index} className="text-center group animate-slide-up relative z-10" style={{ animationDelay: `${index * 300}ms` }}>
                  <div className="relative mb-8">
                    <div className={`w-20 h-20 bg-gradient-to-r ${item.color} rounded-full flex items-center justify-center mx-auto shadow-xl group-hover:scale-110 group-hover:rotate-6 transition-all duration-500`}>
                      <item.icon className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg border-2 border-purple-200">
                      <span className="text-sm font-bold text-purple-600">{item.step}</span>
                    </div>
                    <div className="absolute top-2 left-2 right-2 bottom-2 bg-white/20 rounded-full animate-ping"></div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4 group-hover:text-purple-900 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed group-hover:text-gray-700 transition-colors">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Professional CTA Section */}
          <section className="mt-24 text-center">
            <div className="relative bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-12 text-white overflow-hidden shadow-2xl">
              {/* Subtle Animated Background */}
              <div className="absolute inset-0">
                <div className="absolute top-10 left-10 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
                <div className="absolute bottom-10 right-10 w-40 h-40 bg-white/10 rounded-full blur-xl animate-pulse delay-1000"></div>
              </div>
              
              <div className="relative z-10">
                <h2 className="text-3xl font-bold mb-4">
                  Ready to Transform Your Learning?
                </h2>
                <p className="text-xl mb-8 opacity-90">
                  Join thousands of educators using EduModule to enhance education
                </p>
                <button className="group bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-xl">
                  <span className="flex items-center">
                    Get Started for Free
                    <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
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
