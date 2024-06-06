document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('foto').addEventListener('change', function(e) {
        var file = e.target.files[0];
        var fileType = file["type"];
        var validImageTypes = ["image/jpeg", "image/png"];
        if (!validImageTypes.includes(fileType)) {
            alert("Por favor, carregue um arquivo .png ou .jpg!");
            return;
        }
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview').src = e.target.result;
            document.getElementById('upload-text').style.display = 'none';
        }
        reader.readAsDataURL(file);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    function ValidarNome() {
        document.querySelector('form').addEventListener('submit', function(event) {
            var nome = document.getElementById("nome_perfil").value;
            // Verificação se contém letras maiúsculas, espaços ou símbolos
            var regex = /^[a-z0-9]+$/;
            if (!regex.test(nome)) {
                alert('O nome não pode conter letras maiúsculas, espaços ou símbolos!');
                event.preventDefault();
            }
        });
    }
    // Chama a função para adicionar o event listener ao formulário
    ValidarNome();
});


