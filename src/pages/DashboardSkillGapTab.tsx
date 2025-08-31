import { useState, useEffect } from "react";

const API = "/api/skill-gap";

const DashboardSkillGapTab = () => {
  const [gaps, setGaps] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(API, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setGaps(data.gaps || "");
        setLoading(false);
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    const token = localStorage.getItem("token");
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ gaps }),
    });
    if (res.ok) setMessage("Skill gap analysis saved!");
    else setMessage("Failed to save.");
  };

  if (loading) return <div>Loading skill gap analysis...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Skill Gap Analysis</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className="w-full border rounded p-2"
          rows={6}
          value={gaps}
          onChange={e => setGaps(e.target.value)}
          placeholder="Describe your current skill gaps or areas for improvement..."
        />
        <button type="submit" className="px-4 py-2 bg-primary text-white rounded">Save</button>
        {message && <div className="text-green-600 mt-2">{message}</div>}
      </form>
    </div>
  );
};

export default DashboardSkillGapTab;
