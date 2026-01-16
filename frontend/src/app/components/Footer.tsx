'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export const Footer = () => {
  return (
    <footer className="relative py-20 bg-surface-muted overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 pointer-events-none opacity-30">
        <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="footer-dots" x="0" y="0" width="32" height="32" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" fill="#a3a3a3" opacity="0.3" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#footer-dots)" />
        </svg>
      </div>
      
      <div className="container-wide relative z-10">
        <div className="grid md:grid-cols-4 gap-12 mb-16">
          {/* Brand */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="md:col-span-2"
          >
            <Link href="/" className="inline-block mb-6">
              <span className="text-2xl font-semibold text-ink">carbonseed</span>
            </Link>
            <p className="text-ink-muted leading-relaxed max-w-md mb-6">
              Industrial intelligence for Indian MSMEs. Low-cost edge sensing, cloud analytics, and compliance automation.
            </p>
            <div className="flex items-center gap-2 text-sm text-ink-faint">
              <span className="w-2 h-2 bg-accent-green rounded-full animate-pulse" />
              <span className="font-mono">Systems operational</span>
            </div>
          </motion.div>

          {/* Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          >
            <h4 className="text-sm font-medium text-ink mb-5 uppercase tracking-wider">Product</h4>
            <ul className="space-y-4">
              <li>
                <Link href="#features" className="text-ink-muted hover:text-ink transition-colors inline-flex items-center group">
                  <span className="w-0 group-hover:w-4 h-px bg-accent-green mr-0 group-hover:mr-2 transition-all duration-300" />
                  Features
                </Link>
              </li>
              <li>
                <Link href="#industries" className="text-ink-muted hover:text-ink transition-colors inline-flex items-center group">
                  <span className="w-0 group-hover:w-4 h-px bg-accent-green mr-0 group-hover:mr-2 transition-all duration-300" />
                  Industries
                </Link>
              </li>
              <li>
                <Link href="#pricing" className="text-ink-muted hover:text-ink transition-colors inline-flex items-center group">
                  <span className="w-0 group-hover:w-4 h-px bg-accent-green mr-0 group-hover:mr-2 transition-all duration-300" />
                  Pricing
                </Link>
              </li>
            </ul>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <h4 className="text-sm font-medium text-ink mb-5 uppercase tracking-wider">Connect</h4>
            <ul className="space-y-4">
              <li>
                <Link href="/login" className="text-ink-muted hover:text-ink transition-colors inline-flex items-center group">
                  <span className="w-0 group-hover:w-4 h-px bg-accent-blue mr-0 group-hover:mr-2 transition-all duration-300" />
                  Dashboard
                </Link>
              </li>
              <li>
                <a href="mailto:contact@carbonseed.io" className="text-ink-muted hover:text-ink transition-colors inline-flex items-center group">
                  <span className="w-0 group-hover:w-4 h-px bg-accent-blue mr-0 group-hover:mr-2 transition-all duration-300" />
                  contact@carbonseed.io
                </a>
              </li>
            </ul>
          </motion.div>
        </div>

        {/* Bottom */}
        <motion.div 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4"
        >
          <p className="text-sm text-ink-faint">
            © {new Date().getFullYear()} Carbonseed Technologies Pvt. Ltd.
          </p>
          <div className="flex items-center gap-6">
            <span className="text-sm text-ink-faint font-mono">v1.0.0</span>
            <span className="text-sm text-ink-faint">Made with 🌱 in India</span>
          </div>
        </motion.div>
      </div>
    </footer>
  );
};