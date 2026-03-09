import {LineChart,Line,XAxis,YAxis,Tooltip} from "recharts";

export default function TimeTrend({data = []}) {

 return(

  <div>

   <h2>Time-of-Day Risk Trends</h2>

   <LineChart width={700} height={300} data={data}>

    <XAxis dataKey="hour"/>
    <YAxis/>
    <Tooltip/>

    <Line dataKey="final_risk_score" stroke="#faad14"/>

   </LineChart>

  </div>

 )

}