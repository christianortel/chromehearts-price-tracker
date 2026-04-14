"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Point = {
  label: string;
  retail?: number;
  ask?: number;
  sold?: number;
};

export function PriceHistoryChart({ points }: { points: Point[] }) {
  return (
    <div className="panel h-[320px] p-4">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">History</p>
          <h3 className="mt-2 text-xl font-semibold">Retail, ask, and sold signals</h3>
        </div>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points}>
          <defs>
            <linearGradient id="askFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#b98958" stopOpacity={0.45} />
              <stop offset="95%" stopColor="#b98958" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="retailFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#65745f" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#65745f" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
          <XAxis dataKey="label" stroke="rgba(243,236,223,0.45)" tickLine={false} axisLine={false} />
          <YAxis stroke="rgba(243,236,223,0.45)" tickLine={false} axisLine={false} />
          <Tooltip />
          <Area type="monotone" dataKey="retail" stroke="#65745f" fill="url(#retailFill)" strokeWidth={2} />
          <Area type="monotone" dataKey="ask" stroke="#b98958" fill="url(#askFill)" strokeWidth={2} />
          <Area type="monotone" dataKey="sold" stroke="#d16f4d" fillOpacity={0} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

