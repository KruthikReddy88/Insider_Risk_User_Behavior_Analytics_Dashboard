import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function TimeTrend({ data = [] }) {

  if (!data || data.length === 0) {
    return <p style={{color:"#888"}}>Waiting for activity...</p>;
  }

  const hourCounts = {};

  data.forEach(event => {

    const hour = event.hour ?? "Unknown";

    hourCounts[hour] = (hourCounts[hour] || 0) + 1;

  });

  const chartData = Object.keys(hourCounts).map(h => ({
    hour: h,
    events: hourCounts[h]
  }));

  chartData.sort((a,b)=>a.hour-b.hour);

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chartData}>
        <XAxis dataKey="hour"/>
        <YAxis/>
        <Tooltip/>
        <Line
          type="monotone"
          dataKey="events"
          stroke="#ff4d4f"
          strokeWidth={3}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default TimeTrend;