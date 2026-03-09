import React,{useEffect,useState} from "react";
import axios from "axios";

export default function ThreatFeed(){

 const [threats,setThreats] = useState([]);

 useEffect(()=>{

   axios.get("http://localhost:5000/api/threat-feed")
   .then(res => setThreats(res.data));

 },[]);

 const getColor = (risk) => {

   if(risk > 85) return "#ff4d4f";   // Critical
   if(risk > 64) return "#faad14";   // High
   return "#52c41a";                 // Medium

 };

 return(

   <div style={{marginTop:"40px"}}>

    <h2>Live Threat Feed</h2>

    {threats.map((t,i)=>(
      <div
        key={i}
        style={{
          padding:"10px",
          borderBottom:"1px solid #30363d",
          color:getColor(t.risk_score)
        }}
      >
        ⚠ {t.user} — Risk Score {t.risk_score}
      </div>
    ))}

   </div>

 )

}