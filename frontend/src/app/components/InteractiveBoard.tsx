'use client';

import { useRef, useEffect, useState } from 'react';
import { motion, useScroll, useTransform, useMotionValueEvent } from 'framer-motion';

// ESP32 Board with separable elements for depth effect
const ESP32BoardExploded = ({ 
  explodeProgress, 
  scale,
  className 
}: { 
  explodeProgress: number;
  scale: number;
  className?: string;
}) => {
  // Elements separate based on explode progress
  const pcbOffset = explodeProgress * 10;
  const chipOffset = explodeProgress * 25;
  const componentOffset = explodeProgress * 15;
  const pinOffset = explodeProgress * 8;
  
  return (
    <svg 
      viewBox="0 0 200 280" 
      className={className}
      style={{ 
        filter: `drop-shadow(0 ${20 + explodeProgress * 30}px ${40 + explodeProgress * 40}px rgba(0,0,0,${0.15 + explodeProgress * 0.1}))`,
        transform: `scale(${scale})`,
        transition: 'filter 0.3s ease-out'
      }}
    >
      <defs>
        <linearGradient id="pcb-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#2d5a3d" />
          <stop offset="100%" stopColor="#1a472a" />
        </linearGradient>
        <filter id="inner-shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feComponentTransfer in="SourceAlpha">
            <feFuncA type="table" tableValues="1 0" />
          </feComponentTransfer>
          <feGaussianBlur stdDeviation="2" />
          <feOffset dx="2" dy="2" result="offsetblur" />
          <feFlood floodColor="#000" floodOpacity="0.3" result="color" />
          <feComposite in2="offsetblur" operator="in" />
          <feComposite in2="SourceAlpha" operator="in" />
          <feMerge>
            <feMergeNode in="SourceGraphic" />
            <feMergeNode />
          </feMerge>
        </filter>
        <filter id="glow-green" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Layer 1: PCB Base - furthest back */}
      <g style={{ transform: `translateZ(${-pcbOffset}px)` }}>
        <rect x="10" y="10" width="180" height="260" rx="4" fill="#1a472a" filter="url(#inner-shadow)" />
        <rect x="14" y="14" width="172" height="252" rx="2" fill="url(#pcb-gradient)" />
        
        {/* Circuit traces */}
        <g stroke="#3d7a52" strokeWidth="0.8" fill="none" opacity="0.7">
          <path d="M30 80 L80 80 L80 120 L120 120" />
          <path d="M100 60 L100 100 L140 100" />
          <path d="M60 180 L60 220 L100 220 L100 200" />
          <path d="M140 160 L140 200 L160 200" />
          <path d="M40 140 L80 140 L80 180" />
          <path d="M30 100 L50 100 L50 130" />
          <path d="M150 120 L170 120 L170 150" />
        </g>
        
        {/* Solder points */}
        {[
          [50, 80], [80, 120], [100, 100], [140, 160], [60, 180],
          [100, 220], [30, 140], [170, 200], [50, 130], [170, 150]
        ].map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="2" fill="#5a8a6a" opacity="0.6" />
        ))}
      </g>
      
      {/* Layer 2: Main ESP32 Chip - middle */}
      <g style={{ transform: `translateY(${-chipOffset}px)` }}>
        <rect x="60" y="90" width="80" height="60" rx="3" fill="#0a0a0a" />
        <rect x="63" y="93" width="74" height="54" rx="2" fill="#1a1a1a" />
        <rect x="66" y="96" width="68" height="48" rx="1" fill="#262626" />
        
        {/* Chip markings */}
        <text x="100" y="118" textAnchor="middle" fill="#555" fontSize="7" fontFamily="monospace" fontWeight="600">ESP32</text>
        <text x="100" y="130" textAnchor="middle" fill="#444" fontSize="5" fontFamily="monospace">WROOM-32</text>
        
        {/* Chip corner marker */}
        <circle cx="72" cy="102" r="2" fill="#333" />
      </g>
      
      {/* Layer 3: Chip pins - separate layer */}
      <g style={{ transform: `translateY(${-pinOffset}px)` }}>
        {/* Pins left */}
        {[0, 1, 2, 3, 4, 5, 6].map((i) => (
          <rect key={`pin-l-${i}`} x="52" y={93 + i * 7} width="8" height="3" rx="0.5" fill="#c0c0c0" />
        ))}
        {/* Pins right */}
        {[0, 1, 2, 3, 4, 5, 6].map((i) => (
          <rect key={`pin-r-${i}`} x="140" y={93 + i * 7} width="8" height="3" rx="0.5" fill="#c0c0c0" />
        ))}
      </g>
      
      {/* Layer 4: Components - closest to viewer */}
      <g style={{ transform: `translateY(${-componentOffset}px)` }}>
        {/* Antenna module */}
        <rect x="75" y="18" width="50" height="52" rx="3" fill="#0f0f0f" stroke="#333" strokeWidth="1" />
        <rect x="80" y="23" width="40" height="42" rx="2" fill="#1a1a1a" />
        <path d="M88 33 L112 33 L112 55 L88 55 Z" fill="none" stroke="#404040" strokeWidth="1.5" />
        <path d="M95 40 L105 40 M100 35 L100 45" stroke="#505050" strokeWidth="1" />
        
        {/* USB-C port */}
        <rect x="82" y="248" width="36" height="16" rx="3" fill="#2a2a2a" />
        <rect x="87" y="252" width="26" height="8" rx="2" fill="#0f0f0f" />
        
        {/* Capacitors */}
        <rect x="28" y="168" width="18" height="10" rx="2" fill="#8b7355" />
        <rect x="154" y="168" width="18" height="10" rx="2" fill="#8b7355" />
        
        {/* Resistor array */}
        <rect x="28" y="198" width="14" height="8" rx="1" fill="#1f1f1f" />
        <rect x="158" y="198" width="14" height="8" rx="1" fill="#1f1f1f" />
        
        {/* Crystal oscillator */}
        <rect x="130" y="75" width="20" height="8" rx="1" fill="#c0c0c0" />
        
        {/* Status LEDs */}
        <circle 
          cx="35" 
          cy="40" 
          r="5" 
          fill={`rgba(5, 150, 105, ${0.3 + explodeProgress * 0.7})`}
          filter={explodeProgress > 0.3 ? "url(#glow-green)" : undefined}
        />
        <circle 
          cx="35" 
          cy="58" 
          r="5" 
          fill={`rgba(59, 130, 246, ${0.2 + explodeProgress * 0.5})`}
        />
        
        {/* Reset button */}
        <circle cx="165" cy="45" r="7" fill="#222" stroke="#444" strokeWidth="1" />
        <circle cx="165" cy="45" r="5" fill="#333" />
        
        {/* GPIO headers */}
        <g>
          {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <circle key={`gpio-l-${i}`} cx="23" cy={85 + i * 11} r="2.5" fill="#d4af37" />
          ))}
          {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <circle key={`gpio-r-${i}`} cx="177" cy={85 + i * 11} r="2.5" fill="#d4af37" />
          ))}
        </g>
      </g>
    </svg>
  );
};

// Highway/Tunnel visualization
const HighwayTunnel = ({ progress }: { progress: number }) => {
  const tunnelOpacity = Math.max(0, Math.min(1, (progress - 0.15) * 4));
  const tunnelScale = 0.8 + progress * 0.4;
  
  return (
    <div 
      className="absolute inset-0 flex items-center justify-center pointer-events-none"
      style={{ opacity: tunnelOpacity }}
    >
      <svg 
        viewBox="0 0 1200 800" 
        className="w-full h-full max-w-6xl"
        preserveAspectRatio="xMidYMid slice"
        style={{ transform: `scale(${tunnelScale})` }}
      >
        <defs>
          {/* Tunnel gradient */}
          <linearGradient id="tunnel-gradient" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#1a472a" stopOpacity="0" />
            <stop offset="30%" stopColor="#1a472a" stopOpacity="0.1" />
            <stop offset="70%" stopColor="#2d5a3d" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#1a472a" stopOpacity="0" />
          </linearGradient>
          
          {/* Road surface gradient */}
          <linearGradient id="road-surface" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#1a472a" stopOpacity="0" />
            <stop offset="20%" stopColor="#2d5a3d" stopOpacity="0.6" />
            <stop offset="50%" stopColor="#3d6b4d" stopOpacity="0.8" />
            <stop offset="80%" stopColor="#2d5a3d" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#1a472a" stopOpacity="0" />
          </linearGradient>
          
          {/* Perspective lines pattern */}
          <pattern id="circuit-lines" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
            <path d="M0 50 L40 50 L50 40 L50 0" fill="none" stroke="#4a9960" strokeWidth="0.5" opacity="0.3" />
            <path d="M100 50 L60 50 L50 60 L50 100" fill="none" stroke="#4a9960" strokeWidth="0.5" opacity="0.3" />
            <circle cx="50" cy="50" r="3" fill="#4a9960" opacity="0.2" />
          </pattern>
        </defs>
        
        {/* Vanishing point road */}
        <path
          d="M600 100 
             L300 800 
             L900 800 
             Z"
          fill="url(#road-surface)"
        />
        
        {/* Road edges - perspective lines */}
        <path
          d="M600 100 L300 800"
          fill="none"
          stroke="#4a9960"
          strokeWidth="3"
          opacity="0.4"
        />
        <path
          d="M600 100 L900 800"
          fill="none"
          stroke="#4a9960"
          strokeWidth="3"
          opacity="0.4"
        />
        
        {/* Center dashed line */}
        <path
          d="M600 100 L600 800"
          fill="none"
          stroke="#5aaa70"
          strokeWidth="4"
          strokeDasharray="30 20"
          opacity="0.5"
        />
        
        {/* Horizontal perspective lines */}
        {[150, 200, 270, 360, 480, 640].map((y, i) => {
          const width = 100 + (y - 100) * 0.7;
          return (
            <path
              key={i}
              d={`M${600 - width} ${y} L${600 + width} ${y}`}
              fill="none"
              stroke="#4a9960"
              strokeWidth="1"
              opacity={0.15 + i * 0.05}
            />
          );
        })}
        
        {/* Circuit pattern overlay */}
        <rect
          x="200"
          y="0"
          width="800"
          height="800"
          fill="url(#circuit-lines)"
          opacity="0.3"
          style={{
            clipPath: 'polygon(50% 12.5%, 25% 100%, 75% 100%)'
          }}
        />
        
        {/* Glowing center point (vanishing point) */}
        <circle cx="600" cy="100" r="8" fill="#059669" opacity="0.6">
          <animate attributeName="r" values="8;12;8" dur="3s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.6;0.9;0.6" dur="3s" repeatCount="indefinite" />
        </circle>
        <circle cx="600" cy="100" r="20" fill="none" stroke="#059669" strokeWidth="2" opacity="0.3">
          <animate attributeName="r" values="20;30;20" dur="3s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  );
};

// Feature Signboard Component
interface FeatureSignboard {
  id: string;
  number: string;
  title: string;
  description: string;
  detail: string;
  position: 'left' | 'right';
  triggerProgress: number;
}

const featureSignboards: FeatureSignboard[] = [
  {
    id: 'sensing',
    number: '01',
    title: 'Edge Sensing',
    description: 'Industrial-grade precision',
    detail: 'ESP32 captures temperature (±0.1°C), vibration (3-axis), gas levels, humidity, and power at 100Hz sampling rate.',
    position: 'left',
    triggerProgress: 0.35
  },
  {
    id: 'streaming',
    number: '02',
    title: 'Real-time Streaming',
    description: 'Sub-second latency',
    detail: 'MQTT protocol streams data to cloud with automatic buffering, compression, and offline resilience.',
    position: 'right',
    triggerProgress: 0.45
  },
  {
    id: 'intelligence',
    number: '03',
    title: 'ML Intelligence',
    description: 'Physics-informed models',
    detail: 'Neural networks trained on industrial patterns detect anomalies and predict failures 48 hours in advance.',
    position: 'left',
    triggerProgress: 0.55
  },
  {
    id: 'compliance',
    number: '04',
    title: 'Auto Compliance',
    description: 'Regulatory automation',
    detail: 'Generate audit-ready reports for SPCB, PAT Scheme, and CBAM with zero manual intervention.',
    position: 'right',
    triggerProgress: 0.65
  }
];

const Signboard = ({ 
  feature, 
  progress, 
  index 
}: { 
  feature: FeatureSignboard; 
  progress: number;
  index: number;
}) => {
  const isVisible = progress > feature.triggerProgress;
  const localProgress = isVisible ? Math.min(1, (progress - feature.triggerProgress) * 5) : 0;
  
  const xOffset = feature.position === 'left' ? -100 : 100;
  const currentX = xOffset * (1 - localProgress);
  
  return (
    <motion.div
      className={`absolute ${
        feature.position === 'left' 
          ? 'left-4 md:left-8 lg:left-16 xl:left-24' 
          : 'right-4 md:right-8 lg:right-16 xl:right-24'
      }`}
      style={{
        top: `${25 + index * 15}%`,
        opacity: localProgress,
        x: currentX,
        zIndex: 30 + index
      }}
    >
      <div className={`
        relative max-w-xs md:max-w-sm
        ${feature.position === 'left' ? 'text-left' : 'text-right'}
      `}>
        {/* Signboard frame */}
        <div className="relative bg-surface-elevated/95 backdrop-blur-md rounded-xl border border-border/80 p-6 shadow-2xl shadow-ink/10">
          {/* Accent bar */}
          <div className={`absolute top-0 ${feature.position === 'left' ? 'left-0' : 'right-0'} w-1 h-full bg-gradient-to-b from-accent-green via-accent-green/50 to-transparent rounded-full`} />
          
          {/* Number badge */}
          <div className={`inline-flex items-center gap-2 mb-3 ${feature.position === 'right' ? 'flex-row-reverse' : ''}`}>
            <span className="text-xs font-mono text-accent-green bg-accent-green/10 px-2 py-1 rounded">
              {feature.number}
            </span>
            <div className="w-8 h-px bg-gradient-to-r from-accent-green/50 to-transparent" />
          </div>
          
          {/* Title */}
          <h3 className="text-lg md:text-xl font-semibold text-ink mb-1">
            {feature.title}
          </h3>
          
          {/* Subtitle */}
          <p className="text-sm font-mono text-accent-blue mb-3">
            {feature.description}
          </p>
          
          {/* Detail */}
          <p className="text-sm text-ink-muted leading-relaxed">
            {feature.detail}
          </p>
          
          {/* Connection line to road */}
          <div className={`absolute top-1/2 ${feature.position === 'left' ? '-right-8' : '-left-8'} w-8 h-px bg-gradient-to-r ${feature.position === 'left' ? 'from-transparent to-accent-green/30' : 'from-accent-green/30 to-transparent'}`} />
        </div>
      </div>
    </motion.div>
  );
};

// Subtle background mesh
const BackgroundMesh = ({ scrollProgress }: { scrollProgress: number }) => (
  <div className="absolute inset-0 pointer-events-none overflow-hidden">
    {/* Floating gradient orbs */}
    <motion.div
      className="absolute top-[10%] left-[5%] w-[500px] h-[500px] rounded-full"
      style={{
        background: 'radial-gradient(circle, rgba(5, 150, 105, 0.03) 0%, transparent 70%)',
        x: scrollProgress * 50,
        y: scrollProgress * -30,
      }}
    />
    <motion.div
      className="absolute top-[40%] right-[10%] w-[400px] h-[400px] rounded-full"
      style={{
        background: 'radial-gradient(circle, rgba(100, 116, 139, 0.03) 0%, transparent 70%)',
        x: scrollProgress * -40,
        y: scrollProgress * 20,
      }}
    />
    <motion.div
      className="absolute bottom-[20%] left-[30%] w-[600px] h-[600px] rounded-full"
      style={{
        background: 'radial-gradient(circle, rgba(217, 119, 6, 0.02) 0%, transparent 70%)',
        x: scrollProgress * 30,
        y: scrollProgress * -40,
      }}
    />
    
    {/* Rectangular mesh pattern */}
    <svg className="absolute inset-0 w-full h-full opacity-[0.02]" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="mesh-pattern" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
          <rect x="0" y="0" width="40" height="40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-ink" />
          <rect x="40" y="40" width="40" height="40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-ink" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#mesh-pattern)" />
    </svg>
  </div>
);

// Main component
export const InteractiveBoardSection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });
  
  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    setCurrentProgress(latest);
  });

  // Phase calculations
  // Phase 1 (0-20%): Board dominates, slight depth separation
  // Phase 2 (20-35%): Board recedes, highway appears
  // Phase 3 (35-75%): Features appear along highway
  // Phase 4 (75-100%): Transition out
  
  const boardScale = useTransform(
    scrollYProgress, 
    [0, 0.1, 0.25, 0.75], 
    [1.2, 1, 0.35, 0.2]
  );
  
  const boardY = useTransform(
    scrollYProgress,
    [0, 0.1, 0.3, 0.75],
    [0, 0, -150, -300]
  );
  
  const boardOpacity = useTransform(
    scrollYProgress,
    [0, 0.2, 0.7, 0.8],
    [1, 1, 0.8, 0]
  );
  
  const explodeProgress = useTransform(
    scrollYProgress,
    [0.05, 0.25],
    [0, 1]
  );
  
  const highwayOpacity = useTransform(
    scrollYProgress,
    [0.15, 0.3, 0.75, 0.85],
    [0, 1, 1, 0]
  );
  
  const headlineOpacity = useTransform(
    scrollYProgress,
    [0, 0.05, 0.2, 0.3],
    [0, 1, 1, 0]
  );
  
  const headlineY = useTransform(
    scrollYProgress,
    [0, 0.05],
    [30, 0]
  );
  
  const sectionEndOpacity = useTransform(
    scrollYProgress,
    [0.8, 0.95],
    [0, 1]
  );

  return (
    <section 
      ref={containerRef} 
      id="features"
      className="relative h-[600vh]"
    >
      {/* Pinned container */}
      <div className="sticky top-0 h-screen overflow-hidden bg-surface">
        {/* Background mesh */}
        <BackgroundMesh scrollProgress={currentProgress} />
        
        {/* Highway/Tunnel layer - z-10 */}
        <motion.div 
          style={{ opacity: highwayOpacity }}
          className="absolute inset-0 z-10"
        >
          <HighwayTunnel progress={currentProgress} />
        </motion.div>
        
        {/* Feature signboards - z-30 */}
        <div className="absolute inset-0 z-30">
          {featureSignboards.map((feature, index) => (
            <Signboard 
              key={feature.id}
              feature={feature}
              progress={currentProgress}
              index={index}
            />
          ))}
        </div>
        
        {/* ESP32 Board - z-40 (foreground) */}
        <motion.div 
          style={{ 
            scale: boardScale,
            y: boardY,
            opacity: boardOpacity,
          }}
          className="absolute inset-0 flex flex-col items-center justify-center z-40 pointer-events-none"
        >
          {/* Headline above board */}
          <motion.div 
            style={{ opacity: headlineOpacity, y: headlineY }}
            className="text-center mb-8 px-4"
          >
            <span className="label-sm text-accent-green mb-3 block">The Technology</span>
            <h2 className="heading-lg text-ink max-w-2xl">
              Precision-engineered for Indian industry.
            </h2>
          </motion.div>
          
          {/* The Board */}
          <div className="w-48 md:w-64 lg:w-80">
            <ESP32BoardExploded 
              explodeProgress={explodeProgress.get()}
              scale={1}
              className="w-full h-auto"
            />
          </div>
          
          {/* Tagline below board */}
          <motion.p 
            style={{ opacity: headlineOpacity }}
            className="mt-6 text-sm font-mono text-ink-faint"
          >
            ESP32-based edge sensing • Made for harsh environments
          </motion.p>
        </motion.div>
        
        {/* Scroll progress indicator */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 z-50 hidden lg:block">
          <div className="h-32 w-0.5 bg-border/50 rounded-full overflow-hidden">
            <motion.div 
              style={{ scaleY: scrollYProgress, transformOrigin: 'top' }}
              className="w-full h-full bg-accent-green"
            />
          </div>
          <span className="block mt-2 text-xs font-mono text-ink-faint">
            {Math.round(currentProgress * 100)}%
          </span>
        </div>
        
        {/* End of journey indicator */}
        <motion.div 
          style={{ opacity: sectionEndOpacity }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 z-50 text-center"
        >
          <span className="text-sm font-mono text-ink-faint">Journey complete</span>
          <div className="mt-2 w-6 h-6 mx-auto border-b-2 border-r-2 border-ink-faint rotate-45 animate-bounce" />
        </motion.div>
      </div>
    </section>
  );
};