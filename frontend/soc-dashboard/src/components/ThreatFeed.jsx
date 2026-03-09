import React,{useEffect,useState} from "react";
import axios from "axios";

function ThreatFeed(){

 const [alerts,setAlerts] = useState([]);

 useEffect(()=>{

  const fetchAlerts = ()=>{

   axios.get("http://localhost:5000/api/threat-feed")
   .then(res=>{
    if(Array.isArray(res.data)){
     setAlerts(res.data)
    }
   })

  }

  fetchAlerts()

  const interval = setInterval(fetchAlerts,3000)

  return ()=>clearInterval(interval)

 },[])

 return(

<div>

 {alerts.map((a,i)=>(
  <p key={i} className="alert">
   ⚠ {a.user} risk {a.risk_score}
  </p>
 ))}

</div>

 )

}

export default ThreatFeed