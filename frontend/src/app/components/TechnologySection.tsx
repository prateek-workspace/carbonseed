'use client';

import { useRef, useState } from 'react';
import { motion, useScroll, useTransform, useMotionValueEvent, useInView } from 'framer-motion';

const industries = [
  { name: 'Steel & Foundries', description: 'Furnace monitoring, energy optimization', icon: '🏭' },
  { name: 'Textiles', description: 'Loom efficiency, humidity control', icon: '🧵' },
  { name: 'Food Processing', description: 'Cold chain, quality assurance', icon: '🍱' },
  { name: 'Plastics & Packaging', description: 'Extrusion monitoring, waste reduction', icon: '📦' },
  { name: 'Auto Components', description: 'CNC health, vibration analysis', icon: '⚙️' },
  { name: 'Pharmaceuticals', description: 'GMP compliance, batch tracking', icon: '💊' },
];

const complianceItems = [
  { code: 'SPCB', name: 'State Pollution Control Board', description: 'Continuous emission monitoring' },
  { code: 'PAT', name: 'Perform Achieve Trade', description: 'Energy efficiency certification' },
  { code: 'CBAM', name: 'Carbon Border Adjustment', description: 'EU export readiness' },
];

// Industrial scene SVG - enters small and zooms in
const IndustrialSceneSVG = () => (
  <svg viewBox="0 0 1000 500" className="w-full h-full" style={{ filter: 'drop-shadow(0 30px 80px rgba(0,0,0,0.15))' }}>
    <defs>
      <linearGradient id="industry-sky" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#f8fafc" />
        <stop offset="100%" stopColor="#e2e8f0" />
      </linearGradient>
      <linearGradient id="industry-building" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#475569" />
        <stop offset="100%" stopColor="#334155" />
      </linearGradient>
      <linearGradient id="industry-smoke" x1="0%" y1="100%" x2="0%" y2="0%">
        <stop offset="0%" stopColor="#94a3b8" stopOpacity="0.5" />
        <stop offset="100%" stopColor="#cbd5e1" stopOpacity="0" />
      </linearGradient>
      <filter id="industry-shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="4" stdDeviation="8" floodOpacity="0.1"/>
      </filter>
    </defs>
    
    {/* Sky */}
    <rect width="1000" height="500" fill="url(#industry-sky)" />
    
    {/* Ground plane */}
    <rect x="0" y="380" width="1000" height="120" fill="#cbd5e1" />
    <rect x="0" y="380" width="1000" height="3" fill="#94a3b8" />
    
    {/* Building 1 - Main factory */}
    <g filter="url(#industry-shadow)">
      <rect x="80" y="140" width="250" height="240" fill="url(#industry-building)" rx="2" />
      {/* Windows */}
      {[0, 1, 2].map((row) => 
        [0, 1, 2, 3].map((col) => (
          <rect key={`w1-${row}-${col}`} x={100 + col * 55} y={160 + row * 60} width="35" height="40" fill="#64748b" opacity="0.4" rx="1" />
        ))
      )}
      {/* Roof structure */}
      <polygon points="80,140 205,80 330,140" fill="#334155" />
      {/* Chimney */}
      <rect x="170" y="40" width="35" height="100" fill="#475569" />
      <ellipse cx="187" cy="40" rx="17" ry="6" fill="#64748b" />
      {/* Smoke */}
      <ellipse cx="187" cy="15" rx="25" ry="18" fill="url(#industry-smoke)">
        <animate attributeName="cy" values="15;5;15" dur="4s" repeatCount="indefinite" />
        <animate attributeName="rx" values="25;35;25" dur="4s" repeatCount="indefinite" />
      </ellipse>
    </g>
    
    {/* Building 2 - Warehouse */}
    <g filter="url(#industry-shadow)">
      <rect x="380" y="200" width="200" height="180" fill="url(#industry-building)" rx="2" />
      {/* Curved roof */}
      <path d="M380 200 Q480 140 580 200" fill="#3f3f46" />
      {/* Large doors */}
      <rect x="400" y="280" width="70" height="100" fill="#1f2937" rx="2" />
      <rect x="490" y="280" width="70" height="100" fill="#1f2937" rx="2" />
      {/* Solar panels */}
      <rect x="400" y="165" width="40" height="25" fill="#1e40af" opacity="0.7" rx="1" />
      <rect x="450" y="155" width="40" height="25" fill="#1e40af" opacity="0.7" rx="1" />
      <rect x="500" y="160" width="40" height="25" fill="#1e40af" opacity="0.7" rx="1" />
    </g>
    
    {/* Building 3 - Processing unit */}
    <g filter="url(#industry-shadow)">
      <rect x="650" y="180" width="180" height="200" fill="url(#industry-building)" rx="2" />
      {/* Windows */}
      {[0, 1].map((row) =>
        [0, 1, 2].map((col) => (
          <rect key={`w3-${row}-${col}`} x={665 + col * 50} y={200 + row * 55} width="35" height="35" fill="#64748b" opacity="0.4" rx="1" />
        ))
      )}
      {/* Tanks */}
      <ellipse cx="710" cy="320" rx="25" ry="35" fill="#64748b" />
      <ellipse cx="780" cy="330" rx="20" ry="30" fill="#64748b" />
      {/* Chimney 2 */}
      <rect x="800" y="100" width="25" height="80" fill="#475569" />
      <ellipse cx="812" cy="85" rx="18" ry="12" fill="url(#industry-smoke)">
        <animate attributeName="cy" values="85;70;85" dur="5s" repeatCount="indefinite" />
      </ellipse>
    </g>
    
    {/* Carbonseed sensors (green dots with pulse) */}
    {[
      { cx: 300, cy: 200 },
      { cx: 520, cy: 250 },
      { cx: 750, cy: 230 },
      { cx: 180, cy: 180 },
      { cx: 680, cy: 350 },
    ].map((pos, i) => (
      <g key={i}>
        <circle cx={pos.cx} cy={pos.cy} r="8" fill="#059669">
          <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" begin={`${i * 0.4}s`} repeatCount="indefinite" />
        </circle>
        <circle cx={pos.cx} cy={pos.cy} r="16" fill="none" stroke="#059669" strokeWidth="2" opacity="0.3">
          <animate attributeName="r" values="8;20;8" dur="2s" begin={`${i * 0.4}s`} repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.5;0;0.5" dur="2s" begin={`${i * 0.4}s`} repeatCount="indefinite" />
        </circle>
      </g>
    ))}
    
    {/* Data flow lines (connecting sensors) */}
    <path 
      d="M300 200 Q400 150 520 250 Q620 200 750 230" 
      fill="none" 
      stroke="#059669" 
      strokeWidth="2" 
      strokeDasharray="8 4"
      opacity="0.3"
    >
      <animate attributeName="stroke-dashoffset" values="0;-24" dur="2s" repeatCount="indefinite" />
    </path>
    
    {/* Forklift */}
    <g>
      <rect x="600" y="360" width="50" height="25" fill="#eab308" rx="2" />
      <rect x="580" y="365" width="25" height="15" fill="#ca8a04" rx="1" />
      <rect x="650" y="355" width="4" height="30" fill="#78716c" />
      <rect x="640" y="345" width="20" height="8" fill="#78716c" />
      <circle cx="600" cy="390" r="10" fill="#3f3f46" />
      <circle cx="635" cy="390" r="10" fill="#3f3f46" />
    </g>
    
    {/* Truck */}
    <g>
      <rect x="40" y="355" width="80" height="35" fill="#4b5563" rx="2" />
      <rect x="10" y="365" width="35" height="25" fill="#374151" rx="2" />
      <rect x="15" y="370" width="25" height="12" fill="#60a5fa" opacity="0.4" rx="1" />
      <circle cx="30" cy="395" r="12" fill="#1f2937" />
      <circle cx="100" cy="395" r="12" fill="#1f2937" />
    </g>
  </svg>
);

// Context details that update as zoom progresses
const contextDetails = [
  { progress: 0.2, title: 'Real-time Monitoring', desc: 'Every sensor connected, every reading captured' },
  { progress: 0.4, title: 'Data Integration', desc: 'Seamless flow from edge to cloud' },
  { progress: 0.6, title: 'Operational Intelligence', desc: 'AI-powered insights for every machine' },
  { progress: 0.8, title: 'Compliance Ready', desc: 'Automated reporting for regulatory bodies' },
];

export const TechnologySection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const complianceRef = useRef(null);
  const isComplianceInView = useInView(complianceRef, { once: true, margin: "-100px" });
  const [currentDetail, setCurrentDetail] = useState(0);
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });
  
  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    const detailIndex = contextDetails.findIndex((d, i) => {
      const next = contextDetails[i + 1];
      return latest >= d.progress && (!next || latest < next.progress);
    });
    if (detailIndex !== -1 && detailIndex !== currentDetail) {
      setCurrentDetail(detailIndex);
    }
  });
  
  // Industry image zoom effect - starts small and distant, zooms in
  const imageScale = useTransform(scrollYProgress, [0, 0.3, 0.7], [0.4, 0.8, 1.1]);
  const imageY = useTransform(scrollYProgress, [0, 0.5], [100, 0]);
  const imageOpacity = useTransform(scrollYProgress, [0, 0.15, 0.8, 1], [0, 1, 1, 0.8]);
  
  // Content reveals
  const titleOpacity = useTransform(scrollYProgress, [0.1, 0.25], [0, 1]);
  const titleY = useTransform(scrollYProgress, [0.1, 0.25], [40, 0]);
  
  // Detail card opacity based on progress
  const detailOpacity = useTransform(scrollYProgress, [0.2, 0.3, 0.85, 0.95], [0, 1, 1, 0]);
  
  // Industry cards appear after zoom settles
  const cardsOpacity = useTransform(scrollYProgress, [0.65, 0.8], [0, 1]);
  const cardsY = useTransform(scrollYProgress, [0.65, 0.8], [60, 0]);

  return (
    <section ref={containerRef} id="industries" className="relative">
      {/* Industry Scene with Zoom Effect - Pinned Section */}
      <div className="h-[350vh] relative">
        <div className="sticky top-0 h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-surface to-surface-muted">
          {/* Subtle background pattern */}
          <div className="absolute inset-0 opacity-[0.015] pointer-events-none">
            <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="industry-grid" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
                  <rect width="60" height="60" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-ink" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#industry-grid)" />
            </svg>
          </div>
          
          {/* Section label */}
          <motion.div 
            style={{ opacity: titleOpacity, y: titleY }}
            className="absolute top-8 left-1/2 -translate-x-1/2 text-center z-30"
          >
            <span className="label-sm text-accent-green mb-2 block">Industries We Serve</span>
            <h2 className="heading-lg text-ink">
              Built for Indian manufacturing.
            </h2>
          </motion.div>
          
          {/* Industrial scene - zooms from small to large */}
          <motion.div 
            style={{ 
              scale: imageScale, 
              y: imageY,
              opacity: imageOpacity 
            }}
            className="absolute inset-0 flex items-center justify-center z-10 px-8"
          >
            <div className="w-full max-w-5xl">
              <IndustrialSceneSVG />
            </div>
          </motion.div>
          
          {/* Context detail card - updates as scroll progresses */}
          <motion.div 
            style={{ opacity: detailOpacity }}
            className="absolute bottom-24 left-1/2 -translate-x-1/2 z-30"
          >
            <div className="bg-surface-elevated/95 backdrop-blur-md rounded-xl border border-border px-8 py-5 shadow-2xl shadow-ink/5 text-center min-w-[300px]">
              <motion.div
                key={currentDetail}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              >
                <span className="text-xs font-mono text-accent-green mb-1 block">
                  {String(currentDetail + 1).padStart(2, '0')} / {String(contextDetails.length).padStart(2, '0')}
                </span>
                <h3 className="text-lg font-semibold text-ink mb-1">
                  {contextDetails[currentDetail].title}
                </h3>
                <p className="text-sm text-ink-muted">
                  {contextDetails[currentDetail].desc}
                </p>
              </motion.div>
            </div>
          </motion.div>
          
          {/* Industries grid - appears after zoom settles */}
          <motion.div 
            style={{ opacity: cardsOpacity, y: cardsY }}
            className="absolute bottom-32 left-0 right-0 z-20 px-4"
          >
            <div className="max-w-6xl mx-auto">
              <div className="flex flex-wrap justify-center gap-3">
                {industries.map((industry, index) => (
                  <motion.div
                    key={industry.name}
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ 
                      duration: 0.4, 
                      delay: index * 0.05, 
                      ease: [0.16, 1, 0.3, 1] 
                    }}
                    className="group"
                  >
                    <div className="px-4 py-3 bg-surface-elevated/80 backdrop-blur-sm rounded-lg border border-border/60 hover:border-accent-green/40 hover:shadow-lg transition-all duration-300 flex items-center gap-3">
                      <span className="text-lg">{industry.icon}</span>
                      <div>
                        <h3 className="text-sm font-medium text-ink group-hover:text-accent-green transition-colors">{industry.name}</h3>
                        <p className="text-xs text-ink-faint">{industry.description}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Compliance Section - Follows naturally */}
      <div className="section-spacing bg-surface-muted relative z-30">
        <div className="container-wide">
          <motion.div
            ref={complianceRef}
            initial={{ opacity: 0, y: 30 }}
            animate={isComplianceInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="label-sm text-accent-amber mb-4 block">Compliance</span>
            <h2 className="heading-lg text-ink max-w-2xl mb-12">
              Regulatory readiness, automated.
            </h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              {complianceItems.map((item, index) => (
                <motion.div
                  key={item.code}
                  initial={{ opacity: 0, y: 20 }}
                  animate={isComplianceInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                  transition={{ duration: 0.5, delay: 0.2 + index * 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="group relative p-6 bg-surface-elevated rounded-xl border border-border hover:border-accent-amber/30 transition-all duration-300"
                >
                  {/* Accent line */}
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-accent-amber via-accent-amber/50 to-transparent rounded-l-xl" />
                  
                  <span className="font-mono text-sm text-accent-amber">{item.code}</span>
                  <h3 className="font-medium text-ink mt-2 mb-2 group-hover:text-accent-amber transition-colors">{item.name}</h3>
                  <p className="text-sm text-ink-muted">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};