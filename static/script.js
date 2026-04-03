const insertForm = document.getElementById("insertForm");
const getForm = document.getElementById("getForm");
const updateForm = document.getElementById("updateForm");
const deleteForm = document.getElementById("deleteForm");

function showOutput(data){
    const outputCard = document.getElementById("outputCard");
    const tableBody = document.getElementById("outputTableBody");
    tableBody.innerHTML="";
    if(data.id && data.name!==undefined){
        const row = document.createElement("tr");
        const idCell = document.createElement("td"); idCell.textContent=data.id;
        const nameCell = document.createElement("td"); nameCell.textContent=data.name;
        row.appendChild(idCell); row.appendChild(nameCell);
        tableBody.appendChild(row);
    }else{
        tableBody.innerHTML=`<tr><td colspan="2">${data.message}</td></tr>`;
    }
    outputCard.style.display="block";
}

insertForm.addEventListener("submit", async e=>{
    e.preventDefault();
    const id=e.target.id.value, name=e.target.name.value;
    const res=await fetch("/insert",{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({id:parseInt(id), name})});
    const data=await res.json(); showOutput(data);
});

getForm.addEventListener("submit", async e=>{
    e.preventDefault();
    const id=e.target.id.value;
    const res=await fetch(`/get/${id}`);
    const data=await res.json(); showOutput(data);
});

updateForm.addEventListener("submit", async e=>{
    e.preventDefault();
    const id=e.target.id.value, name=e.target.name.value;
    const res=await fetch(`/update/${id}`,{method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify({name})});
    const data=await res.json(); showOutput(data);
});

deleteForm.addEventListener("submit", async e=>{
    e.preventDefault();
    const id=e.target.id.value;
    const res=await fetch(`/delete/${id}`,{method:"DELETE"});
    const data=await res.json(); showOutput(data);
});
