
import { useEffect, useMemo, useState } from "react";
import {
  Bot,
  Check,
  Clipboard,
  Copy,
  Hash,
  LoaderCircle,
  Menu,
  RefreshCw,
  Sparkles,
  Target,
  WandSparkles,
  Moon,
  Sun,
} from "lucide-react";

import { api, toGenerationPayload } from "./api";

const statuses = [
  "Understanding your brand...",
  "Analyzing brand personality...",
  "Identifying target audience...",
  "Crafting your tweets...",
  "Finalizing your content...",
];

const objectives = [
  "Engagement",
  "Product Promotion",
  "Brand Awareness",
  "Lead Generation",
  "Product Launch",
  "Community Building",
];

const tones = [
  "Let AI Decide",
  "Witty",
  "Premium",
  "Humorous",
  "Informative",
  "Bold",
  "Minimal",
  "Professional",
  "Friendly",
  "Inspirational",
];

const initialForm = {
  brand_name: "",
  industry: "",
  campaign_objective: "Engagement",
  product_description: "",
  preferred_tone: "Let AI Decide",
  target_audience: "",
  additional_instructions: "",
};

// Extract useful messages from FastAPI and Axios errors.
function getErrorMessage(err) {
  if (!err.response) {
    if (err.code === "ECONNABORTED") {
      return "The request timed out. Please try again.";
    }

    return "Cannot connect to the backend. Check that your FastAPI server is running.";
  }

  const data = err.response.data;
  const detail = data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item.loc)
          ? item.loc.filter((part) => part !== "body").join(".")
          : "";

        return location
          ? `${location}: ${item.msg || "Invalid value"}`
          : item.msg || "Validation error";
      })
      .join("\n");
  }

  if (detail && typeof detail === "object") {
    if (Array.isArray(detail.validation_errors)) {
      return detail.validation_errors
        .map((item) => `${item.loc?.join(".") || "Field"}: ${item.msg}`)
        .join("\n");
    }

    if (detail.message) {
      return detail.message;
    }

    return JSON.stringify(detail, null, 2);
  }

  if (typeof data?.message === "string") {
    return data.message;
  }

  return `Server error (${err.response.status}). Please check the backend logs.`;
}

function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [statusIndex, setStatusIndex] = useState(0);
  const [copied, setCopied] = useState("");
  const [editing, setEditing] = useState(null);
  const [regenerating, setRegenerating] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [theme, setTheme] = useState(
    () => localStorage.getItem("brandvoice-theme") || "dark"
  );

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("brandvoice-theme", theme);
  }, [theme]);

  const visibleStatus = useMemo(
    () => statuses[statusIndex % statuses.length],
    [statusIndex]
  );

  const update = (key, value) => {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  };

  const generate = async (endpoint = "/api/generate") => {
    if (loading) {
      return;
    }
    if (form.product_description.trim().length < 10) {
      setError(
        "Product / service description must be at least 10 characters."
      );
      return;
    }

    setLoading(true);
    setError("");
    setStatusIndex(0);

    const timer = setInterval(() => {
      setStatusIndex((value) => value + 1);
    }, 1400);

    try {
      const response = await api.post(
        endpoint,
        toGenerationPayload(form)
      );

      setResult(response.data);
    } catch (err) {
      console.error("GENERATION ERROR:", err.response?.data || err);
      setError(getErrorMessage(err));
    } finally {
      clearInterval(timer);
      setLoading(false);
    }
  };

  const copy = async (text, key) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(key);

      setTimeout(() => setCopied(""), 1600);
    } catch (err) {
      console.error("COPY ERROR:", err);
      setError("Unable to copy text. Please try again.");
    }
  };

  const editTweet = (id, text) => {
    setResult((current) => ({
      ...current,
      tweets: current.tweets.map((tweet) =>
        tweet.id === id
          ? {
              ...tweet,
              text,
              character_count: text.length,
            }
          : tweet
      ),
    }));
  };

  const regenerateTweet = async (tweet) => {
    if (loading || regenerating === tweet.id) {
      return;
    }
    setRegenerating(tweet.id);
    setError("");

    try {
      const response = await api.post(
        `/api/regenerate/${tweet.id}`,
        {
          brand_profile: result.brand_profile,
          campaign_objective: form.campaign_objective,
          product_description: form.product_description,
          additional_instructions: form.additional_instructions,
          category: tweet.category,
          tweet_id: tweet.id,
        }
      );

      setResult((current) => ({
        ...current,
        tweets: current.tweets.map((item) =>
          item.id === tweet.id ? response.data.tweet : item
        ),
      }));
    } catch (err) {
      console.error("REGENERATE ERROR:", err.response?.data || err);
      setError(getErrorMessage(err));
    } finally {
      setRegenerating(null);
    }
  };

  const field = (key, label, placeholder, type = "text") => (
    <label className="field">
      <span>{label}</span>

      {type === "textarea" ? (
        <textarea
          value={form[key]}
          onChange={(e) => update(key, e.target.value)}
          placeholder={placeholder}
        />
      ) : (
        <input
          value={form[key]}
          onChange={(e) => update(key, e.target.value)}
          placeholder={placeholder}
        />
      )}
    </label>
  );

  return (
    <div className="app">
      <nav>
        <a className="logo" href="#">
          <span className="logo-mark">
            <Sparkles size={16} />
          </span>
          BrandVoice <b>AI</b>
        </a>

        <button
          className="menu"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          <Menu />
        </button>

        <div className={`nav-links ${mobileOpen ? "open" : ""}`}>
          <a href="#dashboard">Dashboard</a>
          <a href="#about">About</a>
          <span className="status-dot">● AI ready</span>
          <button
            className="theme-toggle"
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            onClick={() => setTheme((current) => current === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
            <span>{theme === "dark" ? "Light" : "Dark"}</span>
          </button>
        </div>
      </nav>

      <main id="dashboard">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span>✦</span> INTELLIGENT CONTENT STUDIO
            </div>

            <h1>
              Your Brand.
              <br />
              <em>Your Voice.</em>
              <br />
              10 Tweets. Instantly.
            </h1>

            <p>
              Transform your brand identity into engaging social content
              with AI-powered brand intelligence.
            </p>

            <div className="hero-actions">
              <a className="primary" href="#generator">
                <WandSparkles size={17} />
                Generate tweets
              </a>

              <span className="hero-note">
                <span className="avatars">✦</span>
                Crafted for standout brands
              </span>
            </div>
          </div>

          <div className="orb-wrap">
            <div className="orb">
              <Bot size={58} />
              <span className="orbit orbit-one"></span>
              <span className="orbit orbit-two"></span>
            </div>

            <div className="floating-card card-top">
              <Hash size={15} /> 10 fresh ideas
            </div>

            <div className="floating-card card-bottom">
              <Check size={15} /> On-brand, every time
            </div>
          </div>
        </section>

        <section className="workspace" id="generator">
          <div className="section-heading">
            <div>
              <div className="eyebrow">01 / BRAND INTELLIGENCE</div>
              <h2>Tell us about your brand</h2>
              <p>
                The more context you share, the more distinct your voice
                becomes.
              </p>
            </div>

            <div className="step-pill">
              STEP 1 <span>→</span> STEP 2
            </div>
          </div>

          <div className="form-grid">
            {field("brand_name", "Brand name", "e.g. Northstar Coffee")}

            {field("industry", "Industry / category", "e.g. Specialty coffee")}

            <label className="field">
              <span>
                Campaign objective <i>Required</i>
              </span>

              <select
                value={form.campaign_objective}
                onChange={(e) =>
                  update("campaign_objective", e.target.value)
                }
              >
                {objectives.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Preferred tone</span>

              <select
                value={form.preferred_tone}
                onChange={(e) =>
                  update("preferred_tone", e.target.value)
                }
              >
                {tones.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>

            <div className="wide">
              {field(
                "product_description",
                "Product / service description",
                "What do you offer? What makes it different?",
                "textarea"
              )}
            </div>

            {field(
              "target_audience",
              "Target audience",
              "Who are you speaking to?"
            )}

            <div className="wide">
              {field(
                "additional_instructions",
                "Additional instructions",
                "Any themes, words, or ideas to include?",
                "textarea"
              )}
            </div>
          </div>

          {error && <div className="error">{error}</div>}

          <button
            className="generate"
            disabled={loading}
            onClick={() => generate()}
          >
            {loading ? (
              <>
                <LoaderCircle className="spin" size={18} />
                {visibleStatus}
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Generate 10 tweets
                <span>→</span>
              </>
            )}
          </button>
        </section>

        {loading && (
          <div className="loading-panel">
            <div className="loader-ring">
              <Sparkles />
            </div>

            <h3>{visibleStatus}</h3>
            <p>Your brand intelligence is being assembled.</p>

            <div className="progress">
              <span />
            </div>
          </div>
        )}

        {result && !loading && (
          <section className="results">
            <div className="section-heading">
              <div>
                <div className="eyebrow">02 / YOUR CONTENT</div>
                <h2>Content with character.</h2>
                <p>
                  Ten distinct ideas, shaped by your brand voice.
                </p>
              </div>

              <button
                className="secondary"
                onClick={() => generate("/api/regenerate-all")}
              >
                <RefreshCw size={16} />
                Regenerate all
              </button>
            </div>

            <div className="profile-card">
              <div className="profile-icon">
                <Target />
              </div>

              <div className="profile-main">
                <div className="eyebrow">BRAND VOICE PROFILE</div>

                <h3>{result.brand_profile.personality}</h3>

                <p>
                  {result.brand_profile.voice_summary.map((item) => (
                    <span className="summary" key={item}>
                      ✦ {item}
                    </span>
                  ))}
                </p>
              </div>

              <div className="profile-meta">
                <span>
                  <b>TONE</b>
                  {result.brand_profile.tone}
                </span>

                <span>
                  <b>AUDIENCE</b>
                  {result.brand_profile.target_audience}
                </span>

                <span>
                  <b>STYLE</b>
                  {result.brand_profile.writing_style}
                </span>
              </div>
            </div>

            <div className="tweets-header">
              <h3>
                Generated tweets <small>10 / 10</small>
              </h3>

              <button
                className="copy-all"
                onClick={() =>
                  copy(
                    result.tweets
                      .map((tweet) => tweet.text)
                      .join("\n\n"),
                    "all"
                  )
                }
              >
                {copied === "all" ? (
                  <Check size={15} />
                ) : (
                  <Copy size={15} />
                )}

                {copied === "all" ? "Copied" : "Copy all"}
              </button>
            </div>

            <div className="tweet-grid">
              {result.tweets.map((tweet) => (
                <article className="tweet-card" key={tweet.id}>
                  <div className="tweet-top">
                    <span className="number">
                      {String(tweet.id).padStart(2, "0")}
                    </span>

                    <span className="category">{tweet.category}</span>

                    <button
                      className="icon-btn"
                      onClick={() => copy(tweet.text, tweet.id)}
                    >
                      {copied === tweet.id ? (
                        <Check size={15} />
                      ) : (
                        <Clipboard size={15} />
                      )}
                    </button>
                  </div>

                  {editing === tweet.id ? (
                    <textarea
                      className="tweet-edit"
                      autoFocus
                      value={tweet.text}
                      onChange={(e) =>
                        editTweet(tweet.id, e.target.value)
                      }
                      onBlur={() => setEditing(null)}
                      maxLength={280}
                    />
                  ) : (
                    <p className="tweet-text">{tweet.text}</p>
                  )}

                  <div className="tweet-bottom">
                    <span
                      className={
                        tweet.character_count > 260 ? "warning" : ""
                      }
                    >
                      {tweet.character_count} / 280
                    </span>

                    <button
                      onClick={() =>
                        setEditing(
                          editing === tweet.id ? null : tweet.id
                        )
                      }
                    >
                      {editing === tweet.id ? "Done" : "Edit"}
                    </button>

                    <button onClick={() => copy(tweet.text, tweet.id)}>
                      {copied === tweet.id ? "Copied" : "Copy"}
                    </button>

                    <button
                      disabled={regenerating === tweet.id}
                      onClick={() => regenerateTweet(tweet)}
                    >
                      {regenerating === tweet.id ? (
                        <LoaderCircle className="spin" size={12} />
                      ) : (
                        <RefreshCw size={12} />
                      )}{" "}
                      {regenerating === tweet.id ? "Working" : "New"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer id="about">
        <span className="logo">
          <span className="logo-mark">
            <Sparkles size={14} />
          </span>
          BrandVoice <b>AI</b>
        </span>

        <span>Built for brands with something to say.</span>
      </footer>
    </div>
  );
}

export default App;
