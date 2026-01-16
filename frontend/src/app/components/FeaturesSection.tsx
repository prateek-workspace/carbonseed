'use client';

import { useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';

// Stats that appear as a gallery piece
const stats = [
  { value: '99.9%', label: 'Uptime SLA', description: 'Edge devices built for harsh factory environments' },
  { value: '<500ms', label: 'Latency', description: 'From sensor reading to cloud dashboard' },
  { value: '40%', label: 'Cost Reduction', description: 'Average savings in unplanned downtime' },
];

// How it works steps
const steps = [
  {
    number: '01',
    title: 'Deploy Sensors',
    description: 'Install our pre-configured ESP32 edge devices on your existing machinery. No complex wiring needed.',
    visual: '📡'
  },
  {
    number: '02', 
    title: 'Connect & Stream',
    description: 'Devices auto-connect via WiFi/4G and start streaming data within minutes of installation.',
    visual: '🔗'
  },
  {
    number: '03',
    title: 'Analyze & Act',
    description: 'AI models detect anomalies, predict failures, and generate actionable recommendations.',
    visual: '🧠'
  },
  {
    number: '04',
    title: 'Report & Comply',
    description: 'Automated compliance reports generated for SPCB, PAT, and CBAM requirements.',
    visual: '📋'
  }
];

export const FeaturesSection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef(null);
  const isStatsInView = useInView(statsRef, { once: true, margin: "-100px" });
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });
  
  // Parallax for the section title
  const titleY = useTransform(scrollYProgress, [0, 0.5], [50, 0]);
  const titleOpacity = useTransform(scrollYProgress, [0, 0.2], [0, 1]);

  return (
    <section ref={containerRef} className="relative z-20 bg-surface">
      {/* Stats as art pieces */}
      <div className="section-spacing border-b border-border">
        <div className="container-wide">
          <motion.div
            style={{ y: titleY, opacity: titleOpacity }}
            className="text-center mb-20"
          >
            <span className="label-sm text-accent-blue mb-4 block">Performance</span>
            <h2 className="heading-lg text-ink max-w-2xl mx-auto">
              Numbers that matter.
            </h2>
          </motion.div>
          
          <div 
            ref={statsRef}
            className="grid md:grid-cols-3 gap-8 lg:gap-12"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 40, rotateX: -10 }}
                animate={isStatsInView ? { opacity: 1, y: 0, rotateX: 0 } : {}}
                transition={{ 
                  duration: 0.8, 
                  delay: index * 0.2,
                  ease: [0.16, 1, 0.3, 1]
                }}
                className="group relative"
              >
                {/* Card with depth effect */}
                <div className="relative p-8 bg-surface-elevated rounded-2xl border border-border overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-ink/5 hover:-translate-y-1">
                  {/* Subtle gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-accent-blue/5 via-transparent to-accent-green/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="relative z-10">
                    <div className="text-5xl md:text-6xl font-semibold text-ink mb-2 tracking-tight">
                      {stat.value}
                    </div>
                    <div className="text-sm font-mono text-accent-blue mb-3 uppercase tracking-wider">
                      {stat.label}
                    </div>
                    <p className="text-ink-muted text-sm">
                      {stat.description}
                    </p>
                  </div>
                  
                  {/* Corner accent */}
                  <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-transparent to-accent-blue/5 rounded-bl-[60px]" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* How it Works - Gallery Style */}
      <div className="section-spacing">
        <div className="container-wide">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="text-center mb-20"
          >
            <span className="label-sm text-accent-green mb-4 block">Process</span>
            <h2 className="heading-lg text-ink max-w-2xl mx-auto">
              From deployment to insight in four steps.
            </h2>
          </motion.div>
          
          {/* Steps as horizontal gallery */}
          <div className="relative">
            {/* Connection line */}
            <div className="hidden lg:block absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {steps.map((step, index) => (
                <motion.div
                  key={step.number}
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ 
                    duration: 0.6, 
                    delay: index * 0.15,
                    ease: [0.16, 1, 0.3, 1]
                  }}
                  className="relative group"
                >
                  {/* Number badge */}
                  <div className="relative z-10 w-12 h-12 mx-auto mb-6 flex items-center justify-center bg-surface-elevated border border-border rounded-full group-hover:border-accent-green/50 group-hover:shadow-lg transition-all duration-300">
                    <span className="text-sm font-mono text-ink-muted group-hover:text-accent-green transition-colors">
                      {step.number}
                    </span>
                  </div>
                  
                  {/* Visual icon */}
                  <div className="text-4xl text-center mb-4">{step.visual}</div>
                  
                  {/* Content */}
                  <h3 className="text-lg font-semibold text-ink text-center mb-2 group-hover:text-accent-green transition-colors">
                    {step.title}
                  </h3>
                  <p className="text-sm text-ink-muted text-center leading-relaxed">
                    {step.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};