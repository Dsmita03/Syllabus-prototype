import { BookOpen, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-[#ECEEDF] border-t border-[#D9C4B0]/30 mt-24">
      <div className="container mx-auto px-6 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Logo & Description */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center shadow-md">
                <BookOpen className="w-6 h-6 text-gray-800" />
              </div>
              <span className="text-xl font-semibold text-gray-800">EduModule</span>
            </div>
            <p className="text-gray-600 max-w-md mb-6">
              Transform your syllabus into smart learning modules with AI-powered educational technology.
            </p>
            <div className="flex space-x-4">
              <button className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center hover:bg-[#a5cfd8] transition-colors">
                <Mail className="w-5 h-5 text-gray-800" />
              </button>
              <button className="w-10 h-10 bg-[#BBDCE5] rounded-lg flex items-center justify-center hover:bg-[#a5cfd8] transition-colors">
                <Phone className="w-5 h-5 text-gray-800" />
              </button>
            </div>
          </div>
          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-4">Quick Links</h3>
            <ul className="space-y-2">
              {['Home', 'Features', 'How it Works', 'About'].map((link) => (
                <li key={link}>
                  <a href={`#${link.toLowerCase().replace(' ', '-')}`} 
                     className="text-gray-600 hover:text-[#BBDCE5] transition-colors">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          {/* Contact */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-4">Contact</h3>
            <div className="space-y-2 text-gray-600">
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-2" />
                <span className="text-sm">Kolkata</span>
              </div>
              <div className="flex items-center">
                <Mail className="w-4 h-4 mr-2" />
                <span className="text-sm">edumodule@gmail.com</span>
              </div>
            </div>
          </div>
        </div>
        <div className="border-t border-[#D9C4B0]/30 mt-8 pt-8 text-center">
          <p className="text-gray-600 text-sm">
            © 2025 EduModule. All rights reserved.  
          </p>
        </div>
      </div>
    </footer>
  );
}
