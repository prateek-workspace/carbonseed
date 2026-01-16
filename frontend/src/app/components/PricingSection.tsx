'use client';

import { useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import Link from 'next/link';

const problems = [
  {
    stat: '60%',
    label: 'of Indian MSMEs',
    problem: 'lack visibility into real-time operations'
  },
  {
    stat: '₹2.5L',
    label: 'average annual loss',
    problem: 'from unplanned downtime per unit'
  },
  {
    stat: '85%',
    label: 'compliance burden',
    problem: 'spent on manual data collection'
  },
];

export const PricingSection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });
  
  // Parallax effects for depth
  const bgY = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const ctaScale = useTransform(scrollYProgress, [0.5, 0.8], [0.95, 1]);
  const ctaOpacity = useTransform(scrollYProgress, [0.5, 0.7], [0.5, 1]);

  return (
    <section ref={containerRef} id="pricing" className="relative z-20">
      {/* Problems Section with layered depth */}
      <div className="section-spacing bg-surface relative overflow-hidden">
        {/* Background decorative elements */}
        <motion.div 
          style={{ y: bgY }}
          className="absolute inset-0 pointer-events-none"
        >
          <div className="absolute top-20 left-10 w-96 h-96 bg-accent-amber/5 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-80 h-80 bg-accent-blue/5 rounded-full blur-3xl" />
        </motion.div>
        
        <div className="container-wide relative z-10">
          <motion.div
            ref={sectionRef}
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="mb-20"
          >
            <span className="label-sm text-ink-faint mb-4 block">The Problem</span>
            <h2 className="heading-lg text-ink max-w-3xl">
              Indian MSMEs operate in the dark. We change that.
            </h2>
          </motion.div>
          
          {/* Problems as gallery cards with perspective */}
          <div className="grid md:grid-cols-3 gap-8 perspective-container">
            {problems.map((item, index) => (
              <motion.div
                key={item.stat}
                initial={{ opacity: 0, y: 40, rotateY: -5 }}
                animate={isInView ? { opacity: 1, y: 0, rotateY: 0 } : {}}
                transition={{ 
                  duration: 0.7, 
                  delay: index * 0.15, 
                  ease: [0.16, 1, 0.3, 1] 
                }}
                className="group"
              >
                <div className="relative p-8 bg-surface-elevated rounded-2xl border border-border h-full overflow-hidden transition-all duration-500 hover:shadow-xl hover:border-accent-amber/30 hover:-translate-y-2">
                  {/* Hover gradient */}
                  <div className="absolute inset-0 bg-gradient-to-br from-accent-amber/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="relative z-10">
                    <div className="text-5xl md:text-6xl font-bold text-ink mb-3 tracking-tight">
                      {item.stat}
                    </div>
                    <div className="text-sm font-mono text-accent-amber mb-4 uppercase tracking-wider">
                      {item.label}
                    </div>
                    <p className="text-ink-muted leading-relaxed">{item.problem}</p>
                  </div>
                  
                  {/* Decorative line */}
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-accent-amber/0 via-accent-amber/40 to-accent-amber/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section - Floating card effect */}
      <div className="relative -mt-20 z-30 pb-24">
        <div className="container-wide">
          <motion.div
            style={{ scale: ctaScale, opacity: ctaOpacity }}
            className="relative"
          >
            {/* Glowing border effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-accent-green/20 via-accent-blue/20 to-accent-amber/20 rounded-3xl blur-xl opacity-50" />
            
            <div className="relative bg-ink text-surface-elevated rounded-2xl p-12 md:p-16 overflow-hidden">
              {/* Background pattern */}
              <div className="absolute inset-0 opacity-5">
                <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <pattern id="cta-grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                      <circle cx="20" cy="20" r="1" fill="currentColor" />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#cta-grid)" />
                </svg>
              </div>
              
              <div className="relative z-10 text-center">
                <motion.h2 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                  className="heading-lg text-surface-elevated mb-4"
                >
                  Ready to see it in action?
                </motion.h2>
                <motion.p 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="body-lg text-surface-elevated/70 mb-10 max-w-xl mx-auto"
                >
                  We offer a free pilot program for qualifying MSMEs. No upfront costs, no commitments.
                </motion.p>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                >
                  <Link
                    href="/login"
                    className="inline-flex items-center px-8 py-4 bg-surface-elevated text-ink font-medium rounded-xl hover:bg-surface hover:shadow-lg hover:shadow-white/10 transition-all duration-300 group"
                  >
                    Request a Pilot
                    <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </Link>
                </motion.div>
                <motion.p 
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="mt-6 text-sm text-surface-elevated/40 font-mono"
                >
                  Typically respond within 24 hours
                </motion.p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};