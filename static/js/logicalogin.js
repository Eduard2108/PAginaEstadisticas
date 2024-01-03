function registerUser() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
  
    // En un entorno real, esta información debería enviarse al servidor para su procesamiento y almacenamiento seguro.
    // Aquí se muestra un ejemplo de cómo podrías realizar una solicitud AJAX a un servidor.
  
    // En este caso, se utiliza la función fetch() para hacer una solicitud POST a un servidor (puedes cambiar la URL según tus necesidades).
    fetch('http://tu-servidor.com/registrar-usuario', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: username, password: password }),
    })
    .then(response => response.json())
    .then(data => {
      // Aquí puedes manejar la respuesta del servidor, por ejemplo, mostrar un mensaje de éxito o error.
      console.log('Respuesta del servidor:', data);
    })
    .catch((error) => {
      console.error('Error al enviar datos al servidor:', error);
    });
  }
  