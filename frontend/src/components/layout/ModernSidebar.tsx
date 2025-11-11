/**
 * Modern Collapsible Sidebar Component
 * Clean, modern sidebar with smooth animations
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Home, 
  TrendingUp, 
  Brain, 
  Trophy, 
  Heart, 
  Book, 
  Mic, 
  Users, 
  MessageCircle,
  ChevronLeft,
  ChevronRight,
  Menu,
  X
} from 'lucide-react';

interface ModernSidebarProps {
  className?: string;
}

export const ModernSidebar: React.FC<ModernSidebarProps> = ({ className = '' }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const navigationItems = [
    {
      section: 'MAIN',
      items: [
        { icon: Home, label: 'Dashboard', href: '/dashboard', active: false },
        { icon: TrendingUp, label: 'Insights', href: '/insights', active: false },
        { icon: Brain, label: 'Crisis Monitor', href: '/crisis', active: false, badge: 'AI' },
      ]
    },
    {
      section: 'WELLNESS',
      items: [
        { icon: Trophy, label: 'Achievements', href: '/achievements', active: false },
        { icon: Heart, label: 'Mood Tracker', href: '/mood', active: true },
        { icon: Book, label: 'Journal', href: '/journal', active: false },
        { icon: Mic, label: 'Voice Testing', href: '/voice', active: false },
      ]
    },
    {
      section: 'SOCIAL',
      items: [
        { icon: Users, label: 'Community', href: '/community', active: false },
      ]
    }
  ];

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="sm"
        className="lg:hidden fixed top-4 left-4 z-50"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </Button>

      {/* Sidebar */}
      <div className={`
        fixed left-0 top-0 h-full bg-white border-r border-gray-200 z-40
        transition-all duration-300 ease-in-out
        ${isCollapsed ? 'w-16' : 'w-64'}
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        ${className}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              {!isCollapsed && (
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">M</span>
                  </div>
                  <div>
                    <h1 className="font-bold text-lg">MantraPath</h1>
                    <p className="text-sm text-gray-600">Welcome, sachin!</p>
                  </div>
                </div>
              )}
              {isCollapsed && (
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-white font-bold text-sm">M</span>
                </div>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="hidden lg:flex h-8 w-8 p-0"
              >
                {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
              </Button>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto py-4">
            {navigationItems.map((section, sectionIndex) => (
              <div key={sectionIndex} className="mb-6">
                {!isCollapsed && (
                  <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    {section.section}
                  </h3>
                )}
                <div className="space-y-1">
                  {section.items.map((item, itemIndex) => (
                    <Button
                      key={itemIndex}
                      variant={item.active ? "default" : "ghost"}
                      className={`
                        w-full justify-start h-10 px-4 mx-2
                        ${item.active ? 'bg-orange-100 text-orange-700 border-orange-200' : 'hover:bg-gray-100'}
                        ${isCollapsed ? 'px-2' : ''}
                      `}
                    >
                      <item.icon className={`w-5 h-5 ${isCollapsed ? 'mx-auto' : 'mr-3'}`} />
                      {!isCollapsed && (
                        <div className="flex items-center justify-between w-full">
                          <span>{item.label}</span>
                          {item.badge && (
                            <Badge variant="secondary" className="text-xs">
                              {item.badge}
                            </Badge>
                          )}
                        </div>
                      )}
                    </Button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
              {!isCollapsed && (
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Connected</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-gray-600">S</span>
                    </div>
                    <span className="text-xs text-gray-600">sachin</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
    </>
  );
};


