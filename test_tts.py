#!/usr/bin/env python3
import asyncio
import edge_tts
import os

async def test_tts():
    try:
        texto = "Este é um teste simples"
        voice = "pt-BR-AntonioNeural"
        rate = "+0%"
        
        communicate = edge_tts.Communicate(texto, voice, rate=rate)
        await communicate.save("audio/teste.mp3")
        print("Teste de TTS concluído com sucesso!")
        
    except Exception as e:
        print(f"Erro no teste TTS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tts())
