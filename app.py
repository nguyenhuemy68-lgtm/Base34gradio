import gradio as gr
import base64
import os

def file_to_base64_and_html(file_obj):
    """
    Chuyển đổi file tải lên thành chuỗi base64 và tạo đoạn mã HTML nhúng.
    """
    if file_obj is None:
        return "Vui lòng tải lên một tệp.", ""

    file_path = file_obj.name # Lấy đường dẫn của tệp tạm thời

    try:
        # 1. Đọc tệp và chuyển đổi sang base64
        with open(file_path, "rb") as f:
            encoded_bytes = base64.b64encode(f.read())
            base64_string = encoded_bytes.decode('utf-8')

        # 2. Xác định loại MIME (cần thiết cho HTML)
        # Gradio không cung cấp MIME type trực tiếp, ta sẽ dựa vào phần mở rộng
        file_ext = os.path.splitext(file_path)[1].lower()
        mime_type = ""

        if file_ext in ('.jpg', '.jpeg'):
            mime_type = "image/jpeg"
            html_tag = "img"
        elif file_ext == '.png':
            mime_type = "image/png"
            html_tag = "img"
        elif file_ext == '.gif':
            mime_type = "image/gif"
            html_tag = "img"
        elif file_ext == '.mp3':
            mime_type = "audio/mp3"
            html_tag = "audio"
        elif file_ext == '.mp4':
            mime_type = "video/mp4"
            html_tag = "video"
        elif file_ext == '.svg':
            mime_type = "image/svg+xml"
            html_tag = "img"
        else:
            # Mặc định là 'application/octet-stream' hoặc loại khác
            mime_type = f"application/{file_ext[1:]}" # Ví dụ: application/pdf
            html_tag = "div" # Không thể nhúng trực tiếp, hiển thị chuỗi base64 thôi

        # 3. Tạo URL Base64 (Data URI)
        data_uri = f"data:{mime_type};base64,{base64_string}"

        # 4. Tạo đoạn mã HTML nhúng
        if html_tag in ("img", "video", "audio"):
            if html_tag == "img":
                 # Thêm style để ảnh không quá lớn
                html_code = (
                    f'<{html_tag} src="{data_uri}" style="max-width:100%; height:auto;" alt="Nhúng Base64">\n'
                    f'</{html_tag}>'
                )
            elif html_tag == "video" or html_tag == "audio":
                # Thêm controls cho video/audio
                html_code = (
                    f'<{html_tag} src="{data_uri}" controls style="max-width:100%; height:auto;">\n'
                    f'  Trình duyệt của bạn không hỗ trợ thẻ {html_tag}.\n'
                    f'</{html_tag}>'
                )
        else:
            # Dành cho các tệp không thể nhúng trực tiếp (PDF, DOCX...)
            html_code = (
                f'\n'
                f'\n'
                f'<a href="{data_uri}" download="file{file_ext}">Tải xuống Tệp (Base64 Data URI)</a>'
            )

        return data_uri, html_code

    except Exception as e:
        return f"Đã xảy ra lỗi: {e}", ""

# Thiết lập giao diện Gradio
with gr.Blocks(title="File sang Base64 và HTML") as demo:
    gr.Markdown("## 🔄 Chuyển đổi Tệp thành Data URI (Base64) và Mã HTML Nhúng")

    with gr.Row():
        file_input = gr.File(label="Tải lên Tệp (Ảnh, Video, Âm thanh,...)")

    with gr.Row():
        base64_output = gr.Textbox(label="Data URI (Chuỗi Base64)", lines=5)
        html_output = gr.Textbox(label="Mã HTML Nhúng", lines=5)

    # Nút thực hiện chuyển đổi
    file_input.change(
        fn=file_to_base64_and_html,
        inputs=file_input,
        outputs=[base64_output, html_output]
    )

    gr.Markdown("### 🔍 Kết quả Xem trước (Không phải là HTML code)")
    html_preview_component = gr.HTML(value="Tải lên tệp để xem trước...", elem_id="html_preview")

    # Cập nhật xem trước khi có chuỗi HTML mới
    def update_preview(html_code):
        # Fix for SyntaxError: unterminated string literal
        # If html_code is not empty and doesn't look like an HTML tag, display it as a code block.
        # Otherwise, display it directly as HTML.
        if html_code and not html_code.strip().startswith("<"):
            return gr.HTML.update(value=f"<pre><code>{html_code}</code></pre>")
        else:
            return gr.HTML.update(value=html_code)

    # Link the html_output to the update_preview function
    html_output.change(
        fn=update_preview,
        inputs=html_output,
        outputs=html_preview_component # Reference the existing HTML component
    )

demo.launch(share=True)
