(function(){
  const locEl=document.getElementById('locationDisplay'); if(!locEl) return;
  const csrf=document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  const help=document.getElementById('locationHelpText');
  const isBuyer=locEl.dataset.isAuthenticated==='true' && locEl.dataset.userRole==='BUYER';
  function setLabel(city){locEl.childNodes[0].textContent=`📍 ${city||'Set location'} `;}
  function showModal(){modal?.classList.remove('hidden');}
  function hideModal(){modal?.classList.add('hidden');}
  async function postForm(url,data){const body=new URLSearchParams(data); const res=await fetch(url,{method:'POST',headers:{'X-CSRFToken':csrf,'Content-Type':'application/x-www-form-urlencoded'},body}); return res.json();}
  const modal=document.getElementById('locationModal');
  if(!locEl.dataset.currentCity && navigator.geolocation){
    navigator.geolocation.getCurrentPosition(async(pos)=>{
      const d=await postForm('/location/update/',{latitude:pos.coords.latitude,longitude:pos.coords.longitude});
      setLabel(d.city);
      if(help && d.city && d.city !== 'Unknown Location') help.textContent='';
    },()=>{
      if(help) help.textContent='Location access denied. Please set location manually.';
      if(isBuyer) showModal();
    },{enableHighAccuracy:true,timeout:10000,maximumAge:0});
  }
  document.getElementById('openLocationModal')?.addEventListener('click',showModal);
  document.getElementById('closeLocationModal')?.addEventListener('click',hideModal);
  document.getElementById('manualLocationForm')?.addEventListener('submit',async(e)=>{e.preventDefault(); const fd=new FormData(e.target); const d=await postForm('/location/manual-update/',Object.fromEntries(fd.entries())); setLabel(d.city); hideModal();});
})();
