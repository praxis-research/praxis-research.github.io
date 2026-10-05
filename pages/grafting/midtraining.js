// Midtraining approximation: the four models of the paper's Figure 4 as grouped bars. Drawn like the CMT chart
// (same helpers el/hover/tipCard and the same bcmt-* classes), coloured by the condition tokens.
(function(){
const D=JSON.parse(document.getElementById("bmid-data").textContent);
const COL={"control":"var(--c-bare)","mid-trained":"var(--c-midtrain)","native":"var(--c-native)","graft":"var(--c-graft)"};
function draw(){
  if(typeof el!=="function") return;
  Object.keys(COL).forEach(k=>{ if(typeof AC==="object" && !AC[k]) AC[k]=COL[k]; });
  const arms=D.arms;
  document.getElementById("bmid-key").innerHTML=arms.map(a=>`<span><i style="background:${COL[a]}"></i>${a}</span>`).join("");
  const W=1080, L=40, R=6, rowH=250, T=8, H=T+D.bands.length*rowH;
  const host=document.getElementById("bmid-chart"); host.innerHTML="";
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const unit=D.bands[0].rows.length;                        // both bands share one group width
  let y0=T;
  D.bands.forEach(band=>{
    const top=y0+44, base=y0+rowH-52, Y=v=>base-(Math.max(0,Math.min(100,v))/100)*(base-top);
    svg.appendChild(el("text",{x:L,y:y0+18,class:"bcmt-band"},band.label));
    svg.appendChild(el("line",{x1:L,x2:W-R,y1:y0+24,y2:y0+24,stroke:"var(--heading)","stroke-opacity":.45,"stroke-width":1}));
    [0,50,100].forEach(t=>{ svg.appendChild(el("line",{x1:L,x2:W-R,y1:Y(t),y2:Y(t),stroke:t?"var(--c-wash-2)":"var(--c-axis)"}));
      svg.appendChild(el("text",{x:L-6,y:Y(t)+4,"text-anchor":"end",class:"bcmt-t"},String(t))); });
    const gW=(W-L-R)/unit, bw=Math.min(26,(gW*0.8)/arms.length), off=(unit-band.rows.length)*gW/2;   // a shorter band is centred
    band.rows.forEach((r,gi)=>{
      const gx=L+off+gi*gW, x0=gx+(gW-bw*arms.length)/2, g=el("g",{});
      g.appendChild(el("rect",{x:gx,y:top-6,width:gW,height:base-top+10,fill:"transparent"}));
      arms.forEach((a,ai)=>{ const v=r.values[a]; if(v==null) return;
        const x=x0+ai*bw, yy=Y(v);
        g.appendChild(el("rect",{x:x+1,y:yy,width:bw-2,height:Math.max(1.5,base-yy),fill:COL[a]}));
        g.appendChild(el("text",{x:x+bw/2,y:yy-4,"text-anchor":"middle",class:"bcmt-v"},v.toFixed(0)));
      });
      const lab=el("text",{x:gx+gW/2,y:base+18,"text-anchor":"middle",class:"bcmt-cl"}); lab.textContent=r.label+(r.dir==="down"?" ↓":"");
      g.appendChild(lab);
      if(typeof hover==="function" && typeof tipCard==="function")
        hover(g,()=>tipCard(r.label+(r.dir==="down"?" ↓":""), D.model+" · two-seed mean"+(r.note?" · "+r.note:""),
          arms.map(a=>[a,r.values[a]/100,null]), null));
      svg.appendChild(g);
    });
    y0+=rowH;
  });
  host.appendChild(svg);
}
window.addEventListener("load",draw);
})();
