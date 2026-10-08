import os

# 1. tailwind.config.js
tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""
with open("frontend/tailwind.config.js", "w") as f:
    f.write(tailwind_config)

# 2. src/index.css
index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #f8fafc;
}"""
with open("frontend/src/index.css", "w") as f:
    f.write(index_css)

# 3. src/App.jsx
app_jsx = """import React, { useState } from 'react';

const HandoffQueue = () => (
  <div className="p-8 w-full max-w-6xl mx-auto">
    <div className="flex justify-between items-center mb-6">
      <div>
        <h1 className="text-2xl font-bold">Handoff Queue</h1>
        <p className="text-gray-500 text-sm">Sunrise Clinic, Dehradun - conversations the agent escalated</p>
      </div>
      <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm font-semibold">4 OPEN</div>
    </div>

    <div className="grid grid-cols-4 gap-4 mb-6">
      <div className="bg-white p-4 rounded shadow border border-gray-100">
        <div className="text-gray-500 text-xs uppercase font-semibold">Conversations</div>
        <div className="text-2xl font-bold mt-1">37</div>
        <div className="text-gray-400 text-xs">today</div>
      </div>
      <div className="bg-white p-4 rounded shadow border border-gray-100">
        <div className="text-gray-500 text-xs uppercase font-semibold">Completed by Agent</div>
        <div className="text-2xl font-bold mt-1">31</div>
        <div className="text-gray-400 text-xs">84%</div>
      </div>
      <div className="bg-white p-4 rounded shadow border border-blue-200">
        <div className="text-gray-500 text-xs uppercase font-semibold">Escalated</div>
        <div className="text-2xl font-bold mt-1">6</div>
        <div className="text-blue-500 text-xs">4 still open</div>
      </div>
      <div className="bg-white p-4 rounded shadow border border-red-200">
        <div className="text-gray-500 text-xs uppercase font-semibold">Urgent</div>
        <div className="text-2xl font-bold mt-1 text-red-600">1</div>
        <div className="text-red-500 text-xs">clinical, unresolved</div>
      </div>
    </div>

    <div className="bg-white rounded shadow border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 font-semibold">Open handoffs</div>
      <table className="w-full text-left text-sm">
        <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th className="px-6 py-3 font-medium">Conversation</th>
            <th className="px-6 py-3 font-medium">Caller Said</th>
            <th className="px-6 py-3 font-medium">Reason</th>
            <th className="px-6 py-3 font-medium">Time</th>
            <th className="px-6 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b border-gray-50">
            <td className="px-6 py-4 font-mono text-xs">cv_4471</td>
            <td className="px-6 py-4 font-medium">"Seene mein dard ho raha hai"</td>
            <td className="px-6 py-4"><span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-semibold">CLINICAL</span></td>
            <td className="px-6 py-4 text-gray-500">11:42</td>
            <td className="px-6 py-4"><button className="bg-blue-600 text-white px-4 py-1.5 rounded text-xs hover:bg-blue-700">Resolve</button></td>
          </tr>
          <tr className="border-b border-gray-50">
            <td className="px-6 py-4 font-mono text-xs">cv_4468</td>
            <td className="px-6 py-4 font-medium">Cancel for a different patient</td>
            <td className="px-6 py-4"><span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-semibold">NOT AUTHORISED</span></td>
            <td className="px-6 py-4 text-gray-500">11:20</td>
            <td className="px-6 py-4"><button className="border border-gray-300 text-gray-700 px-4 py-1.5 rounded text-xs hover:bg-gray-50">Resolve</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
);

const ConversationDetail = () => (
  <div className="p-8 w-full max-w-6xl mx-auto flex gap-6">
    <div className="flex-1">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Conversation cv_4471</h1>
          <p className="text-gray-500 text-sm">Sunrise Clinic, Dehradun - 27 Sep 2026, 11:42</p>
        </div>
        <div className="bg-red-100 text-red-700 px-3 py-1 rounded text-sm font-semibold">ESCALATED — CLINICAL</div>
      </div>

      <div className="bg-white rounded shadow border border-gray-100 p-6 mb-6">
        <h2 className="font-semibold mb-4">Transcript and tool calls</h2>
        
        <div className="flex mb-4">
          <div className="w-16 text-xs text-gray-400 font-semibold uppercase pt-2">Caller</div>
          <div className="bg-gray-50 p-3 rounded-lg flex-1 border border-gray-100">Kal subah ka appointment mil jayega Dr. Rao ke saath?</div>
        </div>

        <div className="flex mb-4">
          <div className="w-16 text-xs text-gray-400 font-semibold uppercase pt-2">Tool</div>
          <div className="bg-blue-50 text-blue-800 p-3 rounded-lg flex-1 font-mono text-xs border border-blue-100">
            search_slots(doctor_id="dr_rao", date="2026-09-28", window="morning")<br/>
            → 3 slots: 09:30, 10:15, 11:00
          </div>
        </div>

        <div className="flex mb-4">
          <div className="w-16 text-xs text-gray-400 font-semibold uppercase pt-2">Agent</div>
          <div className="bg-gray-100 p-3 rounded-lg flex-1 border border-gray-200">Ji, kal subah 9:30, 10:15 aur 11:00 khali hai. Kaun sa theek rahega?</div>
        </div>
        
        <div className="flex mb-4">
          <div className="w-16 text-xs text-gray-400 font-semibold uppercase pt-2">Caller</div>
          <div className="bg-gray-50 p-3 rounded-lg flex-1 border border-gray-100">10:15 kar dijiye. Waise abhi seene mein dard ho raha hai thoda.</div>
        </div>

        <div className="flex mb-4">
          <div className="w-16 text-xs text-gray-400 font-semibold uppercase pt-2">Tool</div>
          <div className="bg-blue-50 text-blue-800 p-3 rounded-lg flex-1 font-mono text-xs border border-blue-100">
            escalate_to_human(reason="clinical_urgent", detail="caller reports active chest pain")
          </div>
        </div>
        
        <div className="flex mb-4">
          <div className="w-16 text-xs text-gray-400 font-semibold uppercase pt-2">Agent</div>
          <div className="bg-gray-100 p-3 rounded-lg flex-1 border border-gray-200">Main abhi aapko clinic se connect kar rahi hoon. Agar dard badh raha hai, turant nazdeeki emergency par jaiye.</div>
        </div>
        
        <div className="bg-red-50 text-red-700 p-3 rounded-lg border border-red-100 text-center font-medium mt-6 text-sm">
          Booking flow abandoned. No appointment was created.
        </div>
      </div>
    </div>
    
    <div className="w-80 space-y-6 pt-16">
      <div className="bg-white rounded shadow border border-gray-100 p-5">
        <h3 className="font-semibold mb-4 text-sm">Outcome</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between"><span className="text-gray-500">terminal_state</span><span className="font-mono">escalated</span></div>
          <div className="flex justify-between"><span className="text-gray-500">escalation_reason</span><span className="font-mono">clinical_urgent</span></div>
          <div className="flex justify-between"><span className="text-gray-500">patient_id</span><span className="font-mono">pt_0192</span></div>
          <div className="flex justify-between"><span className="text-gray-500">appointment_id</span><span className="font-mono">null</span></div>
          <hr className="my-2"/>
          <div className="flex justify-between"><span className="text-gray-500">tool_calls</span><span className="font-mono">2</span></div>
          <div className="flex justify-between"><span className="text-gray-500">turns</span><span className="font-mono">6</span></div>
          <div className="flex justify-between"><span className="text-gray-500">tokens</span><span className="font-mono">3,140</span></div>
          <div className="flex justify-between"><span className="text-gray-500">latency</span><span className="font-mono">4.2 s</span></div>
        </div>
      </div>
      
      <div className="bg-white rounded shadow border border-gray-100 p-5">
        <h3 className="text-gray-500 text-xs font-semibold uppercase mb-2">Determinism</h3>
        <div className="flex items-center text-sm">
          <span className="text-gray-600">Same terminal state across 3 runs.</span>
          <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-semibold ml-2">STABLE</span>
        </div>
      </div>
    </div>
  </div>
);

function App() {
  const [view, setView] = useState('queue');

  return (
    <div className="min-h-screen flex">
      <div className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-4 space-y-6">
        <button onClick={() => setView('queue')} className={`w-10 h-10 rounded-full border-2 ${view === 'queue' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}></button>
        <button onClick={() => setView('detail')} className={`w-10 h-10 rounded-full border-2 ${view === 'detail' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}></button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {view === 'queue' ? <HandoffQueue /> : <ConversationDetail />}
      </div>
    </div>
  );
}

export default App;
"""
with open("frontend/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(app_jsx)

print("Frontend files created successfully.")
