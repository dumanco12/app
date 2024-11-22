document.getElementById('gerar-qr').addEventListener('click', function() {
  // Obter os valores dos campos de entrada
  var nomeCaixa = document.getElementById('nome-caixa').value.trim();
  var numeroNota = document.getElementById('numero-nota').value.trim();
  var conteudo = document.getElementById('conteudo').value.trim();

  // Verificar se os campos estão preenchidos
  if (!nomeCaixa || !numeroNota || !conteudo) {
    alert('Por favor, preencha todos os campos!');
    return;
  }

  // Montar o texto do QR Code
  var dadosQRCode = `
    Caixa Fracionada: \n\n
	${nomeCaixa}\n\n
    Nota Fiscal: \n\n
	${numeroNota}\n\n
    Conteúdo da Caixa:\n\n
	${conteudo}
  `;

  // Limpar o container do QR Code
  var qrcodeContainer = document.getElementById('qrcode-container');
  qrcodeContainer.innerHTML = ''; // Limpar conteúdo anterior

  try {
    // Gerar o QR Code usando a biblioteca qrcode.js
    QRCode.toCanvas(qrcodeContainer, dadosQRCode, { width: 200 }, function(error) {
      if (error) {
        console.error(error);
        alert('Erro ao gerar o QR Code!');
      } else {
        qrcodeContainer.style.display = 'block'; // Mostrar o QR Code gerado
      }
    });
  } catch (error) {
    console.error(error);
    alert('Ocorreu um erro ao gerar o QR Code.');
  }
});
