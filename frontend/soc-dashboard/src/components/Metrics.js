export default function Metrics({data}){

 const totalUsers = new Set(data.map(d=>d.user_id)).size

 const avgRisk = (
   data.reduce((a,b)=>a+b.final_risk_score,0) /
   data.length
 ).toFixed(2)

 const anomalies =
   data.reduce((a,b)=>a+b.iso_anomaly,0)

 return(

  <div className="metrics">

   <div className="card">
     <h3>Total Users</h3>
     <h2>{totalUsers}</h2>
   </div>

   <div className="card">
     <h3>Average Risk</h3>
     <h2>{avgRisk}</h2>
   </div>

   <div className="card">
     <h3>Total Anomalies</h3>
     <h2>{anomalies}</h2>
   </div>

  </div>

 )

}