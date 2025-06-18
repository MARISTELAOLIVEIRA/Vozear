
document.addEventListener("DOMContentLoaded", function () {
    const botaoFalar = document.getElementById("botao-falar");
    const botaoParar = document.getElementById("botao-parar");
    const campoTexto = document.querySelector("textarea");

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        botaoFalar.disabled = true;
        botaoFalar.innerText = "Reconhecimento não suportado";
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = "pt-BR";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    botaoFalar.addEventListener("click", () => {
        botaoFalar.style.display = "none";
        botaoParar.style.display = "inline-block";
        botaoParar.innerText = "🛑 Parar";
        recognition.start();
    });

    botaoParar.addEventListener("click", () => {
        recognition.stop();
        botaoParar.innerText = "🛑 Encerrando...";
    });

    recognition.onresult = (event) => {
        const texto = event.results[0][0].transcript;
        campoTexto.value += (campoTexto.value ? " " : "") + texto;
    };

    recognition.onerror = (event) => {
        console.error("Erro no reconhecimento de voz:", event.error);
    };

    recognition.onend = () => {
        botaoFalar.style.display = "inline-block";
        botaoFalar.innerText = "🎤 Falar";
        botaoParar.style.display = "none";
    };
});
