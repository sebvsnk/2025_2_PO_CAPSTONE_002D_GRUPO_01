
function go(href){ window.location.href = href; }
function setActiveNav(){
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(a=>{
    const target = a.getAttribute('href');
    if(target && path === target) a.classList.add('active');
  });
}
document.addEventListener('DOMContentLoaded', setActiveNav);
