import React,{useEffect,useState} from "react";
import axios from "axios";

function AnomalySummary(){

 const [data,setData] = useState({
  usb_spikes:0,
  file_spikes:0,
  login_spikes:0
 });

 useEffect(()=>{

  const fetch = ()=>{

   axios.get("http://localhost:5000/api/anomaly-summary")
   .then(res=>setData(res.data))
   .catch(()=>{})

  }

  fetch();

  const interval = setInterval(fetch,3000);

  return ()=>clearInterval(interval);

 },[]);

 return(

<>
<div className="metric-card">
<h3>USB Events</h3>
<h2 className="counter">{data.usb_spikes}</h2>
</div>

<div className="metric-card">
<h3>File Spikes</h3>
<h2 className="counter">{data.file_spikes}</h2>
</div>

<div className="metric-card">
<h3>Login Alerts</h3>
<h2 className="counter">{data.login_spikes}</h2>
</div>
</>

 )

}

export default AnomalySummary;