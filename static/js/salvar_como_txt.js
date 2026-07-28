
document.addEventListener("DOMContentLoaded", function () {
    const botaoSalvar = document.getElementById("botao-salvar");
    const campoTexto = document.querySelector("textarea");

    // Função para gerar nome de arquivo com timestamp
    function gerarNomeArquivo() {
        const agora = new Date();
        const dataHora = agora.toLocaleString("pt-BR", {
            year: "numeric",
            month: "2-digit", 
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }).replace(/[/:\s]/g, "_");
        
        return `vozear_transcricao_${dataHora}.txt`;
    }

    // Função para salvar arquivo
    function salvarTexto(conteudo, nomeArquivo = null) {
        if (!conteudo.trim()) {
            return false;
        }

        // Adicionar cabeçalho com informações
        const cabecalho = `Transcrição gerada pelo Vozear
Data/Hora: ${new Date().toLocaleString("pt-BR")}
Acessibilidade Digital - Maristela Oliveira
========================================

`;
        
        const conteudoCompleto = cabecalho + conteudo.trim();
        
        const blob = new Blob([conteudoCompleto], { type: "text/plain;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = nomeArquivo || gerarNomeArquivo();
        
        // Para navegadores que precisam adicionar ao DOM
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(link.href);
        return true;
    }

    // Salvamento manual pelo botão
    botaoSalvar.addEventListener("click", () => {
        const conteudo = campoTexto.value.trim();
        if (!conteudo) {
            alert("📝 O campo de texto está vazio. Fale algo primeiro ou digite o texto!");
            return;
        }

        if (salvarTexto(conteudo)) {
            // Feedback visual
            const textoOriginal = botaoSalvar.innerText;
            botaoSalvar.innerText = "✅ Salvo!";
            botaoSalvar.style.backgroundColor = "#4CAF50";
            
            setTimeout(() => {
                botaoSalvar.innerText = textoOriginal;
                botaoSalvar.style.backgroundColor = "";
            }, 2000);
            
            console.log("Arquivo salvo manualmente");
        }
    });

    console.log("Sistema de salvamento de texto inicializado");
    console.log("- Salvamento manual: Clique no botão 💾");
});
