export default function HeatMap({data = []}) {

 return(

  <div>

   <h2>Risk Heatmap (Day vs Hour)</h2>

   <table>

    <thead>
     <tr>
      <th>Day</th>
      <th>Hour</th>
      <th>Risk</th>
     </tr>
    </thead>

    <tbody>

     {data.map((row,i)=>(
       <tr key={i}>
        <td>{row.day_of_week}</td>
        <td>{row.hour}</td>
        <td>{row.final_risk_score}</td>
       </tr>
     ))}

    </tbody>

   </table>

  </div>

 )

}