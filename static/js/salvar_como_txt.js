
document.addEventListener("DOMContentLoaded", function () {
    const botaoSalvar = document.getElementById("botao-salvar");
    const campoTexto = document.querySelector("textarea");
    let ultimoTextoSalvo = "";

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

    // Salvamento automático quando há mudanças significativas no texto
    let timeoutSalvamento = null;
    
    campoTexto.addEventListener("input", () => {
        const textoAtual = campoTexto.value.trim();
        
        // Limpar timeout anterior
        if (timeoutSalvamento) {
            clearTimeout(timeoutSalvamento);
        }
        
        // Salvar automaticamente após 5 segundos de inatividade
        // Apenas se o texto mudou significativamente (mais de 10 caracteres)
        timeoutSalvamento = setTimeout(() => {
            if (textoAtual && 
                textoAtual.length > 10 && 
                Math.abs(textoAtual.length - ultimoTextoSalvo.length) > 10) {
                
                console.log("Preparando salvamento automático...");
                ultimoTextoSalvo = textoAtual;
                
                // Mostrar indicação de salvamento automático
                const indicacao = document.createElement("div");
                indicacao.innerHTML = "💾 Texto salvo automaticamente!";
                indicacao.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    z-index: 1000;
                    font-size: 14px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                `;
                
                document.body.appendChild(indicacao);
                
                // Salvar arquivo automaticamente
                salvarTexto(textoAtual, `vozear_auto_${Date.now()}.txt`);
                
                // Remover indicação após 3 segundos
                setTimeout(() => {
                    if (indicacao.parentNode) {
                        indicacao.parentNode.removeChild(indicacao);
                    }
                }, 3000);
            }
        }, 5000);
    });

    // Função global para salvamento de emergência (pode ser chamada de qualquer lugar)
    window.salvarTextoEmergencia = function() {
        const conteudo = campoTexto.value.trim();
        if (conteudo) {
            salvarTexto(conteudo, `vozear_emergencia_${Date.now()}.txt`);
            console.log("Texto salvo em emergência");
        }
    };

    console.log("Sistema de salvamento de texto inicializado");
    console.log("- Salvamento manual: Clique no botão 💾");
    console.log("- Salvamento automático: A cada mudança significativa");
    console.log("- Salvamento de emergência: window.salvarTextoEmergencia()");
});
