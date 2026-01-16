'use client';

import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { InteractiveBoardSection } from './components/InteractiveBoard';
import { FeaturesSection } from './components/FeaturesSection';
import { TechnologySection } from './components/TechnologySection';
import { PricingSection } from './components/PricingSection';
import { Footer } from './components/Footer';

// Animated background mesh component
const AnimatedMesh = () => (
  <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
    {/* Grid pattern */}
    <div className="absolute inset-0 grid-pattern opacity-40" />
    
    {/* Floating gradient orbs */}
    <motion.div
      animate={{
        x: [0, 100, 0],
        y: [0, -50, 0],
      }}
      transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
      className="absolute top-[10%] left-[10%] w-[600px] h-[600px] rounded-full bg-gradient-radial from-accent-blue/5 to-transparent blur-3xl"
    />
    <motion.div
      animate={{
        x: [0, -80, 0],
        y: [0, 80, 0],
      }}
      transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
      className="absolute top-[50%] right-[5%] w-[500px] h-[500px] rounded-full bg-gradient-radial from-accent-green/4 to-transparent blur-3xl"
    />
    <motion.div
      animate={{
        x: [0, 60, 0],
        y: [0, -40, 0],
      }}
      transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
      className="absolute bottom-[10%] left-[30%] w-[400px] h-[400px] rounded-full bg-gradient-radial from-accent-amber/3 to-transparent blur-3xl"
    />
    
    {/* Animated rectangles mesh */}
    <svg className="absolute inset-0 w-full h-full opacity-[0.015]" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="rect-mesh" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
          <rect x="0" y="0" width="60" height="60" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-ink" />
          <rect x="60" y="60" width="60" height="60" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-ink" />
        </pattern>
      </defs>
      <motion.rect 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 2 }}
        width="100%" 
        height="100%" 
        fill="url(#rect-mesh)" 
      />
    </svg>
  </div>
);

// Header Component - Minimal, fixed with z-index
const Header = () => (
  <motion.header 
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
    className="fixed top-0 left-0 right-0 z-[100] bg-surface/60 backdrop-blur-xl border-b border-border/50"
  >
    <div className="container-wide py-4 flex justify-between items-center">
      <Link href="/" className="text-lg font-semibold text-ink hover:text-ink-muted transition-colors">
        carbonseed
      </Link>
      <nav className="hidden md:flex items-center space-x-8">
        <Link href="#features" className="text-sm text-ink-muted hover:text-ink transition-colors">Features</Link>
        <Link href="#industries" className="text-sm text-ink-muted hover:text-ink transition-colors">Industries</Link>
        <Link href="#pricing" className="text-sm text-ink-muted hover:text-ink transition-colors">Pricing</Link>
      </nav>
      <Link 
        href="/login"
        className="px-4 py-2 text-sm text-ink border border-border rounded-md hover:bg-surface-muted transition-colors"
      >
        Dashboard
      </Link>
    </div>
  </motion.header>
);

// Initial landing view - art gallery entrance
const IntroSection = () => {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"]
  });
  
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95]);
  const y = useTransform(scrollYProgress, [0, 0.5], [0, -50]);

  return (
    <section ref={ref} className="min-h-screen flex items-center justify-center pt-16 relative z-10">
      <motion.div 
        style={{ opacity, scale, y }}
        className="container-wide text-center"
      >
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="label-sm text-accent-blue mb-6 block">Industrial IoT Platform</span>
          <h1 className="heading-xl text-ink mb-6 max-w-4xl mx-auto">
            Transform your factory floor with edge intelligence.
          </h1>
          <p className="body-lg max-w-2xl mx-auto mb-10">
            Carbonseed brings real-time monitoring, predictive maintenance, and automated compliance to Indian MSMEs — at a fraction of traditional costs.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link 
              href="/login"
              className="px-6 py-3 bg-ink text-surface-elevated rounded-lg hover:bg-ink/90 transition-colors"
            >
              Request a Pilot
            </Link>
            <Link 
              href="#features"
              className="px-6 py-3 text-ink border border-border rounded-lg hover:bg-surface-muted transition-colors"
            >
              Learn More
            </Link>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
};

export default function HomePage() {
  return (
    <main className="bg-surface text-ink relative noise-texture">
      <AnimatedMesh />
      <Header />
      <IntroSection />
      <InteractiveBoardSection />
      <FeaturesSection />
      <TechnologySection />
      <PricingSection />
      <Footer />
    </main>
  );
}
