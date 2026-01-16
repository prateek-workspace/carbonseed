'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid email or password');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-surface flex">
      {/* Left side - Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-sm"
        >
          {/* Logo */}
          <Link href="/" className="inline-block mb-12">
            <span className="text-xl font-semibold text-ink">carbonseed</span>
          </Link>

          {/* Header */}
          <h1 className="heading-md text-ink mb-2">
            Sign in to your account
          </h1>
          <p className="body-base mb-8">
            Access your operations dashboard.
          </p>

          {/* Error message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm"
            >
              {error}
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-ink mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-surface-elevated border border-border rounded-lg text-ink placeholder-ink-faint focus:outline-none focus:ring-2 focus:ring-ink/10 focus:border-ink/30 transition-all"
                placeholder="you@company.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-ink mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-surface-elevated border border-border rounded-lg text-ink placeholder-ink-faint focus:outline-none focus:ring-2 focus:ring-ink/10 focus:border-ink/30 transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-ink text-surface-elevated font-medium rounded-lg hover:bg-ink/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-10 p-4 bg-surface-muted rounded-lg border border-border">
            <p className="text-xs font-medium text-ink-muted mb-3">Demo credentials</p>
            <div className="space-y-2 text-xs text-ink-faint font-mono">
              <p><span className="text-accent-blue">Admin:</span> admin@carbonseed.io / admin123</p>
              <p><span className="text-accent-green">Owner:</span> owner@steelforge.in / password123</p>
            </div>
          </div>

          {/* Back link */}
          <div className="mt-8">
            <Link href="/" className="text-sm text-ink-muted hover:text-ink transition-colors">
              ← Back to homepage
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Right side - Visual */}
      <div className="hidden lg:flex flex-1 bg-surface-muted items-center justify-center border-l border-border">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="max-w-md text-center px-12"
        >
          <div className="text-6xl mb-8">🏭</div>
          <h2 className="heading-md text-ink mb-4">
            Industrial intelligence at your fingertips.
          </h2>
          <p className="body-base">
            Monitor operations, predict maintenance, and stay compliant — all from one dashboard.
          </p>
        </motion.div>
      </div>
    </main>
  );
}
