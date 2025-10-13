/**
 * Connection Service
 * Handles backend connectivity with automatic retry and health monitoring
 */

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const HEALTH_ENDPOINT = `${BACKEND_URL}/api/v1/monitoring/health`;
const MAX_RETRIES = 10;
const RETRY_DELAY = 3000; // 3 seconds

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  backend_available: boolean;
  message?: string;
}

class ConnectionService {
  private isConnected: boolean = false;
  private retryCount: number = 0;
  private listeners: Array<(status: HealthStatus) => void> = [];

  /**
   * Wait for backend to be ready with automatic retry
   */
  async waitForBackend(): Promise<boolean> {
    console.log('🔄 Waiting for backend to be ready...');
    
    while (this.retryCount < MAX_RETRIES) {
      try {
        const response = await fetch(HEALTH_ENDPOINT, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(5000), // 5s timeout
        });

        if (response.ok) {
          const data = await response.json();
          
          if (data.status === 'healthy') {
            console.log('✅ Backend is ready!');
            this.isConnected = true;
            this.notifyListeners({
              status: 'healthy',
              backend_available: true,
              message: 'Backend connected successfully'
            });
            return true;
          }
        }
      } catch (error) {
        console.log(`⏳ Backend not ready yet (attempt ${this.retryCount + 1}/${MAX_RETRIES})...`);
      }

      this.retryCount++;
      
      if (this.retryCount < MAX_RETRIES) {
        await this.sleep(RETRY_DELAY);
      }
    }

    console.error('❌ Backend failed to start after maximum retries');
    this.notifyListeners({
      status: 'unhealthy',
      backend_available: false,
      message: 'Backend unavailable after maximum retries'
    });
    return false;
  }

  /**
   * Check backend health status
   */
  async checkHealth(): Promise<HealthStatus> {
    try {
      const response = await fetch(HEALTH_ENDPOINT, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });

      if (response.ok) {
        const data = await response.json();
        this.isConnected = true;
        return {
          status: data.status || 'healthy',
          backend_available: true,
        };
      }
    } catch (error) {
      this.isConnected = false;
    }

    return {
      status: 'unhealthy',
      backend_available: false,
      message: 'Backend not responding'
    };
  }

  /**
   * Subscribe to connection status changes
   */
  onStatusChange(callback: (status: HealthStatus) => void) {
    this.listeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  /**
   * Notify all listeners of status change
   */
  private notifyListeners(status: HealthStatus) {
    this.listeners.forEach(callback => callback(status));
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Reset retry counter
   */
  resetRetries() {
    this.retryCount = 0;
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Start periodic health monitoring
   */
  startHealthMonitoring(intervalMs: number = 30000) {
    setInterval(async () => {
      const health = await this.checkHealth();
      this.notifyListeners(health);
    }, intervalMs);
  }
}

// Export singleton instance
export const connectionService = new ConnectionService();

// Auto-start health monitoring
connectionService.startHealthMonitoring();

