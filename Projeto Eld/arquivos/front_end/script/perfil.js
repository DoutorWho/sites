document.addEventListener('DOMContentLoaded', function() {
    var fotoElement = document.getElementById('foto');
    if (fotoElement) {
        fotoElement.addEventListener('change', function(e) {
            var file = e.target.files[0];
            var fileType = file["type"];
            var validImageTypes = ["image/jpeg", "image/png"];
            if (!validImageTypes.includes(fileType)) {
                alert("Erro: Por favor, carregue um arquivo .png ou .jpg!");
                return;
            }
            var reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('preview').src = e.target.result;
                document.getElementById('upload-text').style.display = 'none';
            }
            reader.readAsDataURL(file);
        });
    }

    var formElement = document.getElementById('meuformulario');
    if (formElement) {
        formElement.addEventListener('submit', function(e) {
            e.preventDefault();  // Impede o envio do formulário imediatamente

            var status = document.getElementById('status_conta').value;
            if (status == 'excluir') {
                if (confirm('Você realmente deseja excluir a conta?')) {
                    formElement.submit();  // Permite o envio do formulário
                }
            } else if (status == 'sair') {
                if (confirm('Você realmente deseja sair da conta?')) {
                    formElement.submit();  // Permite o envio do formulário
                }
            } else {
                formElement.submit();  // Permite o envio do formulário para outras opções
            }
        });
    }
});


window.addEventListener('DOMContentLoaded', () => {
    const notificationCount = document.querySelector('.notification-count');
    const notificationIcon = document.querySelector('.notification-icon');
    const notificationMessage = document.querySelector('.notification-span');
    let count = parseInt(document.querySelector('.notification-count').textContent);
    // Atualize o contador
    function updateNotificationCount(newCount) {
        count = newCount;
        notificationCount.textContent = count;
        if (count > 0) {
            notificationMessage.textContent = 'Novas notificações!';
            notificationCount.style.animation = 'blink 1s infinite';
            notificationIcon.style.animation = 'blink 1s infinite';
            notificationIcon.style.animation = 'shake 2s infinite alternate';
        } else {
            notificationMessage.textContent = 'Sem notificações!';
            notificationCount.style.animation = 'none';
            notificationIcon.style.animation = 'none';
            notificationIcon.style.animation = 'none';
        }
    }
    updateNotificationCount(count);
});
function mostrarIframe() {
    const meuIframe = document.getElementById("meuIframe");
    if (meuIframe.style.display === "none" ) {
        meuIframe.style.display = "block";
    } else {
        meuIframe.style.display = "none";
    }
}