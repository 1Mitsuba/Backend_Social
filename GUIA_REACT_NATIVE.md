# Guía de Integración Backend con React Native / Expo

## 🔐 Sistema de Autenticación

### Configuración de Tokens
- **Access Token**: 30 días (43,200 minutos)
- **Refresh Token**: 90 días
- **Algoritmo**: HS256
- **Header**: `Authorization: Bearer <token>`

---

## 📱 Endpoints de Autenticación

### 1. Registro (`POST /api/v1/auth/register`)

```javascript
const registro = async (userData) => {
  const response = await fetch('http://tu-backend.com/api/v1/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      nombre: userData.nombre,
      apellido: userData.apellido,
      correo: userData.correo,
      contrasena: userData.contrasena,
      rol: 'estudiante' // o 'docente', 'administrador'
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Guardar tokens
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
    return data;
  } else {
    throw new Error(data.detail || 'Error en el registro');
  }
};
```

### 2. Login (`POST /api/v1/auth/login`)

```javascript
const login = async (correo, contrasena) => {
  // Importante: OAuth2PasswordRequestForm espera 'username' y 'password'
  const formData = new FormData();
  formData.append('username', correo); // Nota: 'username' es el correo
  formData.append('password', contrasena);
  
  const response = await fetch('http://tu-backend.com/api/v1/auth/login', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Guardar tokens y usuario
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
    return data;
  } else {
    throw new Error(data.detail || 'Credenciales incorrectas');
  }
};
```

### 3. Refresh Token (`POST /api/v1/auth/refresh`)

```javascript
const refreshAccessToken = async () => {
  const refreshToken = await AsyncStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    throw new Error('No hay refresh token');
  }
  
  const response = await fetch('http://tu-backend.com/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Actualizar tokens
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
    return data.access_token;
  } else {
    // Refresh token expirado - cerrar sesión
    await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
    throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
  }
};
```

### 4. Validar Token (`POST /api/v1/auth/validate-token`)

**Útil para debugging**

```javascript
const validateToken = async () => {
  const token = await AsyncStorage.getItem('access_token');
  
  const response = await fetch('http://tu-backend.com/api/v1/auth/validate-token', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  console.log('Token info:', data);
  
  if (data.valid) {
    console.log(`Token expira en ${data.expires_in_days} días`);
  } else {
    console.error('Token inválido:', data.error);
  }
  
  return data;
};
```

---

## 🔄 Interceptor de Requests (Axios)

```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const api = axios.create({
  baseURL: 'http://tu-backend.com/api/v1',
  timeout: 30000,
});

// Request interceptor - agregar token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - manejar token expirado
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Si el token expiró y no hemos intentado refresh aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Intentar refresh
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        
        const response = await axios.post(
          'http://tu-backend.com/api/v1/auth/refresh',
          { refresh_token: refreshToken }
        );
        
        const { access_token, refresh_token: newRefreshToken } = response.data;
        
        // Guardar nuevos tokens
        await AsyncStorage.setItem('access_token', access_token);
        await AsyncStorage.setItem('refresh_token', newRefreshToken);
        
        // Reintentar request original con nuevo token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // Refresh falló - cerrar sesión
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
        // Navegar a login
        // navigation.navigate('Login');
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

---

## 📦 Servicio de Autenticación Completo

```javascript
// authService.js
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api'; // El interceptor de arriba

class AuthService {
  async login(correo, contrasena) {
    const formData = new FormData();
    formData.append('username', correo);
    formData.append('password', contrasena);
    
    const response = await fetch(`${api.defaults.baseURL}/auth/login`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
      await this.saveTokens(data);
      return data.user;
    } else {
      throw new Error(data.detail || 'Error al iniciar sesión');
    }
  }
  
  async register(userData) {
    const response = await api.post('/auth/register', userData);
    await this.saveTokens(response.data);
    return response.data.user;
  }
  
  async logout() {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
  }
  
  async saveTokens(data) {
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
  }
  
  async getUser() {
    const userStr = await AsyncStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
  
  async isAuthenticated() {
    const token = await AsyncStorage.getItem('access_token');
    return !!token;
  }
  
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      await AsyncStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('Error obteniendo usuario actual:', error);
      throw error;
    }
  }
}

export default new AuthService();
```

---

## 🧪 Testing de Tokens

### Con curl:

```bash
# Login
curl -X POST http://tu-backend.com/api/v1/auth/login \
  -d "username=test@univalle.edu.bo&password=test123"

# Usar el token
TOKEN="tu-access-token-aqui"
curl http://tu-backend.com/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Validar token
curl -X POST http://tu-backend.com/api/v1/auth/validate-token \
  -H "Authorization: Bearer $TOKEN"

# Refresh token
REFRESH="tu-refresh-token-aqui"
curl -X POST http://tu-backend.com/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH\"}"
```

---

## ⚠️ Errores Comunes

### 1. "Token inválido o expirado"
- **Causa**: Access token venció (después de 30 días)
- **Solución**: Usar refresh token para obtener uno nuevo

### 2. "Refresh token inválido o expirado"
- **Causa**: Refresh token venció (después de 90 días)
- **Solución**: Usuario debe hacer login nuevamente

### 3. "Bearer duplicado"
- **Causa**: Enviando `Authorization: Bearer Bearer token`
- **Solución**: Enviar solo `Authorization: Bearer token`

### 4. "Network Error" en React Native
- **Causa**: URL incorrecta o backend no accesible
- **Solución**: 
  - Android: Usar IP de tu máquina, no `localhost`
  - iOS: Asegurar que backend sea HTTPS o configurar ATS

### 5. "Usuario no encontrado"
- **Causa**: Token válido pero usuario fue eliminado
- **Solución**: Cerrar sesión y pedir nuevo login

---

## 🎯 Mejores Prácticas

1. **Siempre usar HTTPS en producción**
2. **Implementar refresh automático** con el interceptor
3. **Guardar tokens en AsyncStorage**, nunca en variables de estado
4. **Manejar errores de red** con timeouts y retry logic
5. **Validar tokens** al iniciar la app
6. **Limpiar storage** al cerrar sesión
7. **NO guardar contraseñas** en el dispositivo
8. **Usar el endpoint `/validate-token`** para debugging

---

## 📝 Changelog

### v2.0 (2025-11-19)
- ✅ Tokens de 30/90 días
- ✅ Mejor manejo de expiración
- ✅ Logging detallado
- ✅ Endpoint de validación de tokens
- ✅ Mensajes de error más descriptivos
- ✅ Compatibilidad React Native mejorada

---

## 🆘 Soporte

Si tienes problemas:
1. Verifica que el backend esté corriendo
2. Usa `/auth/validate-token` para ver el estado del token
3. Revisa los logs del backend (hay logging detallado)
4. Asegúrate de que los tokens se guarden correctamente en AsyncStorage
