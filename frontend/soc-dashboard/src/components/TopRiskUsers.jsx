import React,{useEffect,useState} from "react";
import axios from "axios";

function TopRiskUsers(){

 const [users,setUsers] = useState([]);

 useEffect(()=>{

  axios.get("http://localhost:5000/api/top-users")
  .then(res=>{
   if(Array.isArray(res.data)){
    setUsers(res.data)
   }
  })

 },[])

 return(

<table>

<thead>
<tr>
<th>User</th>
<th>Department</th>
<th>Risk</th>
</tr>
</thead>

<tbody>

{users.map((u,i)=>(
<tr key={i}>
<td>{u.user_id}</td>
<td>{u.department}</td>
<td>
<span className={`risk-badge ${u.risk > 80 ? "high":"medium"}`}>
{u.risk}
</span>
</td>
</tr>
))}

</tbody>

</table>

 )

}

export default TopRiskUsers