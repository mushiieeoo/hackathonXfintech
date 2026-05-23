import { useState, useEffect, useCallback } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const API = "http://localhost:8000/api";

const COLORS = {
  ETF: { fill: "#03e29d", light: "#EEF0FF" },
  Stock: { fill: "#fa58a7", light: "#FFF0F0" },
  Crypto: { fill: "#3f22ec", light: "#FFFBEA" },
  "Non-Volatile": { fill: "#efca62", light: "#EDFBEF" },
};

const TREE_STAGES = [
  { emoji: "🌱", label: "Seed", desc: "Just planted" },
  { emoji: "🌿", label: "Sprout", desc: "30% reached!" },
  { emoji: "🌳", label: "Sapling", desc: "50% reached!" },
  { emoji: "🌲", label: "Young Tree", desc: "70% reached!" },
  { emoji: "⛰️", label: "Full Grown", desc: "Goal achieved!" },
];

//Fetch hook — handles loading, errors, and refetching
function useApi(endpoint, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`${API}${endpoint}`);
      if (res.ok) {
        setData(await res.json());
      } else if (res.status !== 404) {
        // 404 just means "not set yet" which is fine — anything else is a real error
        const err = await res.json().catch(() => ({}));
        setError(err.detail || `Error ${res.status}`);
      }
    } catch (e) {
      setError("Can't reach the backend — is uvicorn running?");
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => { fetch_(); }, deps);
  return { data, loading, error, refetch: fetch_ };
}

//POST helper — always throws on failure so callers know what went wrong
async function post(endpoint, body) {
  const res = await fetch(`${API}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(json.detail || `Server error ${res.status}`);
  }
  return json;
}

//converts form string values to floats for the given field names
function convertNumbers(form, fields) {
  const out = { ...form };
  fields.forEach(f => {
    if (out[f] !== undefined && out[f] !== "") {
      out[f] = parseFloat(out[f]);
    }
  });
  return out;
}

//reusable UI bits
function SectionHeader({ number, title, subtitle }) {
  return (
    <div style={{ marginBottom: 28, textAlign:"center"}}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12 }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "#fff", fontWeight: 800, fontSize: 15, flexShrink: 0,
        }}>{number}</div>
        <h2 style={{ margin: 0, fontSize: 34, fontWeight: 800, color: "#3f22ec" }}>{title}</h2>
      </div>
      {subtitle && <p style={{ margin: "8px 0 0 48px", color: "#ffff", fontSize: 14 }}>{subtitle}</p>}
    </div>
  );
}

function Card({ children, style = {} }) {
  return (
    <div style={{
      background: "#fff", borderRadius: 20, padding: "28px 28px",
      boxShadow: "0 4px 24px rgba(0,0,0,0.07)", border: "1.5px solid #f0f0f0",
      ...style,
    }}>{children}</div>
  );
}

function Modal({ open, onClose, title, children }) {
  if (!open) return null;
  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(26,26,46,0.55)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 20, padding: 32, minWidth: 360,
        maxWidth: 480, width: "90%", boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: "#1a1a2e" }}>{title}</h3>
          <button onClick={onClose} style={{
            background: "#f5f5f5", border: "none", borderRadius: "50%",
            width: 32, height: 32, cursor: "pointer", fontSize: 18, color: "#666",
          }}>×</button>
        </div>
        {children}
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = "text", placeholder, min, step }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#555", marginBottom: 6 }}>{label}</label>
      <input
        type={type} value={value} onChange={e => onChange(e.target.value)}
        placeholder={placeholder} min={min} step={step}
        style={{
          width: "100%", boxSizing: "border-box", padding: "10px 14px",
          borderRadius: 10, border: "1.5px solid #e5e5e5", fontSize: 14, outline: "none",
        }}
        onFocus={e => e.target.style.border = "1.5px solid #6C63FF"}
        onBlur={e => e.target.style.border = "1.5px solid #e5e5e5"}
      />
    </div>
  );
}

function PrimaryButton({ children, onClick, color = "#6C63FF", disabled }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      background: color, color: "#fff", border: "none", borderRadius: 12,
      padding: "12px 24px", fontWeight: 700, fontSize: 14,
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.6 : 1, width: "100%",
    }}>{children}</button>
  );
}

// Green success or red error banner
function Banner({ msg, isError }) {
  if (!msg) return null;
  return (
    <div style={{
      background: isError ? "#fff0f0" : "#edfbef",
      border: `1px solid ${isError ? "#FF6B6B" : "#6BCB77"}`,
      color: isError ? "#c0392b" : "#2a6b30",
      borderRadius: 10, padding: "10px 16px", marginBottom: 16, fontSize: 14, fontWeight: 600,
    }}>{msg}</div>
  );
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: "#1a1a2e", color: "#fff", borderRadius: 12,
      padding: "10px 16px", fontSize: 13,
    }}>
      <div style={{ fontWeight: 700 }}>{d.label}</div>
      <div>RM {d.value_RM?.toLocaleString("en-MY", { minimumFractionDigits: 2 })}</div>
      <div style={{ color: "#aaa" }}>{d.ratio_pct?.toFixed(1)}% of portfolio</div>
    </div>
  );
}

// Feature 1: Portfolio Overview
function PortfolioSection({ onRefresh }) {
  const { data: summary, loading, error: summaryError, refetch } = useApi("/portfolio/summary", []);
  const { data: planData, refetch: refetchPlan } = useApi("/portfolio/monthly-plan", []);

  const [addModal, setAddModal] = useState(false);
  const [planModal, setPlanModal] = useState(false);
  const [assetType, setAssetType] = useState("crypto");
  const [form, setForm] = useState({});
  const [planAmount, setPlanAmount] = useState("");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);

  // Auto-refresh prices every minute
  useEffect(() => {
    const t = setInterval(refetch, 60000);
    return () => clearInterval(t);
  }, []);

  const assetFields = {
    crypto: [
      { key: "crypt_name", label: "Coin symbol (e.g. BTC, ETH)", ph: "BTC" },
      { key: "coin_amount", label: "How many coins", ph: "0.5", type: "number", step: "any" },
    ],
    etf: [
      { key: "etf_name", label: "ETF ticker (e.g. VWRA, SPY)", ph: "VWRA" },
      { key: "share_amount", label: "Number of shares", ph: "10", type: "number", step: "any" },
    ],
    stock: [
      { key: "stock_name", label: "Stock ticker (Bursa: 1155.KL, US: NVDA)", ph: "1155.KL" },
      { key: "share_amount", label: "Number of shares", ph: "5", type: "number", step: "any" },
    ],
    bank: [
      { key: "bank_name", label: "Bank name", ph: "Maybank" },
      { key: "amount_RM", label: "Balance (RM)", ph: "5000", type: "number", step: "any" },
    ],
    nvi: [
      { key: "nvi_name", label: "Asset name (e.g. ASB, Gold)", ph: "ASB" },
      { key: "amount_RM", label: "Amount (RM)", ph: "10000", type: "number", step: "any" },
    ],
  };

  async function handleAddAsset() {
    setSaving(true);
    try {
      // Number fields need to be floats, not strings
      const payload = convertNumbers(form, ["coin_amount", "share_amount", "amount_RM"]);
      await post(`/assets/${assetType}`, payload);
      setMsg("Asset added!");
      setIsError(false);
      setAddModal(false);
      setForm({});
      refetch();
      onRefresh?.();
    } catch (e) {
      setMsg(`Failed: ${e.message}`);
      setIsError(true);
    }
    setSaving(false);
    setTimeout(() => setMsg(""), 4000);
  }

  async function handleSavePlan() {
    setSaving(true);
    try {
      await post("/portfolio/monthly-plan", { monthly_plan_RM: parseFloat(planAmount) });
      setMsg("Monthly plan saved!");
      setIsError(false);
      setPlanModal(false);
      refetchPlan();
    } catch (e) {
      setMsg(`Failed: ${e.message}`);
      setIsError(true);
    }
    setSaving(false);
    setTimeout(() => setMsg(""), 4000);
  }

  const pieData = (summary?.breakdown || []).filter(d => d.value_RM > 0);

  return (
    <section style={{ marginBottom: 64 }}>
      <SectionHeader  title="Portfolio Overview"
        subtitle="Live pie chart of your investments — capital refresh every minute!" />

      <Banner msg={msg} isError={isError} />
      {summaryError && <Banner msg={`Backend error: ${summaryError}`} isError />}

      <Card>
        <div style={{ textAlign: "center", marginBottom: 8 }}>
          <div style={{ fontSize: 13, color: "#888", fontWeight: 600, letterSpacing: 1, textTransform: "uppercase" }}>
            Total Portfolio Value
          </div>
          <div style={{ fontSize: 42, fontWeight: 900, color: "#1a1a2e", letterSpacing: -1 }}>
            {loading ? "Loading…" : `RM ${(summary?.total_value_RM ?? 0).toLocaleString("en-MY", { minimumFractionDigits: 2 })}`}
          </div>
          <div style={{ fontSize: 12, color: "#aaa", marginTop: 2 }}>
            Last updated: {summary?.last_updated ? new Date(summary.last_updated).toLocaleTimeString() : "—"}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 32, flexWrap: "wrap" }}>
          <div style={{ flex: "0 0 280px", height: 280 }}>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={120}
                    dataKey="value_RM" nameKey="label" paddingAngle={3}>
                    {pieData.map(entry => (
                      <Cell key={entry.label} fill={COLORS[entry.label]?.fill || "#ccc"} stroke="#fff" strokeWidth={3} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              //for no data yet
              <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#bbb", gap: 8 }}>
                <div style={{ fontSize: 48 }}>📊</div>
                <div style={{ fontSize: 14 }}>No data yet</div>
                <div style={{ fontSize: 12 }}>Add an investment to get started</div>
              </div>
            )}
          </div>

          <div style={{ flex: 1, minWidth: 180 }}>
            {(summary?.breakdown || []).map(item => (
              <div key={item.label} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "10px 0", borderBottom: "1px solid #f5f5f5",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 14, height: 14, borderRadius: 4, background: COLORS[item.label]?.fill || "#ccc" }} />
                  <span style={{ fontWeight: 600, color: "#333", fontSize: 14 }}>{item.label}</span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontWeight: 700, color: "#1a1a2e", fontSize: 14 }}>
                    RM {item.value_RM?.toLocaleString("en-MY", { minimumFractionDigits: 2 })}
                  </div>
                  <div style={{ fontSize: 12, color: "#888" }}>{item.ratio_pct?.toFixed(1)}%</div>
                </div>
              </div>
            ))}

            {planData?.monthly_plan_RM != null && (
              <div style={{ marginTop: 16, padding: "10px 14px", background: "#f5f3ff", borderRadius: 12, border: "1.5px solid #d4d0ff" }}>
                <div style={{ fontSize: 12, color: "#6C63FF", fontWeight: 600 }}>Monthly Plan</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: "#6C63FF" }}>
                  RM {planData.monthly_plan_RM?.toLocaleString("en-MY", { minimumFractionDigits: 2 })}
                </div>
              </div>
            )}
          </div>
        </div>

        <div style={{ display: "flex", gap: 12, marginTop: 24, flexWrap: "wrap" }}>
          <button onClick={() => setAddModal(true)} style={{
            flex: 1, minWidth: 160, background: "linear-gradient(135deg, #6C63FF, #8B84FF)",
            color: "#fff", border: "none", borderRadius: 12, padding: "12px 20px",
            fontWeight: 700, fontSize: 14, cursor: "pointer",
          }}>+ Add Investment</button>
          <button onClick={() => { setPlanAmount(planData?.monthly_plan_RM || ""); setPlanModal(true); }} style={{
            flex: 1, minWidth: 160, background: "#f5f3ff", color: "#6C63FF",
            border: "1.5px solid #d4d0ff", borderRadius: 12, padding: "12px 20px",
            fontWeight: 700, fontSize: 14, cursor: "pointer",
          }}>✏️ Set Monthly Plan</button>
          <button onClick={refetch} style={{
            background: "#f5f5f5", color: "#666", border: "none", borderRadius: 12,
            padding: "12px 20px", fontWeight: 700, fontSize: 14, cursor: "pointer",
          }}>🔄 Refresh</button>
        </div>
      </Card>

      <Modal open={addModal} onClose={() => setAddModal(false)} title="Add Investment">
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 13, fontWeight: 600, color: "#555", display: "block", marginBottom: 6 }}>Asset Type</label>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {["crypto", "etf", "stock", "bank", "nvi"].map(t => (
              <button key={t} onClick={() => { setAssetType(t); setForm({}); }} style={{
                padding: "6px 14px", borderRadius: 20, border: "1.5px solid",
                borderColor: assetType === t ? "#6C63FF" : "#e5e5e5",
                background: assetType === t ? "#f5f3ff" : "#fff",
                color: assetType === t ? "#6C63FF" : "#666",
                fontWeight: 600, fontSize: 13, cursor: "pointer", textTransform: "uppercase",
              }}>{t}</button>
            ))}
          </div>
        </div>
        {assetFields[assetType]?.map(f => (
          <Field key={f.key} label={f.label} placeholder={f.ph} type={f.type || "text"}
            step={f.step} value={form[f.key] || ""}
            onChange={v => setForm(prev => ({ ...prev, [f.key]: v }))} />
        ))}
        <PrimaryButton onClick={handleAddAsset} disabled={saving}>
          {saving ? "Saving…" : "Add Asset"}
        </PrimaryButton>
      </Modal>

      <Modal open={planModal} onClose={() => setPlanModal(false)} title="Set Monthly Investment Plan">
        <Field label="Monthly amount (RM)" type="number" step="0.01" min="0"
          value={planAmount} onChange={setPlanAmount} placeholder="e.g. 2000" />
        <PrimaryButton onClick={handleSavePlan} disabled={saving}>
          {saving ? "Saving…" : "Save Plan"}
        </PrimaryButton>
      </Modal>
    </section>
  );
}

// ── Feature 2: Goal Milestone Tree ────────────────────────────────────────────
function GoalSection({ triggerRefresh }) {
  const year = new Date().getFullYear();
  const { data: goal, loading, refetch } = useApi(`/goals/${year}`, [triggerRefresh]);
  const [goalModal, setGoalModal] = useState(false);
  const [targetAmount, setTargetAmount] = useState("");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);

  async function handleSetGoal() {
    if (!targetAmount || parseFloat(targetAmount) <= 0) {
      setMsg("Please enter a valid target amount");
      setIsError(true);
      return;
    }
    setSaving(true);
    try {
      // No trailing slash — FastAPI is strict about this
      await post("/goals", { year, target_RM: parseFloat(targetAmount) });
      setMsg("Goal saved! 🌱");
      setIsError(false);
      setGoalModal(false);
      refetch();
    } catch (e) {
      setMsg(`Failed: ${e.message}`);
      setIsError(true);
    }
    setSaving(false);
    setTimeout(() => setMsg(""), 4000);
  }

  const stage = goal?.tree_stage ?? 0;
  const progress = goal?.progress_pct ?? 0;
  const milestones = [30, 50, 70, 100];

  return (
    <section style={{ marginBottom: 64 }}>
      <SectionHeader title="Goal Milestone Tree"
        subtitle={`Track your ${year} investment goal — watch your tree grow as you hit milestones`} />

      <Banner msg={msg} isError={isError} />

      <Card>
        {loading ? (
          <div style={{ textAlign: "center", padding: 32, color: "#aaa" }}>Loading…</div>
        ) : !goal ? (
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🎯</div>
            <p style={{ color: "#888", marginBottom: 20 }}>No goal set for {year} yet.</p>
            <button onClick={() => setGoalModal(true)} style={{
              background: "linear-gradient(135deg, #6BCB77, #4CAF50)",
              color: "#fff", border: "none", borderRadius: 12,
              padding: "12px 28px", fontWeight: 700, fontSize: 14, cursor: "pointer",
            }}>🌱 Set Your {year} Goal</button>
          </div>
        ) : (
          <>
            <div style={{ textAlign: "center", padding: "16px 0 24px" }}>
              <div style={{ fontSize: 88, lineHeight: 1 }}>{TREE_STAGES[stage]?.emoji}</div>
              <div style={{ marginTop: 12, fontWeight: 800, fontSize: 20, color: "#1a1a2e" }}>{TREE_STAGES[stage]?.label}</div>
              <div style={{ color: "#888", fontSize: 14 }}>{TREE_STAGES[stage]?.desc}</div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontSize: 13, color: "#888", fontWeight: 600 }}>Progress</span>
                <span style={{ fontSize: 14, fontWeight: 800, color: "#1a1a2e" }}>{progress.toFixed(1)}%</span>
              </div>
              <div style={{ background: "#f0f0f0", borderRadius: 99, height: 16, position: "relative", overflow: "hidden" }}>
                <div style={{
                  height: "100%", borderRadius: 99,
                  background: "linear-gradient(90deg, #6BCB77, #4CAF50)",
                  width: `${Math.min(progress, 100)}%`, transition: "width 0.8s ease",
                }} />
                {milestones.map(m => (
                  <div key={m} style={{
                    position: "absolute", top: 0, bottom: 0, left: `${m}%`, width: 2,
                    background: progress >= m ? "rgba(255,255,255,0.6)" : "#ccc",
                    transform: "translateX(-50%)",
                  }} />
                ))}
              </div>
              <div style={{ position: "relative", height: 20, marginTop: 4 }}>
                {milestones.map(m => (
                  <div key={m} style={{
                    position: "absolute", left: `${m}%`, transform: "translateX(-50%)",
                    fontSize: 11, fontWeight: 700, color: progress >= m ? "#4CAF50" : "#bbb",
                  }}>{m}%</div>
                ))}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 24 }}>
              <div style={{ background: "#f5f3ff", borderRadius: 12, padding: "14px 16px" }}>
                <div style={{ fontSize: 12, color: "#6C63FF", fontWeight: 600, marginBottom: 4 }}>Current Value</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: "#1a1a2e" }}>
                  RM {goal?.current_value_RM?.toLocaleString("en-MY", { minimumFractionDigits: 2 }) || "—"}
                </div>
              </div>
              <div style={{ background: "#edfbef", borderRadius: 12, padding: "14px 16px" }}>
                <div style={{ fontSize: 12, color: "#4CAF50", fontWeight: 600, marginBottom: 4 }}>Target {year}</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: "#1a1a2e" }}>
                  RM {goal?.target_RM?.toLocaleString("en-MY", { minimumFractionDigits: 2 }) || "—"}
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, marginTop: 20, flexWrap: "wrap" }}>
              {milestones.map(m => (
                <div key={m} style={{
                  padding: "6px 14px", borderRadius: 20,
                  background: goal?.milestones_reached?.includes(m) ? "#4CAF50" : "#f0f0f0",
                  color: goal?.milestones_reached?.includes(m) ? "#fff" : "#bbb",
                  fontSize: 13, fontWeight: 700,
                }}>
                  {goal?.milestones_reached?.includes(m) ? "✓ " : ""}{m}%
                </div>
              ))}
            </div>

            <button onClick={() => { setTargetAmount(goal?.target_RM || ""); setGoalModal(true); }}
              style={{
                marginTop: 20, background: "transparent", color: "#6C63FF",
                border: "1.5px solid #d4d0ff", borderRadius: 12,
                padding: "10px 20px", fontWeight: 600, fontSize: 14, cursor: "pointer",
              }}>✏️ Update Goal</button>
          </>
        )}
      </Card>

      <Modal open={goalModal} onClose={() => setGoalModal(false)} title={`Set ${year} Investment Goal`}>
        <Field label={`Target amount for ${year} (RM)`} type="number" step="100" min="1"
          value={targetAmount} onChange={setTargetAmount} placeholder="e.g. 100000" />
        <PrimaryButton onClick={handleSetGoal} disabled={saving} color="#4CAF50">
          {saving ? "Saving…" : "🌱 Set Goal"}
        </PrimaryButton>
      </Modal>
    </section>
  );
}

// Feature 3: Strategy Rebalancing
function RebalancingSection() {
const [advice, setAdvice] = useState(null);
const [adviceLoading, setAdviceLoading] = useState(false);
const [adviceError, setAdviceError] = useState(null);

async function fetchAdvice() {
    setAdviceLoading(true);
    setAdviceError(null);
    try {
        const res = await fetch(`${API}/rebalancing/advice`);
        if (res.ok) setAdvice(await res.json());
        else {
            const err = await res.json().catch(() => ({}));
            setAdviceError(err.detail || "Failed to load advice");
        }
    } catch (e) {
        setAdviceError("Can't reach backend");
    }
    setAdviceLoading(false);
}
  const { data: strategy } = useApi("/rebalancing/strategy", []);

  const [stratModal, setStratModal] = useState(false);
  const [strat, setStrat] = useState({ etf_pct: "", stock_pct: "", crypto_pct: "", nvi_pct: "" });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);

  const total = ["etf_pct", "stock_pct", "crypto_pct", "nvi_pct"]
    .reduce((s, k) => s + (parseFloat(strat[k]) || 0), 0);

  async function handleSaveStrategy() {
    if (Math.abs(total - 100) > 0.01) {
      setMsg("Percentages must add up to 100%");
      setIsError(true);
      return;
    }
    setSaving(true);
    try {
      await post("/rebalancing/strategy", {
        etf_pct: parseFloat(strat.etf_pct),
        stock_pct: parseFloat(strat.stock_pct),
        crypto_pct: parseFloat(strat.crypto_pct),
        nvi_pct: parseFloat(strat.nvi_pct),
      });
      setMsg("Strategy saved!");
      setIsError(false);
      setStratModal(false);
      setTimeout(refetchAdvice, 500);
    } catch (e) {
      setMsg(`Failed: ${e.message}`);
      setIsError(true);
    }
    setSaving(false);
    setTimeout(() => setMsg(""), 4000);
  }

  async function handleManualSnapshot() {
    try {
      const res = await fetch(`${API}/rebalancing/snapshot/manual`, { method: "POST" });
      if (!res.ok) throw new Error("Snapshot failed");
      setMsg("Snapshot taken!");
      setIsError(false);
      setTimeout(() => { refetchAdvice(); setMsg(""); }, 1000);
    } catch (e) {
      setMsg(`Failed: ${e.message}`);
      setIsError(true);
    }
  }

  const driftLabels = { etf: "ETF", stock: "Stock", crypto: "Crypto", nvi: "Non-Volatile" };
  const allocationKeys = ["ETF", "Stock", "Crypto", "Non-Volatile"];

  return (
    <section style={{ marginBottom: 64 }}>
      <SectionHeader title="Strategy Rebalancing"
        subtitle="AI-powered advice to keep your portfolio aligned with your target strategy" />

      <Banner msg={msg} isError={isError} />

      {/* Show a helpful message when no strategy is set yet */}
      {adviceError && (
        <Banner
          msg={adviceError.includes("strategy") ? "Set your investment strategy first to see rebalancing advice." : `Error: ${adviceError}`}
          isError
        />
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <Card style={{ borderTop: "4px solid #6C63FF" }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "#6C63FF", marginBottom: 16, letterSpacing: 0.5, textTransform: "uppercase" }}>
            🎯 Target Strategy
          </div>
          {strategy ? (
            <>
              {[["ETF", strategy.etf_pct], ["Stock", strategy.stock_pct], ["Crypto", strategy.crypto_pct], ["Non-Volatile", strategy.nvi_pct]].map(([label, pct]) => (
                <div key={label} style={{ marginBottom: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 13, color: "#555", fontWeight: 600 }}>{label}</span>
                    <span style={{ fontSize: 13, fontWeight: 800, color: "#1a1a2e" }}>{pct}%</span>
                  </div>
                  <div style={{ height: 6, background: "#f0f0f0", borderRadius: 99 }}>
                    <div style={{ height: "100%", width: `${pct}%`, borderRadius: 99, background: COLORS[label]?.fill || "#6C63FF" }} />
                  </div>
                </div>
              ))}
              <button onClick={() => { setStrat({ etf_pct: strategy.etf_pct, stock_pct: strategy.stock_pct, crypto_pct: strategy.crypto_pct, nvi_pct: strategy.nvi_pct }); setStratModal(true); }}
                style={{ marginTop: 8, background: "transparent", color: "#6C63FF", border: "1.5px solid #d4d0ff", borderRadius: 10, padding: "8px 16px", fontWeight: 600, fontSize: 13, cursor: "pointer" }}>
                ✏️ Edit Strategy
              </button>
            </>
          ) : (
            <div style={{ textAlign: "center", padding: "16px 0" }}>
              <p style={{ color: "#aaa", fontSize: 14, marginBottom: 16 }}>No strategy set yet</p>
              <button onClick={() => setStratModal(true)} style={{
                background: "linear-gradient(135deg, #6C63FF, #8B84FF)", color: "#fff",
                border: "none", borderRadius: 10, padding: "10px 20px", fontWeight: 700, fontSize: 13, cursor: "pointer",
              }}>Set Strategy</button>
            </div>
          )}
        </Card>

        <Card style={{ borderTop: "4px solid #FF6B6B" }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "#FF6B6B", marginBottom: 16, letterSpacing: 0.5, textTransform: "uppercase" }}>
            📊 Current Ratio (Snapshot)
          </div>
          {advice?.current_snapshot ? (
            <>
              {[["ETF", advice.current_snapshot.etf_pct], ["Stock", advice.current_snapshot.stock_pct], ["Crypto", advice.current_snapshot.crypto_pct], ["Non-Volatile", advice.current_snapshot.nvi_pct]].map(([label, pct]) => (
                <div key={label} style={{ marginBottom: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 13, color: "#555", fontWeight: 600 }}>{label}</span>
                    <span style={{ fontSize: 13, fontWeight: 800, color: "#1a1a2e" }}>{pct?.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: 6, background: "#f0f0f0", borderRadius: 99 }}>
                    <div style={{ height: "100%", width: `${Math.min(pct, 100)}%`, borderRadius: 99, background: COLORS[label]?.fill || "#FF6B6B" }} />
                  </div>
                </div>
              ))}
              <button onClick={handleManualSnapshot}
                style={{ marginTop: 8, background: "transparent", color: "#FF6B6B", border: "1.5px solid #ffd0d0", borderRadius: 10, padding: "8px 16px", fontWeight: 600, fontSize: 13, cursor: "pointer" }}>
                📸 Take Snapshot Now
              </button>
            </>
          ) : (
            <div style={{ textAlign: "center", padding: "16px 0" }}>
              <p style={{ color: "#aaa", fontSize: 14, marginBottom: 16 }}>No snapshot yet</p>
              <button onClick={handleManualSnapshot} style={{
                background: "#fff5f5", color: "#FF6B6B", border: "1.5px solid #ffd0d0",
                borderRadius: 10, padding: "10px 20px", fontWeight: 700, fontSize: 13, cursor: "pointer",
              }}>📸 Take First Snapshot</button>
            </div>
          )}
        </Card>
      </div>

      {advice?.drift && (
        <Card style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "#888", marginBottom: 16, letterSpacing: 0.5, textTransform: "uppercase" }}>
            Drift from Target
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: 12 }}>
            {Object.entries(advice.drift).map(([key, val]) => (
              <div key={key} style={{
                textAlign: "center", padding: "12px 8px", borderRadius: 12,
                background: val > 0 ? "#fff5f5" : val < 0 ? "#edfbef" : "#f9f9f9",
                border: `1.5px solid ${val > 0 ? "#ffcccc" : val < 0 ? "#c8f0ce" : "#eee"}`,
              }}>
                <div style={{ fontSize: 11, color: "#888", fontWeight: 600, marginBottom: 4 }}>{driftLabels[key]}</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: val > 0 ? "#FF6B6B" : val < 0 ? "#4CAF50" : "#888" }}>
                  {val > 0 ? "+" : ""}{val.toFixed(1)}%
                </div>
                <div style={{ fontSize: 10, color: "#aaa" }}>{val > 0 ? "over" : val < 0 ? "under" : "balanced"}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {advice?.ai_advice && (
        <Card style={{ background: "linear-gradient(135deg, #1a1a2e, #2d2b55)", border: "none" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <div style={{
              width: 36, height: 36, borderRadius: "50%",
              background: "linear-gradient(135deg, #6C63FF, #FF6B6B)",
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18,
            }}>✨</div>
            <div>
              <div style={{ color: "#fff", fontWeight: 700, fontSize: 15 }}>AI Rebalancing Advice</div>
              <div style={{ color: "#8b8aaa", fontSize: 12 }}>Powered by Gemini</div>
            </div>
          </div>
        
          {advice.allocations && (
            <>
              <div style={{ fontSize: 12, color: "#8b8aaa", fontWeight: 600, marginBottom: 10, letterSpacing: 0.5, textTransform: "uppercase" }}>
                Suggested allocation this month (RM {advice.monthly_plan_RM?.toFixed(0)})
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))", gap: 10 }}>
                {allocationKeys.map(k => (
                  <div key={k} style={{
                    background: "rgba(255,255,255,0.08)", borderRadius: 12,
                    padding: "12px 10px", textAlign: "center", border: "1px solid rgba(255,255,255,0.1)",
                  }}>
                    <div style={{ width: 10, height: 10, borderRadius: 3, background: COLORS[k]?.fill, margin: "0 auto 6px" }} />
                    <div style={{ fontSize: 11, color: "#8b8aaa", fontWeight: 600 }}>{k}</div>
                    <div style={{ fontSize: 16, fontWeight: 800, color: "#fff", marginTop: 2 }}>
                      RM {advice.allocations[k]?.toLocaleString("en-MY", { minimumFractionDigits: 0 }) || "0"}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </Card>
      )}

      {adviceLoading && <div style={{ textAlign: "center", padding: 32, color: "#888" }}>Loading rebalancing data…</div>}
      <button onClick={fetchAdvice} style={{
        background: "linear-gradient(135deg, #6C63FF, #8B84FF)",
        color: "#fff", border: "none", borderRadius: 12,
        padding: "12px 24px", fontWeight: 700, fontSize: 14,
        cursor: "pointer", marginBottom: 16, width: "100%"
      }}>
          Get AI Advice
      </button>

      <Modal open={stratModal} onClose={() => setStratModal(false)} title="Set Investment Strategy">
        <p style={{ color: "#888", fontSize: 13, marginTop: 0 }}>Percentages must add up to 100%</p>
        {[["etf_pct", "ETF %"], ["stock_pct", "Stock %"], ["crypto_pct", "Crypto %"], ["nvi_pct", "Non-Volatile %"]].map(([key, label]) => (
          <Field key={key} label={label} type="number" step="1" min="0" max="100"
            value={strat[key]} onChange={v => setStrat(prev => ({ ...prev, [key]: v }))} />
        ))}
        <div style={{
          textAlign: "right", fontSize: 13, fontWeight: 700, marginBottom: 16,
          color: Math.abs(total - 100) < 0.01 ? "#4CAF50" : total > 100 ? "#FF6B6B" : "#888",
        }}>Total: {total.toFixed(1)}% {Math.abs(total - 100) < 0.01 ? "✓" : "(must be 100%)"}</div>
        <PrimaryButton onClick={handleSaveStrategy} disabled={saving || Math.abs(total - 100) > 0.01}>
          {saving ? "Saving…" : "Save Strategy"}
        </PrimaryButton>
      </Modal>
    </section>
  );
}

// main app shell
export default function App() {
  const [refreshTick, setRefreshTick] = useState(0);

  return (
    <div style={{ fontFamily: "'Yeseva One', serif", background: "#f4b5de", minHeight: "100vh" }}>
      <header style={{
        background: "linear-gradient(135deg, #efca62 100%)",
        padding: "20px 32px", display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 100, boxShadow: "0 4px 24px rgba(26,26,46,0.3)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div>
            <div style={{ color: "#3f22ec", fontWeight: 900, fontSize: 22, letterSpacing: -0.5, justifyContent: "center", textAlign: "center" }}>InvestThing</div>
            <div style={{ color: "#ffff", fontSize: 12 }}>Your personal smart portfolio tracker</div>
          </div>
        </div>
        <div style={{ color: "#3f22ec", fontWeight:600, fontSize: 15 }}>
          {new Date().toLocaleDateString("en-MY", { weekday: "short", year: "numeric", month: "short", day: "numeric" })}
        </div>
      </header>

      <main style={{ maxWidth: 800, margin: "0 auto", padding: "48px 24px" }}>
        <PortfolioSection onRefresh={() => setRefreshTick(t => t + 1)} />
        <GoalSection triggerRefresh={refreshTick} />
        <RebalancingSection />
      </main>

      <footer style={{ textAlign: "center", padding: "24px", color: "#ffff", fontSize: 13 }}>
        ARCEUS · InvesThing · Prices refresh every 60s
      </footer>
    </div>
  );
}
