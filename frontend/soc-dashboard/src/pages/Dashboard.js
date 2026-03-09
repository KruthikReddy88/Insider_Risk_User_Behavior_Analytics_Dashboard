import React, { useEffect, useState } from "react";
import axios from "axios";

import TimeTrend from "../components/TimeTrend";
import HeatMap from "../components/HeatMap";
import ThreatFeed from "../components/ThreatFeed";
import TopRiskUsers from "../components/TopRiskUsers";
import AnomalySummary from "../components/AnomalySummary";

function Dashboard(){

 const [data,setData] = useState([]);

 useEffect(()=>{

 const fetchData = () => {

   axios.get("http://localhost:5000/api/risk-data")
   .then(res => {

     if(Array.isArray(res.data)){
       setData(res.data)
     } else {
       setData([])
     }

   })
   .catch(()=>setData([]))

 }

 fetchData()

 const interval = setInterval(fetchData,3000)

 return ()=>clearInterval(interval)

},[])

 return(

   <div className="dashboard-container">

    <h1>🛡 SOC Monitoring Dashboard</h1>

    <ThreatFeed/>

    <TopRiskUsers/>

    <AnomalySummary/>

    <TimeTrend data={Array.isArray(data) ? data : []}/>

    <HeatMap data={Array.isArray(data) ? data : []}/>

    <a
      href="http://localhost:5000/api/risk-data"
      download
    >
      Download Risk Data
    </a>

   </div>

 )

}

export default Dashboard