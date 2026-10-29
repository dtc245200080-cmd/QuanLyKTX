function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
}
function money(v){ return Number(v||0).toLocaleString('vi-VN') + 'đ'; }
function displayRequestCode(row){ const p=row.request_type==='Chuyển phòng'?'CP':row.request_type==='Trả phòng'?'TP':'DK'; return p+String(row.id).padStart(4,'0'); }

async function loadStays(){
  const body=document.getElementById('stayRequestsBody'); if(!body)return;
  try{ const rows=await api('/stays');
    body.innerHTML=rows.length?rows.map(r=>`<tr><td>${displayRequestCode(r)}</td><td>${escapeHtml(r.mssv)} - ${escapeHtml(r.student)}</td><td>${escapeHtml(r.request_type)}</td><td>${escapeHtml(r.current_room||'-')}</td><td>${escapeHtml(r.desired_room||'-')}</td><td>${escapeHtml(r.status)}</td><td>${r.status==='Chờ duyệt'?`<button class="btn btn-primary" onclick="approve(${r.id})">Duyệt</button> <button class="btn btn-danger" onclick="reject(${r.id})">Từ chối</button>`:'-'}</td></tr>`).join(''):'<tr><td colspan="7">Chưa có yêu cầu.</td></tr>';
  }catch(e){body.innerHTML=`<tr><td colspan="7">${escapeHtml(e.message)}</td></tr>`;}
}
async function approve(id){try{await api(`/stays/${id}/approve`,{method:'PATCH'});alert('Đã duyệt và cập nhật giường.');await loadStays();await loadRooms();}catch(e){alert(e.message)}}
async function reject(id){try{await api(`/stays/${id}/reject`,{method:'PATCH'});alert('Đã từ chối.');await loadStays();}catch(e){alert(e.message)}}

async function loadStudents(){
 const body=document.getElementById('studentTableBody'); if(!body)return;
 try{const rows=await api('/students'); body.innerHTML=rows.length?rows.map(s=>`<tr><td>${escapeHtml(s.mssv)}</td><td>${escapeHtml(s.full_name)}</td><td>${escapeHtml(s.class_name)}</td><td>${escapeHtml(s.phone)}</td><td>${escapeHtml(s.room||'-')}</td><td>${escapeHtml(s.status)}</td></tr>`).join(''):'<tr><td colspan="6">Chưa có sinh viên.</td></tr>';}catch(e){body.innerHTML=`<tr><td colspan="6">${escapeHtml(e.message)}</td></tr>`}
}
function showStudentForm(){document.getElementById('studentForm').style.display='block'}
function hideStudentForm(){document.getElementById('studentForm').style.display='none'}
async function createStudent(){
 const data={mssv:studentMssv.value.trim(),full_name:studentName.value.trim(),class_name:studentClass.value.trim(),phone:studentPhone.value.trim(),password:studentPassword.value||'123456'};
 if(!data.mssv||!data.full_name){alert('Vui lòng nhập MSSV và họ tên.');return}
 try{const r=await api('/students',{method:'POST',body:JSON.stringify(data)});alert(`Đã thêm sinh viên. Tài khoản: ${r.username}\nMật khẩu: ${r.password}`);['studentMssv','studentName','studentClass','studentPhone','studentPassword'].forEach(id=>document.getElementById(id).value='');hideStudentForm();loadStudents()}catch(e){alert(e.message)}
}

async function loadBuildings(){
 const select=document.getElementById('roomBuilding'); if(!select)return;
 try{const rows=await api('/rooms/buildings');select.innerHTML='<option value="">-- Chọn tòa --</option>'+rows.map(b=>`<option value="${escapeHtml(b.code)}">${escapeHtml(b.code)} - ${escapeHtml(b.name)}</option>`).join('')}catch(e){select.innerHTML='<option value="">Không tải được</option>'}
}
async function loadRooms(){
 const body=document.getElementById('roomTableBody'); if(!body)return;
 try{const rows=await api('/rooms');body.innerHTML=rows.length?rows.map(r=>`<tr><td>${escapeHtml(r.code)}</td><td>${escapeHtml(r.building)}</td><td>${r.floor}</td><td>${r.capacity}</td><td>${r.occupied}</td><td>${r.available}</td><td>${escapeHtml(r.status)}</td></tr>`).join(''):'<tr><td colspan="7">Chưa có phòng.</td></tr>'}catch(e){body.innerHTML=`<tr><td colspan="7">${escapeHtml(e.message)}</td></tr>`}
}
function showBuildingForm(){document.getElementById('buildingForm').style.display='block'}
function hideBuildingForm(){document.getElementById('buildingForm').style.display='none'}
async function createBuilding(){const data={code:buildingCode.value.trim(),name:buildingName.value.trim(),floors:Number(buildingFloors.value)};if(!data.code||!data.name||!data.floors){alert('Nhập đủ thông tin tòa.');return}try{await api('/rooms/buildings',{method:'POST',body:JSON.stringify(data)});alert('Đã thêm tòa.');hideBuildingForm();await loadBuildings();}catch(e){alert(e.message)}}
function showRoomForm(){document.getElementById('roomForm').style.display='block';loadBuildings()}
function hideRoomForm(){document.getElementById('roomForm').style.display='none'}
async function createRoom(){const data={code:roomCode.value.trim(),building_code:roomBuilding.value,capacity:Number(roomCapacity.value),floor:Number(roomFloor.value),gender:roomGender.value};if(!data.code||!data.building_code||!data.capacity||!data.floor){alert('Nhập đủ thông tin phòng.');return}try{await api('/rooms',{method:'POST',body:JSON.stringify(data)});alert('Đã thêm phòng và tạo giường.');hideRoomForm();await loadRooms()}catch(e){alert(e.message)}}

async function loadContracts(){
 const body=document.getElementById('contractBody'); if(!body)return;
 try{const rows=await api('/contracts');body.innerHTML=rows.length?rows.map(c=>`<tr><td>${escapeHtml(c.code)}</td><td>${escapeHtml(c.mssv)}</td><td>${escapeHtml(c.student)}</td><td>${escapeHtml(c.room_code)}</td><td>${c.start_date}</td><td>${c.end_date}</td><td>${escapeHtml(c.status)}</td></tr>`).join(''):'<tr><td colspan="7">Chưa có hợp đồng.</td></tr>'}catch(e){body.innerHTML=`<tr><td colspan="7">${escapeHtml(e.message)}</td></tr>`}
}
async function loadContractStudents(){const s=document.getElementById('contractStudent');if(!s)return;try{const rows=await api('/contracts/students');s.innerHTML='<option value="">-- Chọn sinh viên đã xếp phòng --</option>'+rows.map(x=>`<option value="${x.id}">${escapeHtml(x.mssv)} - ${escapeHtml(x.full_name)} (${escapeHtml(x.room)})</option>`).join('')}catch(e){s.innerHTML='<option>Không tải được</option>'}}
function showContractForm(){document.getElementById('contractForm').style.display='block';loadContractStudents()}
function hideContractForm(){document.getElementById('contractForm').style.display='none'}
async function createContract(){const data={student_id:Number(contractStudent.value),start_date:contractStart.value,end_date:contractEnd.value};if(!data.student_id||!data.start_date||!data.end_date){alert('Nhập đủ thông tin.');return}try{const r=await api('/contracts',{method:'POST',body:JSON.stringify(data)});alert('Đã tạo hợp đồng '+r.code);hideContractForm();loadContracts()}catch(e){alert(e.message)}}

async function loadFinance(){
 const summaryBox=document.getElementById('financeSummary');const body=document.getElementById('feeBody');if(!body)return;
 try{const s=await api('/finance/summary');if(summaryBox)summaryBox.innerHTML=`<div class="grid"><div class="card"><h3>Phải thu</h3><div class="number">${money(s.total)}</div></div><div class="card"><h3>Đã thu</h3><div class="number">${money(s.collected)}</div></div><div class="card"><h3>Công nợ</h3><div class="number">${money(s.debt)}</div></div><div class="card"><h3>Tỷ lệ thu</h3><div class="number">${s.collection_rate}%</div></div></div>`;const rows=await api('/finance/fees');body.innerHTML=rows.length?rows.map(f=>`<tr><td>${escapeHtml(f.mssv)}</td><td>${escapeHtml(f.student)}</td><td>${escapeHtml(f.room||'-')}</td><td>${f.month}</td><td>${money(f.amount)}</td><td>${f.due_date}</td><td>${escapeHtml(f.status)}</td><td>${f.status==='Chưa thu'?`<button class="btn btn-primary" onclick="payFee(${f.id})">Xác nhận thu</button>`:'-'}</td></tr>`).join(''):'<tr><td colspan="8">Chưa có khoản thu.</td></tr>'}catch(e){body.innerHTML=`<tr><td colspan="8">${escapeHtml(e.message)}</td></tr>`}
}
async function loadFeeStudents(){const s=document.getElementById('feeStudent');if(!s)return;try{const rows=await api('/students');s.innerHTML='<option value="">-- Chọn sinh viên --</option>'+rows.map(x=>`<option value="${x.id}">${escapeHtml(x.mssv)} - ${escapeHtml(x.full_name)}</option>`).join('')}catch(e){}}
function showFeeForm(){document.getElementById('feeForm').style.display='block';loadFeeStudents()}
function hideFeeForm(){document.getElementById('feeForm').style.display='none'}
async function createFee(){const data={student_id:Number(feeStudent.value),month:feeMonth.value,amount:Number(feeAmount.value),due_date:feeDueDate.value};if(!data.student_id||!data.month||!data.amount||!data.due_date){alert('Nhập đủ thông tin khoản thu.');return}try{await api('/finance/fees',{method:'POST',body:JSON.stringify(data)});alert('Đã tạo khoản thu.');hideFeeForm();loadFinance()}catch(e){alert(e.message)}}
async function payFee(id){if(!confirm('Xác nhận khoản thu này đã thanh toán?'))return;try{await api(`/finance/fees/${id}/pay`,{method:'PATCH'});loadFinance()}catch(e){alert(e.message)}}

async function loadComplaints(){const body=document.getElementById('complaintBody');if(!body)return;try{const rows=await api('/complaints');body.innerHTML=rows.length?rows.map(c=>`<tr><td>${escapeHtml(c.code)}</td><td>${escapeHtml(c.mssv)} - ${escapeHtml(c.student)}</td><td>${escapeHtml(c.content)}</td><td>${new Date(c.created_at).toLocaleDateString('vi-VN')}</td><td>${escapeHtml(c.status)}</td><td><button class="btn btn-secondary" onclick="changeComplaint(${c.id},'Đang xử lý')">Tiếp nhận</button> <button class="btn btn-primary" onclick="changeComplaint(${c.id},'Đã xử lý')">Đã xử lý</button></td></tr>`).join(''):'<tr><td colspan="6">Chưa có phản ánh.</td></tr>'}catch(e){body.innerHTML=`<tr><td colspan="6">${escapeHtml(e.message)}</td></tr>`}}
async function changeComplaint(id,status){try{await api(`/complaints/${id}/status`,{method:'PATCH',body:JSON.stringify({status})});loadComplaints()}catch(e){alert(e.message)}}

async function loadPolicies(){const body=document.getElementById('policyBody');if(!body)return;try{const rows=await api('/policies');body.innerHTML=rows.length?rows.map(p=>`<tr><td>${escapeHtml(p.code)}</td><td>${escapeHtml(p.title)}</td><td>${escapeHtml(p.content)}</td><td>${p.active?'Đang dùng':'Tắt'}</td><td><button class="btn btn-danger" onclick="deletePolicy(${p.id})">Xóa</button></td></tr>`).join(''):'<tr><td colspan="5">Chưa có nội quy. Hãy nhập nội quy thật của KTX.</td></tr>'}catch(e){body.innerHTML=`<tr><td colspan="5">${escapeHtml(e.message)}</td></tr>`}}
async function createPolicy(){const data={code:policyCode.value.trim(),title:policyTitle.value.trim(),content:policyContent.value.trim()};if(!data.code||!data.title||!data.content){alert('Nhập đủ nội quy.');return}try{await api('/policies',{method:'POST',body:JSON.stringify(data)});alert('Đã lưu nội quy thật vào database.');policyCode.value='';policyTitle.value='';policyContent.value='';loadPolicies()}catch(e){alert(e.message)}}
async function deletePolicy(id){if(!confirm('Xóa nội quy này?'))return;try{await api(`/policies/${id}`,{method:'DELETE'});loadPolicies()}catch(e){alert(e.message)}}

async function loadStats(){const box=document.getElementById('statsBox');if(!box)return;try{const s=await api('/stats');box.innerHTML=`<div class="grid"><div class="card"><h3>Sinh viên</h3><div class="number">${s.students}</div></div><div class="card"><h3>Phòng</h3><div class="number">${s.rooms}</div></div><div class="card"><h3>Công suất</h3><div class="number">${s.occupancy_rate}%</div></div><div class="card"><h3>Chờ duyệt</h3><div class="number">${s.pending_stays}</div></div><div class="card"><h3>Đã thu</h3><div class="number">${money(s.fees_collected)}</div></div><div class="card"><h3>Công nợ</h3><div class="number">${money(s.fees_debt)}</div></div><div class="card"><h3>Phản ánh</h3><div class="number">${s.complaints_total}</div></div><div class="card"><h3>Hợp đồng hiệu lực</h3><div class="number">${s.contracts_active}</div></div></div><div class="section"><h2>Báo cáo tổng hợp</h2><table><tr><th>Chỉ tiêu</th><th>Kết quả</th></tr><tr><td>Tỷ lệ lấp đầy</td><td>${s.occupancy_rate}%</td></tr><tr><td>Tỷ lệ thu phí</td><td>${s.collection_rate}%</td></tr><tr><td>Phản ánh đã xử lý</td><td>${s.complaints_done}/${s.complaints_total}</td></tr><tr><td>Chỗ trống</td><td>${s.available}/${s.capacity}</td></tr></table></div>`}catch(e){box.innerHTML=`<div class="notice">${escapeHtml(e.message)}</div>`}}


async function searchRooms(){const result=document.getElementById('roomResult');if(!result)return;try{const rows=await api('/rooms');const b=document.getElementById('searchBuilding')?.value||'Tất cả';const c=document.getElementById('searchCapacity')?.value||'Tất cả';const filtered=rows.filter(r=>(b==='Tất cả'||r.building===b)&&(c==='Tất cả'||r.capacity===Number(c))&&r.available>0);result.innerHTML=filtered.length?filtered.map(r=>`<tr><td>${escapeHtml(r.code)}</td><td>${escapeHtml(r.building)}</td><td>${r.capacity}</td><td>${r.occupied}</td><td>${r.available}</td><td>${escapeHtml(r.status)}</td></tr>`).join(''):'<tr><td colspan="6">Không có phòng phù hợp.</td></tr>'}catch(e){result.innerHTML=`<tr><td colspan="6">${escapeHtml(e.message)}</td></tr>`}}
async function loadSearchBuildings(){const s=document.getElementById('searchBuilding');if(!s)return;try{const rows=await api('/rooms/buildings');s.innerHTML='<option value="Tất cả">Tất cả</option>'+rows.map(x=>`<option value="${escapeHtml(x.code)}">${escapeHtml(x.code)} - ${escapeHtml(x.name)}</option>`).join('')}catch(e){}}

async function loadManagerHome(){const box=document.getElementById('homeStats');if(!box)return;try{const s=await api('/stats');box.innerHTML=`<div class="grid"><div class="card"><h3>Tổng phòng</h3><div class="number">${s.rooms}</div></div><div class="card"><h3>Sinh viên</h3><div class="number">${s.students}</div></div><div class="card"><h3>Đang ở</h3><div class="number">${s.occupied}</div></div><div class="card"><h3>Chờ duyệt</h3><div class="number">${s.pending_stays}</div></div></div>`}catch(e){}}

async function initManager(){await requireRole('quanly');await loadStays();await loadStudents();await loadRooms();await loadBuildings();await loadContracts();await loadFinance();await loadComplaints();await loadPolicies();await loadStats();await loadManagerHome();await loadSearchBuildings();}
document.addEventListener('DOMContentLoaded',initManager);
