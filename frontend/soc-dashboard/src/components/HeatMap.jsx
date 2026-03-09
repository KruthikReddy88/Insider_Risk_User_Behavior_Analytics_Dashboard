import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function HeatMap({ data = [] }) {

  const deptCounts = {};

  data.forEach(d => {

    const dept = d.department || "Unknown";

    deptCounts[dept] = (deptCounts[dept] || 0) + 1;

  });

  const chartData = Object.keys(deptCounts).map(d => ({
    department: d,
    events: deptCounts[d]
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData}>
        <XAxis dataKey="department"/>
        <YAxis/>
        <Tooltip/>
        <Bar dataKey="events" fill="#ff7b72"/>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default HeatMap;