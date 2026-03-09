import React, { useEffect, useState } from "react";
import axios from "axios";

import TimeTrend from "../components/TimeTrend";
import HeatMap from "../components/HeatMap";
import ThreatFeed from "../components/ThreatFeed";
import TopRiskUsers from "../components/TopRiskUsers";
import AnomalySummary from "../components/AnomalySummary";

function SocDashboard(){

 const [data,setData] = useState([]);

 useEffect(()=>{

   const fetchData = () => {

     axios.get("http://localhost:5000/api/risk-data")
     .then(res => {

       if(Array.isArray(res.data)){
         setData(res.data);
       } else {
         setData([]);
       }

     })
     .catch(()=>setData([]));

   };

   fetchData();

   const interval = setInterval(fetchData,3000);

   return ()=>clearInterval(interval);

 },[]);

 return(

<div className="dashboard">

<h1>🛡 SOC Monitoring Dashboard</h1>

<div className="metrics">
 <AnomalySummary/>
</div>

<div className="row">

 <div className="panel">
  <h2>🚨 Threat Feed</h2>
  <ThreatFeed/>
 </div>

 <div className="panel">
  <h2>🔥 Top Risk Users</h2>
  <TopRiskUsers/>
 </div>

</div>

<div className="row">

 <div className="panel">
  <h2>📈 Activity Timeline</h2>
  <TimeTrend data={data}/>
 </div>

 <div className="panel">
  <h2>🌡 Department Activity</h2>
  <HeatMap data={data}/>
 </div>

</div>

</div>

 )

}

export default SocDashboard;