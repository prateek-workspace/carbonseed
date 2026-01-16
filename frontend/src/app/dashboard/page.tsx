'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface LatestData {
  temperature: number | null;
  gas_index: number | null;
  vibration_health: string;
  device_uptime: number | null;
  last_update: string | null;
}

interface Alert {
  id: number;
  title: string;
  message: string;
  severity: string;
  status: string;
  triggered_at: string;
}

interface Device {
  id: number;
  device_id: string;
  device_name: string;
  is_active: boolean;
  last_seen: string | null;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [latestData, setLatestData] = useState<LatestData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchDashboardData(token);
  }, []);

  const fetchDashboardData = async (token: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const userRes = await fetch(`${apiUrl}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (!userRes.ok) throw new Error('Unauthorized');
      const userData = await userRes.json();
      setUser(userData);

      const latestRes = await fetch(`${apiUrl}/data/latest`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const latest = await latestRes.json();
      setLatestData(latest);

      const alertsRes = await fetch(`${apiUrl}/alerts?status=active`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const alertsData = await alertsRes.json();
      setAlerts(alertsData.slice(0, 5));

      const devicesRes = await fetch(`${apiUrl}/devices`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const devicesData = await devicesRes.json();
      setDevices(devicesData);

      if (devicesData.length > 0) {
        const deviceId = devicesData[0].id;
        const tsRes = await fetch(`${apiUrl}/data/timeseries?device_id=${deviceId}&limit=100`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const tsData = await tsRes.json();
        
        const formattedData = tsData.map((d: any) => ({
          time: new Date(d.timestamp).toLocaleTimeString(),
          temperature: d.temperature,
          gas_index: d.gas_index,
        })).reverse();
        
        setTimeSeriesData(formattedData.slice(-20));
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      localStorage.removeItem('token');
      router.push('/login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const downloadReport = async (reportType: string) => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    try {
      const res = await fetch(`${apiUrl}/reports/${reportType}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const report = await res.json();
      
      const dataStr = JSON.stringify(report, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
      const exportFileDefaultName = `carbonseed-${reportType}-report.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-ink border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="bg-surface-elevated border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-8">
              <Link href="/" className="text-lg font-semibold text-ink">
                carbonseed
              </Link>
              <span className="text-sm text-ink-faint font-mono">Dashboard</span>
            </div>
            <div className="flex items-center gap-6">
              {(user?.role === 'admin' || user?.role === 'factory_owner') && (
                <button
                  onClick={() => router.push('/simulator')}
                  className="px-4 py-2 text-sm text-ink-muted border border-border rounded-md hover:bg-surface-muted transition-colors"
                >
                  Data Simulator
                </button>
              )}
              <div className="text-right">
                <p className="text-sm font-medium text-ink">{user?.full_name}</p>
                <p className="text-xs text-ink-faint capitalize">{user?.role.replace('_', ' ')}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-ink-muted hover:text-ink hover:bg-surface-muted rounded-md transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Overview Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <MetricCard
            label="Temperature"
            value={latestData?.temperature ? `${latestData.temperature.toFixed(1)}°C` : 'N/A'}
            status={latestData?.temperature && latestData.temperature > 900 ? 'critical' : 'normal'}
          />
          <MetricCard
            label="Gas Index"
            value={latestData?.gas_index ? latestData.gas_index.toFixed(0) : 'N/A'}
            status={latestData?.gas_index && latestData.gas_index > 400 ? 'warning' : 'normal'}
          />
          <MetricCard
            label="Vibration Health"
            value={latestData?.vibration_health || 'Unknown'}
            status={latestData?.vibration_health === 'critical' ? 'critical' : 
                   latestData?.vibration_health === 'moderate' ? 'warning' : 'normal'}
          />
          <MetricCard
            label="Device Uptime"
            value={latestData?.device_uptime ? `${latestData.device_uptime.toFixed(1)}%` : 'N/A'}
            status={latestData?.device_uptime && latestData.device_uptime < 80 ? 'warning' : 'normal'}
          />
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Time Series Chart */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-2 bg-surface-elevated rounded-xl border border-border p-6"
          >
            <h2 className="text-sm font-medium text-ink mb-4">Temperature Trend</h2>
            {timeSeriesData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={timeSeriesData}>
                  <defs>
                    <linearGradient id="temperatureGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#64748b" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#64748b" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                  <XAxis dataKey="time" stroke="#a3a3a3" style={{ fontSize: '11px' }} />
                  <YAxis stroke="#a3a3a3" style={{ fontSize: '11px' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #e5e5e5',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Area type="monotone" dataKey="temperature" stroke="#64748b" strokeWidth={2} fill="url(#temperatureGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-ink-faint">
                No data available
              </div>
            )}
          </motion.div>

          {/* Alerts Panel */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-surface-elevated rounded-xl border border-border p-6"
          >
            <h2 className="text-sm font-medium text-ink mb-4">Active Alerts</h2>
            <div className="space-y-3">
              {alerts.length > 0 ? (
                alerts.map((alert) => (
                  <AlertItem key={alert.id} alert={alert} />
                ))
              ) : (
                <p className="text-sm text-ink-faint">No active alerts</p>
              )}
            </div>
          </motion.div>
        </div>

        {/* Device Status and Reports */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Device Status */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-surface-elevated rounded-xl border border-border p-6"
          >
            <h2 className="text-sm font-medium text-ink mb-4">Devices</h2>
            <div className="space-y-3">
              {devices.map((device) => (
                <DeviceItem key={device.id} device={device} />
              ))}
            </div>
          </motion.div>

          {/* Compliance Reports */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-surface-elevated rounded-xl border border-border p-6"
          >
            <h2 className="text-sm font-medium text-ink mb-4">Compliance Reports</h2>
            <div className="space-y-3">
              <ReportButton title="Weekly Report" onClick={() => downloadReport('weekly')} />
              <ReportButton title="Monthly Report" onClick={() => downloadReport('monthly')} />
              <ReportButton title="Compliance Report (SPCB/PAT/CBAM)" onClick={() => downloadReport('compliance')} />
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ label, value, status }: { 
  label: string;
  value: string;
  status: 'normal' | 'warning' | 'critical';
}) {
  const statusColors = {
    normal: 'text-accent-green',
    warning: 'text-accent-amber',
    critical: 'text-red-600',
  };

  const statusDot = {
    normal: 'bg-accent-green',
    warning: 'bg-accent-amber',
    critical: 'bg-red-600',
  };

  return (
    <div className="bg-surface-elevated rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-ink-muted">{label}</span>
        <span className={`w-2 h-2 rounded-full ${statusDot[status]}`} />
      </div>
      <p className={`text-2xl font-semibold ${status === 'normal' ? 'text-ink' : statusColors[status]}`}>
        {value}
      </p>
    </div>
  );
}

function AlertItem({ alert }: { alert: Alert }) {
  const severityStyles = {
    info: 'border-l-accent-blue bg-blue-50/50',
    warning: 'border-l-accent-amber bg-amber-50/50',
    critical: 'border-l-red-500 bg-red-50/50',
  };

  return (
    <div className={`p-3 rounded-r-lg border-l-2 ${severityStyles[alert.severity as keyof typeof severityStyles] || severityStyles.info}`}>
      <h4 className="text-sm font-medium text-ink">{alert.title}</h4>
      <p className="text-xs text-ink-muted mt-1">{alert.message}</p>
      <p className="text-xs text-ink-faint mt-1 font-mono">
        {new Date(alert.triggered_at).toLocaleString()}
      </p>
    </div>
  );
}

function DeviceItem({ device }: { device: Device }) {
  const isOnline = device.last_seen && 
    (new Date().getTime() - new Date(device.last_seen).getTime()) < 300000;

  return (
    <div className="flex items-center justify-between p-3 border border-border rounded-lg">
      <div>
        <h4 className="text-sm font-medium text-ink">{device.device_name}</h4>
        <p className="text-xs text-ink-faint font-mono">{device.device_id}</p>
      </div>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-accent-green' : 'bg-ink-faint'}`} />
        <span className={`text-xs ${isOnline ? 'text-accent-green' : 'text-ink-faint'}`}>
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>
    </div>
  );
}

function ReportButton({ title, onClick }: { title: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between p-4 border border-border rounded-lg hover:bg-surface-muted transition-colors"
    >
      <span className="text-sm font-medium text-ink">{title}</span>
      <svg className="w-4 h-4 text-ink-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
    </button>
  );
}
