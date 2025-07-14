
document.addEventListener("DOMContentLoaded", function () {
    const botaoSalvar = document.getElementById("botao-salvar");
    const campoTexto = document.querySelector("textarea");

    botaoSalvar.addEventListener("click", () => {
        const conteudo = campoTexto.value.trim();
        if (!conteudo) {
            alert("O campo de texto está vazio.");
            return;
        }

        const blob = new Blob([conteudo], { type: "text/plain;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "vozear_transcricao.txt";
        link.click();
        URL.revokeObjectURL(link.href);
    });
});
