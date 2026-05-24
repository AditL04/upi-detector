import React, { useEffect, useRef, useState } from "react";
import "./App.css";

/* ════════════════════════════════════
   PARTICLE CANVAS
════════════════════════════════════ */
function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animId;

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const particles = Array.from({ length: 55 }, () => ({
      x:     Math.random() * canvas.width,
      y:     Math.random() * canvas.height,
      r:     Math.random() * 2.2 + 0.5,
      dx:    (Math.random() - 0.5) * 0.35,
      dy:    (Math.random() - 0.5) * 0.35,
      alpha: Math.random() * 0.3 + 0.08,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p) => {
        p.x += p.dx;
        p.y += p.dy;
        if (p.x < 0 || p.x > canvas.width)  p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(79,70,229,${p.alpha})`;
        ctx.fill();
      });

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dist = Math.hypot(
            particles[i].x - particles[j].x,
            particles[i].y - particles[j].y
          );
          if (dist < 115) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(79,70,229,${0.06 * (1 - dist / 115)})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" />;
}

/* ════════════════════════════════════
   TYPEWRITER
════════════════════════════════════ */
function Typewriter({ words, speed = 80, pause = 2000 }) {
  const [display,  setDisplay]  = useState("");
  const [wordIdx,  setWordIdx]  = useState(0);
  const [charIdx,  setCharIdx]  = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = words[wordIdx];
    let t;

    if (!deleting && charIdx <= current.length) {
      setDisplay(current.slice(0, charIdx));
      t = setTimeout(() => setCharIdx(c => c + 1), speed);
    } else if (!deleting && charIdx > current.length) {
      t = setTimeout(() => setDeleting(true), pause);
    } else if (deleting && charIdx >= 0) {
      setDisplay(current.slice(0, charIdx));
      t = setTimeout(() => setCharIdx(c => c - 1), speed / 2);
    } else {
      setDeleting(false);
      setWordIdx(w => (w + 1) % words.length);
    }
    return () => clearTimeout(t);
  }, [charIdx, deleting, wordIdx, words, speed, pause]);

  return (
    <span className="typewriter">
      {display}<span className="cursor-blink">|</span>
    </span>
  );
}

/* ════════════════════════════════════
   ANIMATED COUNTER
════════════════════════════════════ */
function Counter({ target, suffix = "", duration = 1800 }) {
  const [value, setValue] = useState(0);
  const ref     = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          const tick = (now) => {
            const p    = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - p, 3);
            setValue(Math.floor(ease * target));
            if (p < 1) requestAnimationFrame(tick);
            else setValue(target);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.5 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [target, duration]);

  return <span ref={ref} className="stat-value">{value}{suffix}</span>;
}

/* ════════════════════════════════════
   MAGNETIC BUTTON
════════════════════════════════════ */
function MagneticBtn({ children, className, onClick }) {
  const ref = useRef(null);

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    const x = e.clientX - r.left - r.width  / 2;
    const y = e.clientY - r.top  - r.height / 2;
    ref.current.style.transform    = `translate(${x * 0.26}px,${y * 0.26}px) scale(1.04)`;
    ref.current.style.transition   = "transform 0.12s ease";
  };

  const onLeave = () => {
    ref.current.style.transform  = "translate(0,0) scale(1)";
    ref.current.style.transition = "transform 0.55s cubic-bezier(0.25,0.46,0.45,0.94)";
  };

  return (
    <button
      ref={ref}
      className={className}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

/* ════════════════════════════════════
   TILT CARD
════════════════════════════════════ */
function TiltCard({ children, className }) {
  const ref = useRef(null);

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width  - 0.5;
    const y = (e.clientY - r.top)  / r.height - 0.5;
    ref.current.style.transform  = `perspective(900px) rotateX(${-y * 11}deg) rotateY(${x * 11}deg) scale(1.03)`;
    ref.current.style.transition = "transform 0.1s ease";
    const shine = ref.current.querySelector(".card-shine");
    if (shine) {
      shine.style.opacity    = "1";
      shine.style.background = `radial-gradient(circle at ${(x + 0.5) * 100}% ${(y + 0.5) * 100}%, rgba(255,255,255,0.2), transparent 65%)`;
    }
  };

  const onLeave = () => {
    ref.current.style.transform  = "perspective(900px) rotateX(0) rotateY(0) scale(1)";
    ref.current.style.transition = "transform 0.6s cubic-bezier(0.25,0.46,0.45,0.94)";
    const shine = ref.current.querySelector(".card-shine");
    if (shine) shine.style.opacity = "0";
  };

  return (
    <div ref={ref} className={className} onMouseMove={onMove} onMouseLeave={onLeave}>
      {children}
    </div>
  );
}

/* ════════════════════════════════════
   MAIN APP
════════════════════════════════════ */
export default function App() {
  const [navScrolled,  setNavScrolled]  = useState(false);
  const [mousePos,     setMousePos]     = useState({ x: -999, y: -999 });
  const [scanActive,   setScanActive]   = useState(false);
  const [toastVisible, setToastVisible] = useState(false);
  const [prediction, setPrediction] = useState("READY");
  const [confidence, setConfidence] = useState(null);
  const fileInputRef = useRef(null);

  /* Navbar scroll */
  useEffect(() => {
    const onScroll = () => setNavScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* Mouse spotlight */
  useEffect(() => {
    const onMove = (e) => setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  /* Scroll reveal */
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("visible"); }),
      { threshold: 0.1, rootMargin: "0px 0px -36px 0px" }
    );
    document.querySelectorAll(".reveal").forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);

  /* Toast */
  useEffect(() => {
    const t = setTimeout(() => {
      setToastVisible(true);
      setTimeout(() => setToastVisible(false), 4500);
    }, 3000);
    return () => clearTimeout(t);
  }, []);

  const FEATURES = [
    {
      icon: "⚡",
      title: "Lightning Fast Scan",
      desc: "Upload any UPI screenshot and receive a fraud verdict in under 3 seconds — no queues, no delays, no compromise.",
      tag: "Speed",
    },
    {
      icon: "🔍",
      title: "Deep Visual Analysis",
      desc: "Detects edited amounts, font inconsistencies, pixel manipulation, metadata tampering, and fake overlays invisible to the human eye.",
      tag: "Accuracy",
    },
    {
      icon: "🔒",
      title: "Secure & Private",
      desc: "Screenshots are analyzed in isolated memory and deleted within 60 seconds. Your data never touches long-term storage.",
      tag: "Privacy",
    },
  ];

  const STEPS = [
    {
      num: "01",
      title: "Upload Screenshot",
      desc: "Drag & drop or tap to upload any UPI payment screenshot from GPay, PhonePe, Paytm, or any app.",
    },
    {
      num: "02",
      title: "AI Checks Every Detail",
      desc: "Our model inspects pixel patterns, EXIF metadata, font rendering, amount semantics, and layout consistency.",
    },
    {
      num: "03",
      title: "Instant Fraud Report",
      desc: "Get a detailed verdict with fraud confidence score, highlighted anomalies, and an exportable evidence summary.",
    },
  ];

  const BRANDS = [
    "Meesho Sellers", "Etsy India", "OLX Merchants", "Freelancers",
    "D2C Brands", "Instagram Shops", "Flipkart Sellers", "Local Vendors",
    "Meesho Sellers", "Etsy India", "OLX Merchants", "Freelancers",
    "D2C Brands", "Instagram Shops", "Flipkart Sellers", "Local Vendors",
  ];
  const handleFileChange = async (e) => {

  const file = e.target.files[0];
  if (!file) return;

  setScanActive(true);

  const formData = new FormData();
  formData.append("file", file);

  try {

    const response = await fetch(
      "http://127.0.0.1:8000/predict",
      {
        method: "POST",
        body: formData
      }
    );

    console.log("Response status:", response.status);

    if (!response.ok) {
      throw new Error("Server returned error status");
    }

    const data = await response.json();

    console.log("Backend data:", data);

    if (!data.prediction || data.cnn_score === undefined) {
      throw new Error("Unexpected response format");
    }

    setPrediction(data.prediction);
    setConfidence((data.cnn_score * 100).toFixed(2));

  }

  catch (err) {

    console.error("Frontend error:", err);
    alert("Prediction failed — check console (F12)");

  }

  setScanActive(false);
};

  return (
    <div
      className="app"
      style={{ "--mx": `${mousePos.x}px`, "--my": `${mousePos.y}px` }}
    >
      <input
  type="file"
  accept="image/*"
  ref={fileInputRef}
  style={{ display: "none" }}
  onChange={handleFileChange}
/>
      {/* Background layers */}
      <ParticleCanvas />
      <div className="spotlight" />
      <div className="bg-blob blob-1" />
      <div className="bg-blob blob-2" />
      <div className="bg-blob blob-3" />

      {/* ── TOAST ── */}
      <div className={`toast-notif ${toastVisible ? "toast-show" : ""}`}>
        <span className="toast-icon">🚨</span>
        <div className="toast-body">
          <strong>Fraud Blocked!</strong>
          <span>Fake ₹12,500 receipt detected · 98.7% confidence</span>
        </div>
        <div className="toast-bar" />
      </div>

      {/* ════════ NAVBAR ════════ */}
      <nav className={`navbar ${navScrolled ? "nav-scrolled" : ""}`}>
        <div className="nav-inner">
          <div className="nav-logo">
            <span className="logo-icon">🛡️</span>
            <span className="logo-text">UPI<span className="logo-accent">Shield</span></span>
          </div>

          <div className="nav-links">
            {["Features", "How it Works"].map((l) => (
              <a key={l} href={`#${l.toLowerCase().replace(/ /g, "-")}`} className="nav-link">
                {l}
              </a>
            ))}
          </div>


        </div>
      </nav>

      {/* ════════ HERO ════════ */}
      <section className="hero" id="hero">
        <div className="hero-content">

          <div className="hero-badge reveal">
            <span className="badge-dot" />
            <span>AI-Powered · Live Fraud Detection</span>
            <span className="badge-shimmer-bar" />
          </div>

          <h1 className="hero-title reveal">
            Detect Fake UPI<br />
            <span className="gradient-text gradient-animated">
              <Typewriter
                words={["Payment Screenshots", "Transaction Proofs", "Receipt Forgeries", "Edited Amounts", "Fake QR Slips"]}
              />
            </span>
            <br />Instantly.
          </h1>

          <p className="hero-subtitle reveal">
            
            Stop payment fraud before it costs you. Our AI scans every pixel —
            edited amounts, fake overlays, and forged receipts detected in
            under&nbsp;3&nbsp;seconds.
          </p>

          <div className="hero-actions reveal">
            <MagneticBtn
              className="btn-primary btn-large btn-glow"
              onClick={() => fileInputRef.current.click()}
            >
              ↑ Upload Screenshot
            </MagneticBtn>
          </div>

          <div className="hero-stats reveal">
            <div className="stat">
              <Counter target={99} suffix=".2%" />
              <span className="stat-label">Accuracy Rate</span>
            </div>
            <div className="stat-divider" />
            <div className="stat">
              <span className="stat-value">&lt;3s</span>
              <span className="stat-label">Scan Speed</span>
            </div>
            <div className="stat-divider" />
            <div className="stat">
              <Counter target={50} suffix="K+" />
              <span className="stat-label">Frauds Blocked</span>
            </div>
          </div>
        </div>

        {/* ── Hero Visual ── */}
        <div className="hero-visual">
          <div className="orbit-ring" />
          <div className="orbit-dot od-1" />
          <div className="orbit-dot od-2" />
          <div className="orbit-dot od-3" />

          {/* Main card */}
          <div className={`mock-card main-card float-anim ${scanActive ? "card-scanning" : ""}`}>
            <div className={`mock-card main-card float-anim ${scanActive ? "card-scanning" : ""}`}>
  <div className="result-display">
    <div className={`result-glow-text ${
      scanActive ? "result-scanning" :
      prediction === "REAL" ? "result-real" :
      prediction === "FAKE" ? "result-fake" : "result-ready"
    }`}>
      {scanActive ? "SCANNING…" : prediction || "READY"}
    </div>
    {confidence !== null && !scanActive && (
      <div className="result-confidence">
        Confidence: {confidence}%
      </div>
    )}
  </div>
  <div className="scan-bar">
    <div className="scan-line" />
  </div>
  {scanActive && (
    <div className="scan-laser-overlay">
      <div className="laser-beam" />
    </div>
  )}
</div>
<div className="scan-bar">
              <div className="scan-line" />
            </div>
            {scanActive && (
              <div className="scan-laser-overlay">
                <div className="laser-beam" />
              </div>
            )}
          </div>

          {/* Mini cards */}
          <div className="mock-card mini-card-1 float-anim-slow">
            <div className="mini-icon">⚠️</div>
            <div className="mini-text">
              <strong>Pixel Mismatch</strong>
              <span>Amount field edited</span>
            </div>
            <div className="mini-ring-pulse" />
          </div>

          <div className="mock-card mini-card-2 float-anim-rev">
            <div className="mini-icon">✅</div>
            <div className="mini-text">
              <strong>Metadata OK</strong>
              <span>Font authentic</span>
            </div>
          </div>

          {/* Accuracy pill */}
          <div className="accuracy-pill float-anim-slow">
            <div className="accuracy-label">Fraud Score</div>
            <div className="accuracy-bar">
              <div className="accuracy-fill" />
            </div>
            <div className="accuracy-value">
  {confidence !== null ? `${confidence}%` : "—"}
</div>
          </div>

          {/* Sparkles */}
          {[...Array(7)].map((_, i) => (
            <div key={i} className={`sparkle sp-${i}`} />
          ))}
        </div>
      </section>

      {/* ════════ MARQUEE ════════ */}
      <section className="trusted">
        <p className="trusted-label">Trusted by businesses across India</p>
        <div className="marquee-wrap">
          <div className="marquee-track">
            {BRANDS.map((b, i) => (
              <span key={i} className="trusted-item">
                <span className="trusted-dot">◆</span>{b}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ════════ FEATURES ════════ */}
      <section className="features" id="features">
        <div className="section-label reveal">Why UPI Shield</div>
        <h2 className="section-title reveal">
          Fraud Detection That<br />
          <span className="gradient-text gradient-animated">Delivers Real Results</span>
        </h2>
        <p className="section-sub reveal">Every fake screenshot has a fingerprint. We find it.</p>

        <div className="features-grid">
          {FEATURES.map((f, i) => (
            <TiltCard
              key={i}
              className="feature-card reveal"
              style={{ transitionDelay: `${i * 0.12}s` }}
            >
              <div className="feature-icon-wrap">
                <span className="feature-icon">{f.icon}</span>
                <div className="icon-halo" />
              </div>
              <div className="feature-tag">{f.tag}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
              <div className="card-shine" />
              <div className="card-bottom-line" />
            </TiltCard>
          ))}
        </div>
      </section>

      {/* ════════ HOW IT WORKS ════════ */}
      <section className="how-it-works" id="how-it-works">
        <div className="section-label reveal">Simple Process</div>
        <h2 className="section-title reveal">
          Three Steps to{" "}
          <span className="gradient-text gradient-animated">Zero Fraud</span>
        </h2>
        <p className="section-sub reveal">
          From upload to verdict in under 3 seconds.
        </p>

        <div className="steps">
          {STEPS.map((s, i) => (
            <React.Fragment key={i}>
              <div
                className="step reveal"
                style={{ transitionDelay: `${i * 0.16}s` }}
              >
                <div className="step-num">{s.num}</div>
                <div className="step-content">
                  <h3>{s.title}</h3>
                  <p>{s.desc}</p>
                </div>
              </div>
              {i < STEPS.length - 1 && (
                <div className="step-connector reveal" style={{ transitionDelay: `${i * 0.16 + 0.08}s` }}>
                  <div className="connector-beam" />
                  <div className="connector-arrow">›</div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* ════════ CTA ════════ */}
      <section className="cta-section">
        <div className="cta-bg-anim" />
        {[...Array(10)].map((_, i) => (
          <div key={i} className={`cta-particle cp-${i}`} />
        ))}
        <div className="cta-inner reveal">
          <div className="cta-glow" />
          <p className="cta-eyebrow">Stop Fraud Now</p>
          <h2>Verify Every Payment.<br />Ship With Confidence.</h2>
          <p>
            Thousands of sellers and businesses scan screenshots with UPI Shield
            every day. Join them — free to start, no card needed.
          </p>

        </div>
      </section>

      {/* ════════ FOOTER ════════ */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <span className="logo-icon">🛡️</span>
            <span className="logo-text">
              UPI<span className="logo-accent">Shield</span>
            </span>
          </div>
          <p className="footer-copy">© 2026 UPI Shield. All rights reserved.</p>
          <div className="footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}