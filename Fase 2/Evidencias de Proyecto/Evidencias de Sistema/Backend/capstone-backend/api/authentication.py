# api/authentication.py
import jwt
import os
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User
from django.conf import settings

class SupabaseJWTAuthentication(BaseAuthentication):
    """
    Clase de autenticación de Django REST Framework para validar
    tokens JWT emitidos por Supabase.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None  # No se intentó autenticar

        try:
            # El header debe ser "Bearer <token>"
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                raise exceptions.AuthenticationFailed('Formato de token inválido. Debe ser "Bearer <token>".')
        except ValueError:
            raise exceptions.AuthenticationFailed('Formato de token inválido. Debe ser "Bearer <token>".')
        except TypeError:
            raise exceptions.AuthenticationFailed('No se proporcionó token de autorización.')

        try:
            # 1. Decodificar el JWT usando el secreto de Supabase
            SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
            if not SUPABASE_JWT_SECRET:
                raise exceptions.APIException('SUPABASE_JWT_SECRET no está configurado en .env')

            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                # 'aud' (audiencia) debe ser 'authenticated'
                options={"verify_aud": True, "require": ["aud", "exp", "sub"]},
                audience="authenticated",
                leeway=15,  # toleramos hasta 15s de desfase entre relojes
            )

            # 2. Obtener datos del usuario desde el token
            supabase_user_id = payload.get('sub') # El ID de Supabase Auth
            user_email = payload.get('email')

            if not supabase_user_id or not user_email:
                raise exceptions.AuthenticationFailed('Token inválido: faltan "sub" o "email".')

            # 3. Encontrar o crear un "usuario espejo" en Django
            # DRF necesita un request.user local (en la tabla auth_user de Django)
            # para que los permisos (IsAuthenticated) funcionen.
            # Usamos el ID de Supabase (sub) como 'username' local.
            user, created = User.objects.get_or_create(
                username=supabase_user_id,
                # --- ✅ MODIFICACIÓN 1: Añadir 'is_active: True' ---
                defaults={'email': user_email, 'is_staff': False, 'is_active': True}
            )
            
            if created:
                # Si es nuevo, no tiene contraseña local válida
                user.set_unusable_password()
                user.save()
            # --- ✅ MODIFICACIÓN 2: Reactivar si estaba inactivo ---
            elif not user.is_active:
                # Esto arreglará tus usuarios antiguos que quedaron inactivos
                user.is_active = True
                user.save()
            # --- FIN DE LA MODIFICACIÓN ---

            return (user, token) # ¡Autenticación exitosa!

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado.')
        except jwt.InvalidAudienceError:
            raise exceptions.AuthenticationFailed('Audiencia de token inválida.')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f'Token JWT inválido: {e}')
        except Exception as e:
            raise exceptions.APIException(f'Error de autenticación: {e}')
