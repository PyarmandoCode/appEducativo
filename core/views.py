from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from .models import Estudiante,Asistencia,Profesores,Secciones,Apoderados,Mensajes
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse
from reportlab.lib.pagesizes import mm

from reportlab.pdfgen import canvas
from django.conf import settings
import requests
from django.contrib import messages

from io import BytesIO
from reportlab.lib.colors import HexColor
from django.utils.timezone import now
from PIL import Image
from reportlab.lib import colors
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, MensajeForm

def lista_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'lista.html', {'estudiantes': estudiantes})

LOGO_URL = "https://res.cloudinary.com/dream-music/image/upload/v1739577892/nuevologo_g81gus.png"
SELLO_URL = "https://res.cloudinary.com/dream-music/image/upload/v1739577892/nuevologo_g81gus.png"

def obtener_imagen(url):
    """Descarga una imagen desde una URL y la convierte en ImageReader."""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return ImageReader(BytesIO(response.content))
    except Exception:
        return None
    return None

def mejorar_calidad_imagen(imagen_path, output_size=(100, 100)):
    """Redimensiona la imagen sin pérdida de calidad y la devuelve en un formato óptimo."""
    img = Image.open(imagen_path).convert("RGB")
    img = img.resize(output_size, Image.LANCZOS)  # Mantiene la mejor calidad de imagen
    
    temp_buffer = BytesIO()
    img.save(temp_buffer, format="PNG", quality=95)  # Guardamos en calidad alta
    return ImageReader(temp_buffer)

def dibujar_texto_con_borde(pdf, texto, x, y, tamaño=10, color_texto=colors.white, color_borde=colors.black):
    """Dibuja texto con borde grueso para dar un efecto impactante."""
    pdf.setFont("Helvetica-Bold", tamaño)
    
    # Dibuja el borde del texto en negro (sombra)
    pdf.setFillColor(color_borde)
    for dx, dy in [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]:
        pdf.drawCentredString(x + dx, y + dy, texto)
    
    # Dibuja el texto principal en blanco
    pdf.setFillColor(color_texto)
    pdf.drawCentredString(x, y, texto)

def generar_todos_carnets(request):
    estudiantes = Estudiante.objects.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carnets_estudiantes.pdf"'
    pdf = canvas.Canvas(response, pagesize=(53.98 * mm, 85.6 * mm))  # Tamaño ID-1 en vertical

    logo_image = obtener_imagen(LOGO_URL)
    sello_image = obtener_imagen(SELLO_URL)

    for estudiante in estudiantes:
        pdf.setFillColor(HexColor("#D32F2F"))  # Rojo intenso
        pdf.rect(0, 0, 53.98 * mm, 85.6 * mm, fill=True, stroke=False)

        pdf.setFillColor(HexColor("#FFC107"))  # Amarillo vibrante
        pdf.rect(3 * mm, 3 * mm, 47.98 * mm, 79.6 * mm, fill=True, stroke=False)

        if sello_image:
            pdf.setFillAlpha(0.1)
            pdf.drawImage(sello_image, 7 * mm, 35 * mm, width=40 * mm, height=40 * mm, mask='auto')
            pdf.setFillAlpha(1)

        if logo_image:
            pdf.drawImage(logo_image, 38 * mm, 73 * mm, width=9 * mm, height=8 * mm, mask='auto')

        # Dibujar textos con borde para mayor impacto
        dibujar_texto_con_borde(pdf, "Colegio Emblemático", 26.99 * mm, 75 * mm, tamaño=9)
        dibujar_texto_con_borde(pdf, "Ventura Ccalamaqui", 26.99 * mm, 71 * mm, tamaño=11)
        dibujar_texto_con_borde(pdf, estudiante.nombre, 26.99 * mm, 65 * mm, tamaño=9)

        # Línea divisoria
        pdf.setStrokeColor(HexColor("#FFFFFF"))
        pdf.line(5 * mm, 62 * mm, 49 * mm, 62 * mm)

        # Imagen del estudiante mejorada
        if estudiante.foto:
            foto_mejorada = mejorar_calidad_imagen(estudiante.foto.path, output_size=(80, 80))
            pdf.drawImage(foto_mejorada, 12 * mm, 33 * mm, width=28 * mm, height=28 * mm, mask='auto')

        # Código QR
        if estudiante.codigo_qr:
            codigo_path = estudiante.codigo_qr.path
            pdf.drawImage(ImageReader(codigo_path), 16 * mm, 5 * mm, width=22 * mm, height=22 * mm, mask='auto')

        pdf.showPage()

    pdf.save()
    return response


def registrar_asistencia(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo_barras", "").strip()

        try:
            estudiante = Estudiante.objects.get(matricula=codigo)
            Asistencia.objects.create(estudiante=estudiante, fecha_hora=now())

            # URL de la foto del estudiante
            foto_url = estudiante.foto.url if estudiante.foto else "/static/img/default.jpg"

            return JsonResponse({
                "success": True,
                "mensaje": f"Asistencia registrada para {estudiante.nombre}",
                "nombre": estudiante.nombre,
                "foto": foto_url
            })

        except Estudiante.DoesNotExist:
            return JsonResponse({"success": False, "mensaje": "Estudiante no encontrado"})

    return render(request, "asistencia.html")


def dashboard(request):
    return render(request, 'dashboard.html')

def login_view(request):
    if request.method == "POST":
        print("entro aaaaa")
        usuario = request.POST.get('usuario').strip()
        contraseña = request.POST.get('contraseña').strip()
        print(request.POST)
        print(f"capturando el usuario y contraseña {usuario} {contraseña}")

        try:
            profesor = Profesores.objects.get(usuario=usuario, contraseña=contraseña)
            request.session['profesor_id'] = profesor.id  # Guardamos la sesión
            return redirect('seleccionar_seccion')
        except Profesores.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, 'login.html')

#@login_required
def seleccionar_seccion(request):
    if 'profesor_id' not in request.session:
        return redirect('login')

    profesor = Profesores.objects.get(id=request.session['profesor_id'])
    secciones = profesor.secciones.all()
    
    return render(request, 'seleccionar_seccion.html', {"secciones": secciones, "profesor": profesor})

def logout_view(request):
    
    return redirect('ir_login')
    #if request.method in ["POST", "GET"]:
        #logout(request)
        #request.session.flush()  # Borra la sesión manualmente por seguridad
    #    return redirect('login')

#@login_required
def ver_estudiantes(request, seccion_id):
    seccion = get_object_or_404(Secciones, id=seccion_id)  # Obtiene la sección
    estudiantes = Estudiante.objects.filter(seccion_id=seccion_id)
    return render(request, "ver_estudiantes.html", {
        "seccion": seccion,  # Pasamos la sección al template
        "estudiantes": estudiantes
    })

#@login_required
def enviar_mensaje(request, apoderado_id):
    if 'profesor_id' not in request.session:
        return redirect('login')

    profesor = get_object_or_404(Profesores, id=request.session['profesor_id'])
    apoderado = get_object_or_404(Apoderados, id=apoderado_id)

    if request.method == "POST":
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.profesor = profesor
            mensaje.apoderado = apoderado
            mensaje.save()

            messages.success(request, "Mensaje enviado correctamente.")  # ✅ Mensaje de éxito
            return redirect('enviar_mensaje', apoderado_id=apoderado.id)  # Recargar para mostrar la alerta

    else:
        form = MensajeForm()
    
    return render(request, 'enviar_mensaje.html', {
        "form": form,
        "apoderado": apoderado,
        "profesor": profesor  # ✅ Asegurar que el nombre del profesor esté en el contexto
    })

def  ir_login(request):
    request.session.flush()  
    return render(request, 'login.html')



def login_apoderado(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contraseña = request.POST.get("contraseña")

        try:
            apoderado = Apoderados.objects.get(usuario=usuario, contraseña=contraseña)
            request.session['apoderado_id'] = apoderado.id  # Guardamos la sesión
            messages.success(request, f"¡Bienvenido, {apoderado.Apoderado}!")
            return redirect('ver_mensajes')
        except Apoderados.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")
    
    return render(request, 'login_apoderado.html')

def ver_mensajes(request):
    if 'apoderado_id' not in request.session:
        return redirect('login_apoderado')
    
    apoderado = Apoderados.objects.get(id=request.session['apoderado_id'])
    mensajes = Mensajes.objects.filter(apoderado=apoderado).order_by('-fecha')
    
    return render(request, 'ver_mensajes.html', {'mensajes': mensajes, 'apoderado': apoderado})

def logout_apoderado(request):
    request.session.flush()  # Elimina la sesión
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('login_apoderado')
