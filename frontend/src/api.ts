export async function api<T>(path: string, body?: unknown): Promise<T> {
 const serialized=body===undefined?undefined:JSON.stringify(body)
 const slot=`request:${path}:${serialized}`
 let key=serialized?sessionStorage.getItem(slot):null
 if(serialized&&!key){key=Array.from(crypto.getRandomValues(new Uint8Array(16)),n=>n.toString(16).padStart(2,'0')).join('');sessionStorage.setItem(slot,key)}
 const response=await fetch(`/api${path}`,serialized===undefined?undefined:{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key!},body:serialized})
 const value=await response.json()
 if(!response.ok){if(response.status<500)sessionStorage.removeItem(slot);throw new Error(value.error||`Request failed (${response.status})`)}
 sessionStorage.removeItem(slot)
 return value as T
}
