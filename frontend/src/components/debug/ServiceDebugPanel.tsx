/**
 * Debug component to show real-time service status
 * Helps visualize the current state of connections
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useServiceMonitor } from '@/hooks/useServiceMonitor';
import { RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export const ServiceDebugPanel: React.FC = () => {
  const { services, isMonitoring, checkAllServices, connectionStatus, healthyCount, totalCount, isAllHealthy } = useServiceMonitor();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="text-green-500" size={16} />;
      case 'unhealthy': return <XCircle className="text-red-500" size={16} />;
      case 'loading': return <AlertCircle className="text-yellow-500" size={16} />;
      default: return <AlertCircle className="text-gray-500" size={16} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-700';
      case 'unhealthy': return 'bg-red-100 text-red-700';
      case 'loading': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <Card className="mt-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">🔧 Service Debug Panel</CardTitle>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={checkAllServices}
            disabled={isMonitoring}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${isMonitoring ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
        <p className="text-sm text-gray-600">
          Monitoring: {isMonitoring ? 'Active' : 'Idle'} | Health: {healthyCount}/{totalCount}
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {services.map((service) => (
            <div 
              key={service.name}
              className="p-3 border rounded-lg bg-gray-50"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(service.status)}
                  <span className="font-medium text-sm">{service.name}</span>
                </div>
                <Badge className={getStatusColor(service.status)}>
                  {service.status}
                </Badge>
              </div>
              
              <div className="space-y-1 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>Port:</span>
                  <span className="font-mono">{service.port}</span>
                </div>
                <div className="flex justify-between">
                  <span>Response:</span>
                  <span className="font-mono">{service.responseTime}ms</span>
                </div>
                <div className="flex justify-between">
                  <span>URL:</span>
                  <span className="font-mono text-xs">localhost:{service.port}</span>
                </div>
                <div className="flex justify-between">
                  <span>Connection:</span>
                  <span className="font-mono">{connectionStatus[service.name] || 'unknown'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <h4 className="font-medium text-blue-900 mb-2">Debug Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-blue-700 font-medium">Total Services:</span>
              <p className="text-blue-900">{totalCount}</p>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Healthy Services:</span>
              <p className="text-blue-900">{healthyCount}</p>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Overall Status:</span>
              <p className="text-blue-900">{isAllHealthy ? 'All Healthy' : 'Some Issues'}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ServiceDebugPanel;
