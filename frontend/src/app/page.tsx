import FileUpload from '@/components/FileUpload';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Image from 'next/image';
import { Zap, Target,Upload, CheckCircle, Users, BookOpen, Brain} from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#ECEEDF] via-white to-[#BBDCE5]/30 overflow-hidden relative">
      {/* Subtle Background Art */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-[#BBDCE5]/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#D9C4B0]/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>
      <Navbar />
      {/* Hero Section with Image */}
      <main className="relative z-10 py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-12 items-center mb-16">
            {/* Left Content */}
            <div className="animate-slide-up">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
                Transform Your{' '}
                <span className="text-[#BBDCE5]">Syllabus</span>
                <br />
                Into Smart{' '}
                <span className="text-[#CFAB8D]">Learning Modules</span>
              </h1>
              
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Upload any syllabus and our{' '}
                <span className="font-semibold text-[#BBDCE5]">Advanced AI</span>{' '}
                instantly breaks it down into organized learning modules 
                with automatically generated questions.
              </p>
              {/* Feature Badges */}
              <div className="flex flex-wrap gap-4 mb-8">
                {[
                  { icon: Zap, text: 'Fast Processing', bg: 'bg-[#BBDCE5]/20' },
                  { icon: CheckCircle, text: 'Accurate Analysis', bg: 'bg-[#D9C4B0]/20' },
                  { icon: Users, text: 'Educator Approved', bg: 'bg-[#CFAB8D]/20' }
                ].map((feature, index) => (
                  <div key={index} className={`flex items-center px-4 py-2 ${feature.bg} rounded-full border border-white/40`}>
                    <feature.icon className="w-4 h-4 mr-2 text-gray-700" />
                    <span className="text-sm font-medium text-gray-700">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>
            {/* Right Image */}
            <div className="relative animate-slide-up delay-300">
              <div className="relative w-full h-96 bg-gradient-to-br from-[#BBDCE5]/30 to-[#D9C4B0]/30 rounded-2xl overflow-hidden shadow-2xl">
                <Image
                  src="/home.png"
                  alt="EduModule AI Learning"
                  fill
                  className="object-cover"
                />
              </div>
              <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-[#CFAB8D] rounded-full opacity-30 animate-bounce"></div>
            </div>
          </div>

          {/* File Upload */}
          <div className="mb-20">
            <FileUpload />
          </div>

          {/* Features Section with Images */}
          <section id="features" className="mt-24">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Everything You Need for{' '}
                <span className="text-[#BBDCE5]">Better Learning</span>
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Transform educational content into engaging learning experiences
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: BookOpen,
                  title: 'Smart Module Division',
                  description: 'AI analyzes your syllabus content and intelligently divides it into logical, digestible learning modules.',
                  color: 'bg-[#BBDCE5]',
                  imageAlt: 'Module Division'
                },
                {
                  icon: Target,
                  title: 'Multi-Level Questions',
                  description: 'Generate questions at easy, medium, and hard difficulty levels including multiple choice and essays.',
                  color: 'bg-[#D9C4B0]',
                  imageAlt: 'Question Generation'
                },
                {
                  icon: Zap,
                  title: 'Instant Processing',
                  description: 'Lightning-fast AI analysis that processes your documents in seconds with comprehensive results.',
                  color: 'bg-[#CFAB8D]',
                  imageAlt: 'Fast Processing'
                }
              ].map((feature, index) => (
                <div key={index} className="group bg-white/90 backdrop-blur-sm rounded-2xl p-6 border border-white/60 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  {/* Feature Image */}
                  <div className="relative w-full h-32 mb-6 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl overflow-hidden">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <feature.icon className="w-12 h-12 text-gray-400" />
                      <p className="absolute bottom-2 text-xs text-gray-500">Feature Image</p>
                    </div> 
                    <Image 
                      src={`/feature-${index + 1}.png`} 
                      alt={feature.imageAlt} 
                      fill 
                      className="object-cover"
                    />
                  </div>

                  <div className={`w-12 h-12 ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  
                  <h3 className="text-xl font-bold mb-3 text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed mb-4">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </section>

   {/* How It Works Section */}
   <section id="how-it-works" className="mt-24">
   <div className="text-center mb-16">
    <h2 className="text-4xl font-bold text-gray-900 mb-4">
      How It <span className="text-[#BBDCE5]">Works</span>
    </h2>
    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
      Simple 3-step process to transform your syllabus into interactive learning modules
    </p>
  </div>

  <div className="grid md:grid-cols-3 gap-8">
    {[
      {
        step: '1',
        title: 'Upload Syllabus',
        description: 'Simply drag and drop your PDF or text syllabus file into our secure upload area',
        icon: Upload,
        color: 'bg-[#BBDCE5]'
      },
      {
        step: '2', 
        title: 'AI Processing',
        description: 'Our advanced AI analyzes and intelligently divides content into logical learning modules',
        icon: Brain,
        color: 'bg-[#D9C4B0]'
      },
      {
        step: '3',
        title: 'Get Results',
        description: 'Receive beautifully organized modules with automatically generated questions',
        icon: CheckCircle,
        color: 'bg-[#CFAB8D]'
      }
    ].map((item, index) => (
      <div key={index} className="text-center group relative">
        <div className="relative mb-6">
          <div className={`w-16 h-16 ${item.color} rounded-full flex items-center justify-center mx-auto shadow-lg group-hover:scale-110 transition-transform duration-300`}>
            <item.icon className="w-8 h-8 text-white" />
          </div>
          <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md border-2 border-[#BBDCE5]/30">
            <span className="text-sm font-bold text-gray-700">{item.step}</span>
          </div>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-4 group-hover:text-[#BBDCE5] transition-colors">
          {item.title}
        </h3>
        <p className="text-gray-600 leading-relaxed group-hover:text-gray-700 transition-colors">
          {item.description}
        </p>
      </div>
    ))}
      </div>
   </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
