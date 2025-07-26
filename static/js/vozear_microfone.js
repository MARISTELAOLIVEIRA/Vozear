
document.addEventListener("DOMContentLoaded", function () {
    const botaoFalar = document.getElementById("botao-falar");
    const botaoParar = document.getElementById("botao-parar");
    const campoTexto = document.querySelector("textarea");
    let isRecording = false;
    let timeoutId = null;

    console.log("Inicializando reconhecimento de voz...");

    // Verificar suporte do navegador
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        console.error("Reconhecimento de voz não suportado neste navegador");
        botaoFalar.disabled = true;
        botaoFalar.innerText = "❌ Reconhecimento não suportado";
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    // Configurações para reconhecimento contínuo e inteligente
    recognition.lang = "pt-BR";
    recognition.interimResults = true;  // Mostrar resultados parciais
    recognition.continuous = true;      // Reconhecimento contínuo
    recognition.maxAlternatives = 1;

    console.log("Reconhecimento configurado para modo contínuo");

    // Colocar foco automaticamente na caixa de texto
    campoTexto.focus();
    console.log("Foco definido na caixa de texto");

    function iniciarReconhecimento() {
        if (isRecording) return;
        
        isRecording = true;
        botaoFalar.style.display = "none";
        botaoParar.style.display = "inline-block";
        botaoParar.innerText = "🛑 Parar";
        
        try {
            recognition.start();
            console.log("Reconhecimento iniciado");
        } catch (error) {
            console.error("Erro ao iniciar reconhecimento:", error);
            pararReconhecimento();
        }
    }

    function pararReconhecimento() {
        isRecording = false;
        if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
        
        try {
            recognition.stop();
        } catch (error) {
            console.log("Reconhecimento já estava parado");
        }
        
        botaoFalar.style.display = "inline-block";
        botaoFalar.innerText = "🎤 Falar";
        botaoParar.style.display = "none";
        console.log("Reconhecimento parado");
    }

    // Função para definir timeout de silêncio
    function definirTimeoutSilencio() {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        
        // Para automaticamente após 3 segundos de silêncio
        timeoutId = setTimeout(() => {
            console.log("Timeout de silêncio atingido - parando reconhecimento");
            pararReconhecimento();
        }, 3000);
    }

    botaoFalar.addEventListener("click", iniciarReconhecimento);
    botaoParar.addEventListener("click", pararReconhecimento);

    recognition.onstart = () => {
        console.log("Reconhecimento iniciado com sucesso");
        botaoParar.innerText = "� Gravando... (Fale agora)";
        definirTimeoutSilencio();
    };

    recognition.onresult = (event) => {
        console.log("Resultado recebido:", event);
        
        // Resetar timeout quando há nova fala
        definirTimeoutSilencio();
        
        let textoFinal = "";
        let textoInterino = "";
        
        // Processar todos os resultados
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                textoFinal += transcript;
                console.log("Texto final:", transcript);
            } else {
                textoInterino += transcript;
                console.log("Texto interino:", transcript);
            }
        }
        
        // Adicionar apenas texto final ao campo
        if (textoFinal) {
            campoTexto.value += (campoTexto.value ? " " : "") + textoFinal;
            console.log("Texto adicionado ao campo:", textoFinal);
            
            // Mostrar feedback visual
            botaoParar.innerText = "✅ Texto capturado! (Continue falando)";
            setTimeout(() => {
                if (isRecording) {
                    botaoParar.innerText = "🔴 Gravando... (Fale agora)";
                }
            }, 1000);
        }
    };

    recognition.onerror = (event) => {
        console.error("Erro no reconhecimento de voz:", event.error);
        
        let mensagemErro = "Erro no reconhecimento";
        switch(event.error) {
            case 'no-speech':
                console.log("Nenhuma fala detectada - continuando...");
                return; // Não parar por falta de fala
            case 'audio-capture':
                mensagemErro = "❌ Erro no microfone";
                break;
            case 'not-allowed':
                mensagemErro = "❌ Permissão negada para microfone";
                break;
            case 'network':
                mensagemErro = "❌ Erro de rede";
                break;
            case 'aborted':
                console.log("Reconhecimento foi interrompido pelo usuário");
                return;
        }
        
        botaoParar.innerText = mensagemErro;
        setTimeout(() => {
            pararReconhecimento();
        }, 2000);
    };

    recognition.onend = () => {
        console.log("Reconhecimento finalizado");
        
        // Pedir para salvar quando o reconhecimento termina por timeout (parou de falar)
        const textoAtual = campoTexto.value.trim();
        if (textoAtual.length > 10 && !isRecording) {
            console.log("Pessoa parou de falar - pedindo para salvar arquivo");
            setTimeout(() => {
                if (typeof window.salvarTextoEmergencia === 'function') {
                    window.salvarTextoEmergencia();
                }
            }, 500);
        }
        
        if (isRecording) {
            // Se ainda estamos gravando mas o reconhecimento parou, reiniciar
            console.log("Reiniciando reconhecimento automaticamente...");
            setTimeout(() => {
                if (isRecording) {
                    try {
                        recognition.start();
                    } catch (error) {
                        console.log("Não foi possível reiniciar, parando...");
                        pararReconhecimento();
                    }
                }
            }, 100);
        } else {
            pararReconhecimento();
        }
    };
});
