# SkySquidyGame 

Jogo de plataforma 2D feito com Pygame Zero. Controle Squiddy, um alienígena veloz, para coletar moedas no céu e voltar para casa!

## Visão Geral do Jogo
- **Gênero**: Plataforma 2D
- **Engine**: Pygame Zero (usando módulos `Rect`, `math` e `random`)
- **Objetivo**: Colete 100 moedas enquanto evade de inimigos. O valor das moedas aumenta conforme seu progresso.

## Funcionalidades
- **Pontuação dinâmica das moedas**:
  - 1 ponto por moeda (até 10 moedas)
  - 2 pontos por moeda (10–50 moedas)
  - 3 pontos por moeda (50–100 moedas)
- **Inimigos**: Aparecem após coletar 5 moedas. Toque neles e o jogo termina!
- **Menu** com navegação por teclado ou mouse.
- **Vitória**: Alcance 100+ pontos para finalizar o jogo.

## Controles
- **Durante o Jogo**:
  - `ESPAÇO`: Pular
  - `SETAS ESQUERDA/DIREITA`: Movimentar no ar ou no chão
  - `ESC` (após vencer): Voltar ao menu
- **Menu**:
  - `SETAS CIMA/BAIXO` + `ENTER`: Navegar
  - `Clique do Mouse`: Selecionar itens

## Recursos & Créditos
- **Música**: *Friends* por Patrick de Arteaga ([licença livre de royalties](https://patrickdearteaga.com/en/royalty-free-music/))
- **Efeitos Sonoros**:
  - Som de moeda do [Mixkit](https://mixkit.co/free-sound-effects/coin/)
  - Sons personalizados criados no [BeepBox](https://www.beepbox.co/)
- **Artes Visuais**: Sprites do pacote *Pixel Platformer* da [Kenney](https://kenney.nl/assets/pixel-platformer)

## Aviso Legal
Todo o conteúdo é **apenas para fins educacionais e não comerciais**. Desenvolvido como projeto de aprendizado e demonstração técnica.

---

**Como Jogar**:  
Clone o repositório e execute o jogo usando Pygame Zero. Certifique-se de ter as dependências instaladas (`pgzero`, `pygame`).
