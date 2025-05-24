import os
from PIL import Image
import cv2
import face_recognition
import numpy as np

carpeta_autorizados = "autorizados"

def convertir_imagenes_rgb():
    print("🔄 Convirtiendo imágenes a formato RGB seguro...")
    for archivo in os.listdir(carpeta_autorizados):
        if archivo.lower().endswith((".jpg", ".jpeg", ".png")) and not archivo.endswith("_ok.jpg"):
            ruta_original = os.path.join(carpeta_autorizados, archivo)
            try:
                imagen = Image.open(ruta_original).convert("RGB")
                nombre_base = os.path.splitext(archivo)[0]
                ruta_guardar = os.path.join(carpeta_autorizados, nombre_base + "_ok.jpg")
                imagen.save(ruta_guardar, "JPEG", quality=95)
                print(f"[✔] Convertida: {ruta_guardar}")
            except Exception as e:
                print(f"[✖] Error al convertir {archivo}: {e}")

def cargar_rostros_autorizados():
    print("\n🔍 Cargando rostros autorizados...")
    codificaciones = []
    nombres = []
    for archivo in os.listdir(carpeta_autorizados):
        if archivo.lower().endswith("_ok.jpg"):
            ruta = os.path.join(carpeta_autorizados, archivo)
            try:
                # Cargar con PIL y convertir a RGB
                imagen_pil = Image.open(ruta).convert("RGB")
                imagen = np.array(imagen_pil)  # Convertir a NumPy array
                codificacion = face_recognition.face_encodings(imagen)
                if codificacion:
                    codificaciones.append(codificacion[0])
                    nombre = os.path.splitext(archivo)[0].replace("_ok", "")
                    nombres.append(nombre)
                    print(f"[✔] Registrado: {nombre}")
                else:
                    print(f"[✖] No se detectó rostro en {archivo}")
            except Exception as e:
                print(f"[✖] Error procesando {archivo}: {e}")
    return codificaciones, nombres

def reconocimiento_en_vivo(codificaciones_autorizadas, nombres_autorizados):
    print("\n🎥 Iniciando cámara para reconocimiento facial en vivo...")
    cap = cv2.VideoCapture(0)
    acceso_permitido = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[!] No se pudo capturar imagen de la cámara")
            break

        frame_pequeño = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_pequeño = cv2.cvtColor(frame_pequeño, cv2.COLOR_BGR2RGB)

        ubicaciones = face_recognition.face_locations(rgb_pequeño)
        codificaciones = face_recognition.face_encodings(rgb_pequeño, ubicaciones)

        for codificacion, ubicacion in zip(codificaciones, ubicaciones):
            coincidencias = face_recognition.compare_faces(codificaciones_autorizadas, codificacion)
            nombre = "Desconocido"

            distancias = face_recognition.face_distance(codificaciones_autorizadas, codificacion)
            if len(distancias) > 0:
                mejor_match = np.argmin(distancias)
                if coincidencias[mejor_match]:
                    nombre = nombres_autorizados[mejor_match]

            y1, x2, y2, x1 = [v * 4 for v in ubicacion]  # volver a escala original
            color = (0, 255, 0) if nombre != "Desconocido" else (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, nombre, (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            if nombre != "Desconocido":
                print(f"[✅] Acceso permitido a: {nombre}")
                acceso_permitido = True
                break  # Ya encontró a alguien autorizado, puede salir del ciclo

        cv2.imshow("Reconocimiento Facial Condominio", frame)

        if acceso_permitido:
            cv2.waitKey(2000)  # Espera 2 segundos para mostrar el cuadro
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saliendo...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    convertir_imagenes_rgb()
    codificaciones_aut, nombres_aut = cargar_rostros_autorizados()
    if len(codificaciones_aut) == 0:
        print("[!] No hay rostros autorizados cargados. Termina el programa.")
    else:
        reconocimiento_en_vivo(codificaciones_aut, nombres_aut)
