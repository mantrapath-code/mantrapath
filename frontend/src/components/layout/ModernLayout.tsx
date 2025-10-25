/**
 * Modern Layout Component
 * Clean, modern layout with collapsible sidebar and floating chat
 */

import React from 'react';
import { ModernSidebar } from './ModernSidebar';
import { FloatingChatButton } from '../chat/FloatingChatButton';

interface ModernLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const ModernLayout: React.FC<ModernLayoutProps> = ({ children, className = '' }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <ModernSidebar />
      
      {/* Main Content */}
      <div className="lg:ml-64 transition-all duration-300 ease-in-out">
        <div className={`min-h-screen ${className}`}>
          {children}
        </div>
      </div>
      
      {/* Floating Chat Button */}
      <FloatingChatButton />
    </div>
  );
};

