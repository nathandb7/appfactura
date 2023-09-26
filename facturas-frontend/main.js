import javascriptLogo from './javascript.svg'

let form = document.querySelector('#login')


form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  formData.append('grant_type', 'password'); // Agrega grant_type
  const username = formData.get('username');
  const password = formData.get('password');

  try {
    const response = await fetch('/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams(formData).toString(), // Convierte los datos a form-urlencoded
    });

    // console.log(response);

    if (response.ok) {
      // La solicitud fue exitosa, maneja la respuesta aquí
      const tokenData = await response.json();
      console.log('Token recibido:', tokenData.access_token);
      // Guardar Session storage
      sessionStorage.setItem('token', tokenData.access_token);
      window.location.href = 'bloqueado.html';

    } else if (response.status === 422) {
      // La solicitud falló, maneja los errores aquí
      const errorData = await response.json();
      console.log(errorData);
      console.error('Error en la solicitud:', errorData.detail[0].msg);
      // Muestra un mensaje de error al usuario
    } else if (response.status === 401) {
      // La solicitud falló, maneja los errores aquí
      const errorData = await response.json();
      console.log(errorData);
      console.error('Error no autorizado:', errorData.detail);
      // Muestra un mensaje de error al usuario
    }
  } catch (error) {
    console.error('Error:', error);
  }
});
