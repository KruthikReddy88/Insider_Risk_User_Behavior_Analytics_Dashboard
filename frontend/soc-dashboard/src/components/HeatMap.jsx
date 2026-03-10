import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function HeatMap({ data = [] }) {

  if (!data || data.length === 0) {
    return <p style={{color:"#888"}}>Waiting for department data...</p>;
  }

  const deptCounts = {};

  data.forEach(event => {

    const dept = event.department || "Unknown";

    deptCounts[dept] = (deptCounts[dept] || 0) + 1;

  });

  const chartData = Object.keys(deptCounts).map(dept => ({
    department: dept,
    events: deptCounts[dept]
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