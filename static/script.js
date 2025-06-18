
function mostrarProgresso() {
    const barra = document.getElementById("barra");
    const barraInterna = document.querySelector(".progress-bar-fill");
    barra.style.display = "block";
    barraInterna.style.width = "0%";

    let largura = 0;
    const intervalo = setInterval(() => {
        if (largura >= 100) {
            clearInterval(intervalo);
        } else {
            largura += 1;
            barraInterna.style.width = largura + "%";
        }
    }, 30);
}

// Reprodução de som ao finalizar (quando áudio aparecer)
document.addEventListener("DOMContentLoaded", () => {
    const player = document.querySelector("audio");
    if (player) {
        const audioFx = new Audio("/static/sucesso.mp3");
        audioFx.play();
    }
});
