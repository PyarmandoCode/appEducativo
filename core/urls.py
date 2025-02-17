from django.urls import path
from .views import lista_estudiantes,generar_todos_carnets,registrar_asistencia,dashboard,login_view,seleccionar_seccion,ver_estudiantes,enviar_mensaje,ir_login,login_apoderado,logout_apoderado,ver_mensajes
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('lista_estudiantes', lista_estudiantes, name='lista_estudiantes'),
    path('carnets/', generar_todos_carnets, name='generar_todos_carnets'),
    path("asistencia/", registrar_asistencia, name="registrar_asistencia"),
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('seleccionar_seccion/', seleccionar_seccion, name='seleccionar_seccion'),
    path('seccion/<int:seccion_id>/', ver_estudiantes, name='ver_estudiantes'),
    path('enviar-mensaje/<int:apoderado_id>/', enviar_mensaje, name='enviar_mensaje'),
    path('ir_login/', ir_login, name='ir_login'),
    path('apoderado/login/', login_apoderado, name='login_apoderado'),
    path('apoderado/logout/', logout_apoderado, name='logout_apoderado'),
    path('apoderado/mensajes/', ver_mensajes, name='ver_mensajes'),
   
]
