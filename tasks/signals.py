from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from datetime import datetime






@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    superuser = User.objects.get(is_superuser=True)
    
    current_date = datetime.now().date()
    # REGISTRO NUEVO 
    if user.date_joined and user.date_joined.date() == current_date:
        subject = "Registro nuevo"
        message = f"Se ha registrado un nuevo usuario:  {user.username} ."
        from_email = "mextlikallimprenta@gmail.com"  # Tu dirección de correo electrónico.
        recipient_list = [superuser.email]
        #recipient_list = ['egio201757@upemor.edu.mx']
        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Correo electrónico de notificación enviado correctamente.")
        except Exception as e:
            print(f"Errorsito al enviar correo: {str(e)}")



    # INICIO DE SESION 
    # Compara la fecha de last_login del usuario con la fecha actual
    if user.last_login and user.last_login.date() == current_date:
        
        subject = "Inicio de sesión de usuario"
        message = f"El usuario {user.username} ha iniciado sesión en la aplicación."
        from_email = "mextlikallimprenta@gmail.com"  # Tu dirección de correo electrónico.
        recipient_list = [superuser.email]

        

        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Correo electrónico de notificación enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
    