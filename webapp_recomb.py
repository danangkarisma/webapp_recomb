import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import os

st.set_page_config(page_title="PDF Resi 4-in-1 Generator", layout="centered")

st.title("📦 PDF Resi 4-in-1 Grid Generator")
st.write("Upload beberapa PDF resi tunggal, dan website ini akan menggabungkannya menjadi layout 2x2 siap cetak!")

# 1. Komponen Upload File (Bisa multi-file sekaligus)
uploaded_files = st.file_uploader(
    "Pilih atau Tarik File PDF Resi", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Berhasil mengunggah {len(uploaded_files)} file resi.")
    
    # Tombol untuk mulai memproses
    if st.button("Proses & Buat Grid PDF", type="primary"):
        with st.spinner("Sedang memproses resi... Mohon tunggu."):
            try:
                all_pages_images = []
                
                # 2. Konversi setiap PDF yang diupload menjadi gambar di memori (Tanpa Poppler)
                for uploaded_file in uploaded_files:
                    # Membaca file dari buffer memory Streamlit
                    file_bytes = uploaded_file.read()
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    
                    for page in doc:
                        zoom = 150 / 72
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat)
                        
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        all_pages_images.append(img)
                    doc.close()

                if not all_pages_images:
                    st.warning("Tidak ada halaman resi yang ditemukan di dalam file PDF.")
                else:
                    # Dimensi kanvas A4 (Skala 150 DPI agar ukuran file kecil & ringan)
                    a4_width = 1240
                    a4_height = 1754
                    
                    # Ukuran target per resi (2x2 grid)
                    target_width = 570
                    target_height = 800
                    
                    # Koordinat posisi simetris di tengah
                    positions = [
                        (33, 51),       # Kiri atas
                        (637, 51),      # Kanan atas
                        (33, 903),      # Kiri bawah
                        (637, 903)      # Kanan bawah
                    ]
                    
                    output_doc = fitz.open()
                    
                    # 3. Pengelompokan 4 resi per halaman
                    for i in range(0, len(all_pages_images), 4):
                        chunk = all_pages_images[i:i+4]
                        page_canvas = Image.new("RGB", (a4_width, a4_height), color="white")
                        
                        for index, img in enumerate(chunk):
                            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                            pos = positions[index]
                            page_canvas.paste(resized_img, pos)
                        
                        # Kompresi ke JPEG bytes (Hemat ukuran file, bebas error)
                        img_byte_arr = io.BytesIO()
                        page_canvas.save(img_byte_arr, format='JPEG', quality=80)
                        img_bytes = img_byte_arr.getvalue()
                        
                        # Masukkan ke halaman PDF baru lewat PyMuPDF
                        new_page = output_doc.new_page(width=595, height=842)
                        rect = fitz.Rect(0, 0, 595, 842)
                        new_page.insert_image(rect, stream=img_bytes)
                    
                    # 4. Menyimpan hasil PDF ke dalam memory buffer untuk diunduh user
                    pdf_buffer = io.BytesIO()
                    output_doc.save(pdf_buffer, garbage=4, deflate=True)
                    output_doc.close()
                    pdf_data = pdf_buffer.getvalue()
                    
                    st.balloons() # Efek animasi sukses
                    st.success("🎉 PDF Grid 4-in-1 Berhasil Dibuat!")
                    
                    # 5. Tombol Download Otomatis untuk User (Bisa di klik dari HP Android/iPhone)
                    st.download_button(
                        label="⬇️ Download Hasil PDF",
                        data=pdf_data,
                        file_name="hasil_resi_4in1.pdf",
                        mime="application/pdf"
                    )
                    
            except Exception as e:
                st.error(f"Gagal memproses dokumen. Error: {str(e)}")