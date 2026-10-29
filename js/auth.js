
const API_BASE = "http://127.0.0.1:8000/api";

function getToken(){ return localStorage.getItem("ktxToken"); }
function authHeaders(){
  const token=getToken();
  return token ? {"Authorization":"Bearer "+token,"Content-Type":"application/json"} : {"Content-Type":"application/json"};
}
async function api(path, options={}){
  const opts={...options, headers:{...authHeaders(), ...(options.headers||{})}};
  const res=await fetch(API_BASE+path, opts);
  if(res.status===401){ localStorage.removeItem("ktxToken"); localStorage.removeItem("ktxUser"); location.href="/index.html"; return; }
  const data=await res.json().catch(()=>({}));
  if(!res.ok){
    let message = "Có lỗi xảy ra";
    if(Array.isArray(data.detail)){
      message = data.detail.map(item => {
        const loc = Array.isArray(item.loc) ? item.loc.join(" > ") : "";
        return `${loc}: ${item.msg || "Dữ liệu không hợp lệ"}`;
      }).join("\n");
    } else if(typeof data.detail === "string"){
      message = data.detail;
    } else if(data.detail && typeof data.detail === "object"){
      message = JSON.stringify(data.detail);
    }
    throw new Error(message);
  }
  return data;
}
async function login(event){
  event.preventDefault();
  const role=document.getElementById("role").value;
  const username=document.getElementById("username").value.trim();
  const password=document.getElementById("password").value;
  const error=document.getElementById("error");
  try{
    const data=await api("/auth/login",{method:"POST",body:JSON.stringify({username,password})});
    if(data.role!==role) throw new Error("Tài khoản không thuộc quyền đã chọn.");
    localStorage.setItem("ktxToken",data.access_token);
    localStorage.setItem("ktxUser",JSON.stringify(data));
    location.href="/"+data.role+"/home.html";
  }catch(e){ error.textContent=e.message; }
}
async function requireRole(role){
  const token=getToken();
  if(!token){location.href="/index.html";return null;}
  try{
    const user=await api("/auth/me");
    if(role && user.role!==role){location.href="/index.html";return null;}
    document.querySelectorAll("[data-user]").forEach(e=>e.textContent=user.full_name);
    return user;
  }catch(e){return null;}
}
function logout(){localStorage.removeItem("ktxToken");localStorage.removeItem("ktxUser");location.href="/index.html";}
