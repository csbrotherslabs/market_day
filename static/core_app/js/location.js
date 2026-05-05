(function(){
  const locEl=document.getElementById('locationDisplay'); if(!locEl) return;
  const csrf=document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  const help=document.getElementById('locationHelpText');
  function setLabel(city){locEl.childNodes[0].textContent=`📍 ${city||'Set location'} `;}
  async function postForm(url,data){const body=new URLSearchParams(data); const res=await fetch(url,{method:'POST',headers:{'X-CSRFToken':csrf,'Content-Type':'application/x-www-form-urlencoded'},body}); return res.json();}
  if(!locEl.dataset.currentCity && !localStorage.getItem('marketflow_location_denied') && navigator.geolocation){
    navigator.geolocation.getCurrentPosition(async(pos)=>{const d=await postForm('/location/update/',{latitude:pos.coords.latitude,longitude:pos.coords.longitude}); setLabel(d.city);},()=>{localStorage.setItem('marketflow_location_denied','true'); if(help) help.textContent='Location access denied. Please set location manually.';});
  }
  const modal=document.getElementById('locationModal');
  document.getElementById('openLocationModal')?.addEventListener('click',()=>modal.classList.remove('hidden'));
  document.getElementById('closeLocationModal')?.addEventListener('click',()=>modal.classList.add('hidden'));
  document.getElementById('manualLocationForm')?.addEventListener('submit',async(e)=>{e.preventDefault(); const fd=new FormData(e.target); const d=await postForm('/location/manual-update/',Object.fromEntries(fd.entries())); setLabel(d.city); modal.classList.add('hidden');});
})();
