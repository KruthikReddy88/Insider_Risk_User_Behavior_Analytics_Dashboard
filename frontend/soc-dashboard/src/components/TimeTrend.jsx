import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function TimeTrend({ data = [] }) {

  const [chartData, setChartData] = useState([]);

  useEffect(() => {

    const now = new Date().toLocaleTimeString();

    const newPoint = {
      time: now,
      events: data.length
    };

    setChartData(prev => {
      const updated = [...prev, newPoint];

      if (updated.length > 12) {
        updated.shift();
      }

      return updated;
    });

  }, [data]);

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chartData}>
        <XAxis dataKey="time"/>
        <YAxis/>
        <Tooltip/>
        <Line
          type="monotone"
          dataKey="events"
          stroke="rgb(255, 0, 0)"
          strokeWidth={3}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default TimeTrend;