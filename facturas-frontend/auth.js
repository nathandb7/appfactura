const token = sessionStorage.getItem('token');
if (!token) {
    window.location.href = '/index.html'; // Redirecciona al usuario no autenticado a la página de inicio
}

const app = document.querySelector('#app');

// Función para realizar la solicitud a la API de usuario
async function fetchUserData() {
    try {
        const response = await fetch('/api/users/me', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            },
        });

        if (response.ok) {
            const userData = await response.json();
            console.log('Usuario:', userData);
            // Realiza acciones con los datos del usuario aquí
            const userParagraph = document.createElement('p');
            userParagraph.textContent = `A ingresado correctamente, ${userData.username} (${userData.email})`;
            app.appendChild(userParagraph);
        } else if (response.status === 401) {
            // Token expirado o no válido, redirecciona al usuario a la página de inicio
            window.location.href = '/index.html';
        } else {
            // Maneja otros errores de la API de acuerdo a tus necesidades
            console.error('Error en la solicitud:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Llama a la función para realizar la solicitud a la API de usuario
fetchUserData();
