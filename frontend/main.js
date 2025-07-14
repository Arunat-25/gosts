let ws = new WebSocket("ws://87.228.102.121:8001/api/");
ws.onmessage = function(event) {
    let data = JSON.parse(event.data);

    let elementDivFiles;
    if (data.its_search === true){
        elementDivFiles = document.getElementById("filesAfterRequest");
        document.getElementById("files").innerHTML = "";
    }
    else{
        elementDivFiles = document.getElementById("files");
        document.getElementById("filesAfterRequest").innerHTML = "";
    }

    const binaryString = atob(data.file.content);
    const byteArray = new Uint8Array(binaryString.length);
    for (let j = 0; j < binaryString.length; j++) {
        byteArray[j] = binaryString.charCodeAt(j);
    }
    const fileName = data.file.name;
    elementDivFiles.insertAdjacentHTML("beforeend",
        `<div id='file${data.number}'>
                   <a href='#' class="file-link" data-filename="${fileName}">${fileName}</a>
              </div>`
    );

    // Обработчик клика для скачивания
    document.querySelector(`#file${data.number} a`).addEventListener('click', function(e) {
        e.preventDefault();
        const blob = new Blob([byteArray], {type: 'application/pdf'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 100);
    });
};

document.getElementById("send-text").addEventListener("click", function (event){
    let inputElement = document.getElementById("input-text");
    let text = inputElement.value;
    ws.send(JSON.stringify({"text": text}));
    inputElement.value = "";
});
