/**
 * Mood Service Test Page - Simplified Version
 * Redirects to the optimized mood page
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, ExternalLink, ArrowRight } from 'lucide-react';
import { OptimizedMoodPage } from './OptimizedMoodPage';

export const MoodTestPage: React.FC = () => {
  const [showOptimized, setShowOptimized] = React.useState(false);

  if (showOptimized) {
    return <OptimizedMoodPage />;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Mood Service Test Page
        </h1>
        <p className="text-gray-600">
          This page has been replaced with an optimized mood experience
        </p>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-3">
            <p>
              The old mood components have been consolidated into a single, optimized experience.
              The new page includes:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Real-time wellness scoring</li>
              <li>Dynamic mood-based theming</li>
              <li>Simplified mood entry interface</li>
              <li>Integrated analytics and patterns</li>
              <li>No duplicate components</li>
            </ul>
          </div>
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ExternalLink className="w-6 h-6 text-blue-600" />
            Use the Optimized Mood Page
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-4">
            The new optimized mood page provides a cleaner, more user-friendly experience
            with real backend data integration and no mock responses.
          </p>
          <Button 
            onClick={() => setShowOptimized(true)}
            className="w-full"
          >
            Open Optimized Mood Page
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};