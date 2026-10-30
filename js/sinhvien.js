function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));}
function money(v){return Number(v||0).toLocaleString('vi-VN')+'đ';}
async function loadMyRoom(){
    const data=await api('/stays/my-room').catch(()=>({room:null}));
    document.querySelectorAll('[data-room]').forEach(e=>e.textContent=data.room||'Chưa có phòng');
    const r=document.getElementById('currentRoom');
    if(r)r.value=data.room||'Chưa có phòng';
    const b=document.getElementById('currentBed');
    if(b)b.textContent=data.bed?String(data.bed).padStart(2,'0'):'-';
    const build=document.getElementById('currentBuilding');
    if(build)build.textContent=data.building||'-';
}
async function loadAvailableRooms(){const s=document.getElementById('desiredRoom');
    if(!s)return;try{const rows=await api('/rooms');
        const available=rows.filter(r=>r.available>0);
        s.innerHTML='<option value="">-- Chọn phòng --</option>'+available.map(r=>`<option value="${escapeHtml(r.code)}">${escapeHtml(r.code)} - ${escapeHtml(r.building)} - còn ${r.available} chỗ</option>`).join('')}catch(e){s.innerHTML='<option>Không tải được phòng</option>'}}
async function submitRequest(type){try{const desired=document.getElementById('desiredRoom')?.value||null;const note=document.getElementById('requestNote')?.value||'';const current=document.getElementById('currentRoom')?.value||null;const data=await api('/stays',{method:'POST',body:JSON.stringify({request_type:type,desired_room:desired,current_room:current,note})});alert(`Đã gửi yêu cầu. Mã: ${type==='Chuyển phòng'?'CP':type==='Trả phòng'?'TP':'DK'}${String(data.id).padStart(4,'0')}`);loadMyRequests()}catch(e){alert(e.message)}}
async function loadMyRequests(){const body=document.getElementById('myStayBody');if(!body)return;try{const rows=await api('/stays/my');body.innerHTML=rows.length?rows.map(x=>`<tr><td>${x.id}</td><td>${escapeHtml(x.request_type)}</td><td>${escapeHtml(x.current_room||'-')}</td><td>${escapeHtml(x.desired_room||'-')}</td><td>${escapeHtml(x.status)}</td></tr>`).join(''):'<tr><td colspan="5">Chưa có yêu cầu.</td></tr>'}catch(e){}}
async function sendFeedback(){const text=document.getElementById('feedbackTitle')?.value.trim();if(!text){alert('Nhập nội dung phản ánh.');return}try{const d=await api('/complaints',{method:'POST',body:JSON.stringify({content:text})});alert('Đã gửi '+d.code);document.getElementById('feedbackTitle').value='';loadMyComplaints()}catch(e){alert(e.message)}}
async function loadMyComplaints(){const body=document.getElementById('myComplaintBody');if(!body)return;try{const rows=await api('/complaints/my');body.innerHTML=rows.length?rows.map(c=>`<tr><td>${escapeHtml(c.code)}</td><td>${escapeHtml(c.content)}</td><td>${new Date(c.created_at).toLocaleDateString('vi-VN')}</td><td>${escapeHtml(c.status)}</td></tr>`).join(''):'<tr><td colspan="4">Chưa có phản ánh.</td></tr>'}catch(e){}}
async function loadMyFees(){const body=document.getElementById('feeTable');if(!body)return;try{const rows=await api('/finance/fees');const debt=rows.filter(x=>x.status==='Chưa thu').reduce((a,x)=>a+Number(x.amount),0);const paid=rows.filter(x=>x.status==='Đã thu').reduce((a,x)=>a+Number(x.amount),0);const total=rows.reduce((a,x)=>a+Number(x.amount),0);document.getElementById('feeTotal')?.replaceChildren(document.createTextNode(money(total)));document.getElementById('feePaid')?.replaceChildren(document.createTextNode(money(paid)));document.getElementById('feeDebt')?.replaceChildren(document.createTextNode(money(debt)));body.innerHTML=rows.length?rows.map(x=>`<tr><td>${x.month}</td><td>${money(x.amount)}</td><td>${x.due_date}</td><td>${escapeHtml(x.status)}</td></tr>`).join(''):'<tr><td colspan="4">Chưa có khoản thu.</td></tr>'}catch(e){}}
async function sendChat(){const input=document.getElementById('chatInput'),box=document.getElementById('chatBox');if(!input||!box||!input.value.trim())return;const q=input.value.trim();box.innerHTML+=`<div class="notice"><strong>Bạn:</strong> ${escapeHtml(q)}</div>`;try{const d=await api('/ai/chat',{method:'POST',body:JSON.stringify({question:q})});const src=(d.sources||[]).map(x=>x.code).join(', ')||'Không có';box.innerHTML+=`<div class="notice"><strong>KTX-AI:</strong> ${escapeHtml(d.answer)}<br><small>Nguồn: ${escapeHtml(src)}</small></div>`}catch(e){box.innerHTML+=`<div class="notice"><strong>KTX-AI:</strong> ${escapeHtml(e.message)}</div>`}input.value=''}
async function initStudent(){const u=await requireRole('sinhvien');if(!u)return;await loadMyRoom();await loadAvailableRooms();await loadMyRequests();await loadMyFees();await loadMyComplaints();}
document.addEventListener('DOMContentLoaded',initStudent);
