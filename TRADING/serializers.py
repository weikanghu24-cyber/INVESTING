from rest_framework import serializers
from django.contrib.auth import get_user_model

# Obtenemos tu modelo de usuario personalizado
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Los campos que pediremos al usuario para registrarse
        fields = ('email', 'username', 'password')
        
        # Le decimos a Django que la contraseña es "write_only" (solo escritura).
        # Así, cuando devolvamos los datos del usuario, la contraseña NUNCA viajará de vuelta.
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # ¡OJO AQUÍ! Usamos create_user() en lugar de simplemente guardar.
        # Esto es vital para que Django encripte (hashee) la contraseña.
        # Si no lo haces así, la contraseña se guardaría en texto plano y el login fallaría.
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Aquí ponemos SOLO los campos que el usuario tiene permitido ver de su propio perfil
        fields = ('id', 'email', 'username', 'avatar', 'created_at')