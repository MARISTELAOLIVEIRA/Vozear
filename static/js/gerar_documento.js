document.addEventListener("DOMContentLoaded", function() {
    const campoTexto = document.querySelector("textarea");
    const botaoLimpar = document.getElementById("limpar");
    
    // Função para gerar documento final
    function gerarDocumentoFinal() {
        const conteudo = campoTexto.value.trim();
        
        if (!conteudo || conteudo.length < 10) {
            alert("⚠️ É necessário ter pelo menos 10 caracteres para gerar um documento.");
            return;
        }

        // Estatísticas do texto
        const palavras = conteudo.split(/\s+/).filter(word => word.length > 0).length;
        const caracteres = conteudo.length;
        const paragrafos = conteudo.split(/\n\s*\n/).filter(p => p.trim().length > 0).length;
        
        // Estimar tempo de leitura (média de 200 palavras por minuto)
        const tempoLeitura = Math.ceil(palavras / 200);
        
        // Cabeçalho completo do documento
        const cabecalho = `DOCUMENTO GERADO PELO VOZEAR
============================================

📋 INFORMAÇÕES DO DOCUMENTO:
• Data/Hora de criação: ${new Date().toLocaleString("pt-BR")}
• Palavras: ${palavras}
• Caracteres: ${caracteres}
• Parágrafos: ${paragrafos}
• Tempo estimado de leitura: ${tempoLeitura} minuto${tempoLeitura > 1 ? 's' : ''}

🎧 Sistema de Acessibilidade Digital
Desenvolvido por: Maristela Oliveira
Projeto: Vozear - Transforme Palavras em Experiências Sonoras

============================================

CONTEÚDO:

`;

        const documentoCompleto = cabecalho + conteudo;
        
        // Criar arquivo
        const blob = new Blob([documentoCompleto], { type: "text/plain;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        
        // Nome do arquivo com data e hora
        const agora = new Date();
        const nomeArquivo = `Documento_Vozear_${agora.toLocaleDateString("pt-BR").replace(/\//g, "-")}_${agora.toLocaleTimeString("pt-BR").replace(/:/g, "-")}.txt`;
        link.download = nomeArquivo;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
        
        // Mostrar confirmação visual
        mostrarConfirmacao(`📄 Documento "${nomeArquivo}" gerado com sucesso!`);
        
        // Oferecer para limpar o campo após salvamento
        setTimeout(() => {
            if (confirm("🗑️ Deseja limpar o campo de texto para iniciar um novo documento?")) {
                campoTexto.value = "";
                campoTexto.focus();
                console.log("Campo limpo para novo documento");
            }
        }, 2000);
        
        console.log(`Documento final gerado: ${palavras} palavras, ${caracteres} caracteres`);
    }
    
    // Função para mostrar confirmação visual
    function mostrarConfirmacao(mensagem) {
        const confirmacao = document.createElement("div");
        confirmacao.innerHTML = mensagem;
        confirmacao.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 20px 30px;
            border-radius: 10px;
            z-index: 2000;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 5px 25px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
            animation: fadeInOut 4s ease-in-out;
        `;
        
        // Adicionar animação CSS
        const style = document.createElement("style");
        style.textContent = `
            @keyframes fadeInOut {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                15% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                85% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(confirmacao);
        
        setTimeout(() => {
            if (confirmacao.parentNode) {
                confirmacao.parentNode.removeChild(confirmacao);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 4000);
    }
    
    // Criar botão para gerar documento final
    const botaoGerarDoc = document.createElement("button");
    botaoGerarDoc.innerHTML = "📄 Gerar Documento Final";
    botaoGerarDoc.id = "gerar-documento";
    botaoGerarDoc.style.cssText = `
        background: linear-gradient(135deg, #2196F3, #1976D2);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        margin: 10px 5px;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.3);
    `;
    
    botaoGerarDoc.addEventListener("mouseenter", () => {
        botaoGerarDoc.style.transform = "translateY(-2px)";
        botaoGerarDoc.style.boxShadow = "0 5px 15px rgba(33, 150, 243, 0.4)";
    });
    
    botaoGerarDoc.addEventListener("mouseleave", () => {
        botaoGerarDoc.style.transform = "translateY(0)";
        botaoGerarDoc.style.boxShadow = "0 3px 10px rgba(33, 150, 243, 0.3)";
    });
    
    botaoGerarDoc.addEventListener("click", gerarDocumentoFinal);
    
    // Inserir o botão após o botão de limpar
    if (botaoLimpar && botaoLimpar.parentNode) {
        botaoLimpar.parentNode.insertBefore(botaoGerarDoc, botaoLimpar.nextSibling);
    }
    
    // Função global para acesso rápido
    window.gerarDocumentoFinal = gerarDocumentoFinal;
    
    // Atalho de teclado: Ctrl+D para gerar documento
    document.addEventListener("keydown", (event) => {
        if (event.ctrlKey && event.key === 'd') {
            event.preventDefault();
            gerarDocumentoFinal();
        }
    });
    
    console.log("Sistema de geração de documentos inicializado");
    console.log("- Botão: 📄 Gerar Documento Final");
    console.log("- Atalho: Ctrl+D");
    console.log("- Função global: window.gerarDocumentoFinal()");
});
