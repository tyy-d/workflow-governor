import { useEffect, useState, type CSSProperties } from 'react'

const colors=[['Sage','#78917b'],['Blue','#7794b4'],['Lavender','#a091b4'],['Rose','#bd9290'],['Sand','#b5a078'],['Stone','#96938b']]
const valid=(value:string|null):value is string=>Boolean(value&&/^#[a-f\d]{6}$/i.test(value))
export function usePageColor(page:string) {
 const read=()=>{try{const saved=localStorage.getItem(`page-color:${page}`);return valid(saved)?saved:page==='overview'?'#78917b':'#7794b4'}catch{return '#78917b'}}
 const [color,setColor]=useState(read)
 const [error,setError]=useState('')
 useEffect(()=>{setColor(read());setError('')},[page])
 const change=(next:string)=>{if(!valid(next))return;setColor(next);try{localStorage.setItem(`page-color:${page}`,next);setError('')}catch{setError('Color could not be saved in this browser.')}}
 return {style:{'--page-color':color} as CSSProperties,control:<details className="page-color-menu"><summary aria-label="Page color" title="Page color · saved in this browser"><span style={{background:color}}/>Color</summary><div className="page-color-options"><strong>Page color</strong><div className="color-swatches">{colors.map(([label,value])=><button key={label} type="button" aria-label={`${label} page color`} aria-pressed={color===value} style={{background:value}} onClick={()=>change(value)}>{color===value?'✓':''}</button>)}</div><label>Custom color<input type="color" aria-label="Custom page color" value={color} onChange={e=>change(e.target.value)}/></label>{error&&<small role="alert">{error}</small>}</div></details>}
}
