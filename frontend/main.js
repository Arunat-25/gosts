let ws = new WebSocket("ws://87.228.102.121:8001/");
ws.onmessage = function(event) {
    let data = JSON.parse(event.data);
    let elementDivFiles = document.getElementById("files");
    elementDivFiles.innerHTML = "";

    for (let i = 0; i < data.files.length; i++) {
        const binaryString = atob(data.files[i].content);
        const byteArray = new Uint8Array(binaryString.length);
        for (let j = 0; j < binaryString.length; j++) {
            byteArray[j] = binaryString.charCodeAt(j);
        }
        const fileName = data.files[i].name;
        elementDivFiles.insertAdjacentHTML("beforeend",
            `<div id='file${i}'>
                    <a href='#' class="file-link" data-filename="${fileName}">${fileName}</a>
                  </div>`
        );

        // Обработчик клика для скачивания
        document.querySelector(`#file${i} a`).addEventListener('click', function(e) {
            e.preventDefault();
            const blob = new Blob([byteArray], {type: 'application/pdf'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            a.click();
            setTimeout(() => URL.revokeObjectURL(url), 100);
        });
    }
};

document.getElementById("send-text").addEventListener("click", function (event){
    let inputElement = document.getElementById("input-text");
    let text = inputElement.value;
    ws.send(JSON.stringify({"text": text}));
    inputElement.value = "";
});
