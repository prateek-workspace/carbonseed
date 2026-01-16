'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface Device {
  id: number;
  device_id: string;
  device_name: string;
}

interface Reading {
  device_id: string;
  temperature: number;
  gas_index: number;
  vibration_x: number;
  vibration_y: number;
  vibration_z: number;
  humidity: number;
  pressure: number;
  power_consumption: number;
}

export default function SimulatorPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [jsonInput, setJsonInput] = useState('');
  const [readings, setReadings] = useState<Reading[]>([
    {
      device_id: 'ESP32-SF-001',
      temperature: 850.5,
      gas_index: 320.0,
      vibration_x: 2.1,
      vibration_y: 1.8,
      vibration_z: 2.3,
      humidity: 45.0,
      pressure: 1013.2,
      power_consumption: 32.5
    }
  ]);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchData(token);
  }, []);

  const fetchData = async (token: string) => {
    try {
      const userRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!userRes.ok) throw new Error('Unauthorized');
      const userData = await userRes.json();
      setUser(userData);

      const devicesRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/devices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const devicesData = await devicesRes.json();
      setDevices(devicesData);
    } catch (error) {
      console.error('Error fetching data:', error);
      localStorage.removeItem('token');
      router.push('/login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const addReading = () => {
    setReadings([...readings, {
      device_id: devices[0]?.device_id || '',
      temperature: 0,
      gas_index: 0,
      vibration_x: 0,
      vibration_y: 0,
      vibration_z: 0,
      humidity: 0,
      pressure: 0,
      power_consumption: 0
    }]);
  };

  const removeReading = (index: number) => {
    setReadings(readings.filter((_, i) => i !== index));
  };

  const updateReading = (index: number, field: keyof Reading, value: string) => {
    const updated = [...readings];
    if (field === 'device_id') {
      updated[index][field] = value;
    } else {
      updated[index][field] = parseFloat(value) || 0;
    }
    setReadings(updated);
  };

  const handleJsonUpload = () => {
    try {
      const parsed = JSON.parse(jsonInput);
      if (Array.isArray(parsed)) {
        setReadings(parsed);
      } else if (parsed.readings) {
        setReadings(parsed.readings);
      } else {
        setReadings([parsed]);
      }
      setMessage({ type: 'success', text: 'JSON loaded successfully' });
      setJsonInput('');
    } catch (error) {
      setMessage({ type: 'error', text: 'Invalid JSON format' });
    }
  };

  const handleSubmit = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/simulator/ingest-batch`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ readings })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `Successfully ingested ${data.ingested_count} of ${data.total_readings} readings` 
        });
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to ingest data' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error' });
    } finally {
      setLoading(false);
    }
  };

  const generateSample = async (deviceId: string) => {
    const token = localStorage.getItem('token');
    if (!token) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/simulator/generate-sample?device_id=${deviceId}&count=20`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      const data = await response.json();
      if (response.ok) {
        setMessage({ type: 'success', text: data.message });
      } else {
        setMessage({ type: 'error', text: data.detail });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to generate sample data' });
    } finally {
      setLoading(false);
    }
  };

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
              <span className="text-sm text-ink-faint font-mono">Data Simulator</span>
            </div>
            <div className="flex items-center gap-6">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-sm text-ink-muted hover:text-ink transition-colors"
              >
                ← Dashboard
              </button>
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
        {/* Message */}
        {message && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mb-6 p-4 rounded-lg border ${
              message.type === 'success' 
                ? 'bg-green-50 border-green-200 text-accent-green' 
                : 'bg-red-50 border-red-200 text-red-600'
            } text-sm`}
          >
            {message.text}
          </motion.div>
        )}

        {/* Quick Actions */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 bg-surface-elevated rounded-xl border border-border p-6"
        >
          <h2 className="text-sm font-medium text-ink mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {devices.slice(0, 3).map((device, index) => (
              <motion.button
                key={device.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => generateSample(device.device_id)}
                disabled={loading}
                className="p-4 border border-border rounded-lg hover:bg-surface-muted text-left disabled:opacity-50 transition-colors"
              >
                <p className="text-sm font-medium text-ink mb-1">{device.device_name}</p>
                <p className="text-xs text-ink-faint">Generate 20 sample readings</p>
              </motion.button>
            ))}
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* JSON Upload */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-surface-elevated rounded-xl border border-border p-6"
          >
            <h2 className="text-sm font-medium text-ink mb-4">Upload JSON</h2>
            <p className="text-sm text-ink-muted mb-4">
              Paste JSON array of readings or single reading object
            </p>
            <textarea
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              placeholder='[{"device_id": "ESP32-SF-001", "temperature": 850.5, ...}]'
              className="w-full h-64 px-4 py-3 bg-surface border border-border rounded-lg text-sm font-mono text-ink placeholder-ink-faint focus:outline-none focus:ring-2 focus:ring-ink/10 focus:border-ink/30 transition-all"
            />
            <button
              onClick={handleJsonUpload}
              className="mt-4 w-full py-3 bg-ink text-surface-elevated font-medium rounded-lg hover:bg-ink/90 transition-colors"
            >
              Load JSON
            </button>
          </motion.div>

          {/* Manual Entry */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-surface-elevated rounded-xl border border-border p-6"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-medium text-ink">Manual Entry</h2>
              <button
                onClick={addReading}
                className="px-3 py-1.5 text-sm text-ink border border-border rounded-md hover:bg-surface-muted transition-colors"
              >
                + Add
              </button>
            </div>
            
            <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
              {readings.map((reading, idx) => (
                <motion.div 
                  key={idx} 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-4 bg-surface rounded-lg border border-border"
                >
                  <div className="flex justify-between items-start mb-3">
                    <select
                      value={reading.device_id}
                      onChange={(e) => updateReading(idx, 'device_id', e.target.value)}
                      className="text-sm bg-surface-elevated border border-border rounded-md px-3 py-2 text-ink focus:outline-none focus:ring-2 focus:ring-ink/10"
                    >
                      {devices.map(d => (
                        <option key={d.device_id} value={d.device_id}>{d.device_name}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => removeReading(idx)}
                      className="text-ink-faint hover:text-red-500 transition-colors p-1"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(reading).map(([key, value]) => {
                      if (key === 'device_id') return null;
                      return (
                        <input
                          key={key}
                          type="number"
                          step="0.1"
                          value={value}
                          onChange={(e) => updateReading(idx, key as keyof Reading, e.target.value)}
                          placeholder={key.replace('_', ' ')}
                          className="px-3 py-2 bg-surface-elevated border border-border rounded-md text-ink font-mono focus:outline-none focus:ring-2 focus:ring-ink/10 transition-all"
                        />
                      );
                    })}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Submit Button */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6"
        >
          <button
            onClick={handleSubmit}
            disabled={loading || readings.length === 0}
            className="w-full py-4 bg-accent-green text-white font-medium rounded-lg hover:bg-accent-green/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Ingesting...' : `Ingest ${readings.length} Reading${readings.length !== 1 ? 's' : ''}`}
          </button>
        </motion.div>

        {/* Current Data Preview */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-6 bg-surface-elevated rounded-xl border border-border p-6"
        >
          <h2 className="text-sm font-medium text-ink mb-4">Data Preview</h2>
          <pre className="bg-surface p-4 rounded-lg text-xs font-mono text-ink-muted overflow-x-auto border border-border">
            {JSON.stringify({ readings }, null, 2)}
          </pre>
        </motion.div>
      </main>
    </div>
  );
}
