export default function TopUsers({data}){

 const sorted=[...data].sort(
  (a,b)=>b.final_risk_score-a.final_risk_score
 )

 return(

  <div className="panel">

   <h2>Top Risk Users</h2>

   <table>

    <thead>
      <tr>
       <th>User</th>
       <th>Risk</th>
      </tr>
    </thead>

    <tbody>

     {sorted.slice(0,10).map((u,i)=>(
       <tr key={i}>
        <td>{u.user_id}</td>
        <td>{u.final_risk_score}</td>
       </tr>
     ))}

    </tbody>

   </table>

  </div>

 )

}